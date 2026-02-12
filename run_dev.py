import uvicorn
from dotenv import load_dotenv

if __name__ == "__main__":
    # 자동으로 환경변수 로드 후 API 실행
    load_dotenv(".env")  

    uvicorn.run(
        "api.main:app",
        # host="0.0.0.0",
        port=8000,
        reload=True  # 개발 중 코드 변경 시 자동 재시작
    )