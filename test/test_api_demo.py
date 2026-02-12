import requests
import os
import sys
import unittest
from typing import Dict, Any
import json
from pathlib import Path

# 프로젝트 루트 디렉토리를 모듈 검색 경로에 추가함
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestRAGAPI(unittest.TestCase):
    """ADaM RAG API의 엔드포인트 테스트 클래스"""
    
    # BASE_URL = "http://localhost:8000"
    
    def setUp(self, base_url = "http://localhost:8000"):
        """테스트 전 설정을 수행함"""
        self.BASE_URL = base_url

        # API가 실행 중인지 확인함
        try:
            response = requests.get(f"{self.BASE_URL}/")
            self.api_running = response.status_code == 200
        except requests.ConnectionError:
            self.api_running = False
            print("\n⚠️ API 서버가 실행 중이지 않음. 'python run_dev.py'로 서버를 먼저 실행해야 함")
    
    def test_health_endpoint(self):
        """헬스 체크 엔드포인트 테스트함"""
        if not self.api_running:
            self.skipTest("API 서버가 실행 중이지 않음")
        
        response = requests.get(f"{self.BASE_URL}/")
        
        # 응답 코드 확인함
        self.assertEqual(response.status_code, 200)
        
        # 응답 내용 확인함
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("ADaM RAG API", data["message"])
        
        print("✅ 헬스 체크 엔드포인트 테스트 성공")
    
    def test_search_post_endpoint(self):
        """POST 검색 엔드포인트 테스트함"""
        if not self.api_running:
            self.skipTest("API 서버가 실행 중이지 않음")
        
        # POST 요청 데이터 준비함
        payload = {
            "query": "백엔드 개발자 채용",
            "k": 2
        }
        
        # POST 요청 전송함
        response = requests.post(
            f"{self.BASE_URL}/v1/search/",
            json=payload
        )
        
        # 응답 코드 확인함
        self.assertEqual(response.status_code, 200)
        
        # 응답 구조 확인함
        data = response.json()
        self.assertIn("results", data)
        self.assertIn("query", data)
        self.assertIn("count", data)
        
        # 요청한 개수만큼 결과가 반환되는지 확인함
        self.assertEqual(len(data["results"]), payload["k"])
        self.assertEqual(data["count"], payload["k"])
        
        # 쿼리가 정확히 반환되는지 확인함
        self.assertEqual(data["query"], payload["query"])
        
        # 각 결과의 구조 확인함
        for result in data["results"]:
            self.assertIn("content", result)
            self.assertIn("distance", result)
        
        print(f"✅ POST 검색 엔드포인트 테스트 성공 - {payload['k']}개 결과 반환됨")
    
    def test_search_get_endpoint(self):
        """GET 검색 엔드포인트 테스트함"""
        if not self.api_running:
            self.skipTest("API 서버가 실행 중이지 않음")
        
        # GET 요청 매개변수 준비함
        params = {
            "query": "프론트엔드 개발자 채용",
            "k": 3
        }
        
        # GET 요청 전송함
        response = requests.get(
            f"{self.BASE_URL}/v1/search/",
            params=params
        )
        
        # 응답 코드 확인함
        self.assertEqual(response.status_code, 200)
        
        # 응답 구조 확인함
        data = response.json()
        self.assertIn("results", data)
        self.assertIn("query", data)
        self.assertIn("count", data)
        
        # 요청한 개수만큼 결과가 반환되는지 확인함
        self.assertEqual(len(data["results"]), params["k"])
        self.assertEqual(data["count"], params["k"])
        
        # 쿼리가 정확히 반환되는지 확인함
        self.assertEqual(data["query"], params["query"])
        
        print(f"✅ GET 검색 엔드포인트 테스트 성공 - {params['k']}개 결과 반환됨")
    
    def test_error_handling(self):
        """오류 처리 테스트함"""
        if not self.api_running:
            self.skipTest("API 서버가 실행 중이지 않음")
        
        # 잘못된 요청 데이터 준비함 (k 값이 범위를 벗어남)
        params = {
            "query": "데이터 사이언티스트",
            "k": 20  # 10보다 큰 값은 오류를 발생시켜야 함
        }
        
        # GET 요청 전송함
        response = requests.get(
            f"{self.BASE_URL}/v1/search/",
            params=params
        )
        
        # 응답 코드가 오류(4XX)여야 함
        self.assertEqual(response.status_code, 422)
        
        print("✅ 오류 처리 테스트 성공")
    
    def print_search_results(self, query: str, k: int = 3) -> Dict[str, Any]:
        """검색 결과를 출력하는 헬퍼 메소드임"""
        if not self.api_running:
            print("❌ API 서버가 실행 중이지 않음")
            return {}
        
        params = {"query": query, "k": k}
        response = requests.get(f"{self.BASE_URL}/v1/search/", params=params)
        
        if response.status_code != 200:
            print(f"❌ API 요청 실패: {response.status_code}")
            return {}
        
        data = response.json()
        
        print("\n==== 검색 결과 ====")
        print(f"📝 쿼리: {data['query']}")
        print(f"🔢 결과 수: {data['count']}")
        
        for i, result in enumerate(data['results'], 1):
            print(f"\n📌 결과 {i}:")
            print(f"📄 내용: {result['content'][:100]}..." if len(result['content']) > 100 else result['content'])
            print(f"🔍 유사도: {result['similarity']:.4f}")
        
        return data

if __name__ == "__main__":
    # 테스트 케이스 실행함
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestRAGAPI)
    unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    # 테스트 후 직접 검색 결과 확인함
    test = TestRAGAPI()
    test.setUp()
    if test.api_running:
        print("\n===== 실제 검색 결과 샘플 =====")
        test.print_search_results("백엔드 개발자 채용 정보", k=2)
        test.print_search_results("인공지능 ML 엔지니어", k=2)