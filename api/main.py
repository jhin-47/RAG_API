# import
import datetime
from typing import List, Optional
import os

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field

# 커스텀 모듈
from .module.embedding import Embedding
from .module.sqlitevec import SQLiteVecDB, get_sqlite_db_path


################################
##### FastAPI 클래스 초기화 #####

# FastAPI 앱 생성
app = FastAPI(
    title="ADaM RAG API",
    description="ADaM 챗봇을 위한 RAG(Retrieval Augmented Generation) API",
    version="0.0.1"
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


######################################
##### API 서버 시작 시 초기화 작업 #####

START_TIME = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
SERVER_TIMEZONE = str(datetime.datetime.now().astimezone().tzinfo)

# 벡터 DB 클래스 변수
VECTOR_DB = None
DB_NAME = None

@app.on_event("startup")
async def startup_event():
    """앱 시작 시 벡터 데이터베이스를 초기화함"""
    global VECTOR_DB
    global DB_NAME
    
    try:
        # API 키 가져옴
        api_key = os.getenv("LLM_API_KEY")
        if not api_key:
            raise ValueError("환경변수에서 LLM_API_KEY를 찾을 수 없음")
        
        # 임베딩 모델 초기화함
        embedding_source = os.getenv("EMBEDDING_SOURCE", "google")
        embedding_model = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")
        embedding = Embedding(api_key=api_key, source=embedding_source, model=embedding_model)
        
        # SQLite 데이터베이스 경로 가져옴
        db_name = os.getenv("RAG_DB_FILENAME", "default")
        db_path = get_sqlite_db_path(db_name)
        
        # SQLite 벡터 데이터베이스 초기화함
        VECTOR_DB = SQLiteVecDB(
            db_filepath=db_path,
            embedding_function=embedding.embed
        )
        DB_NAME = db_name
        print(f"벡터 데이터베이스 로드 완료: {db_path}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"벡터 데이터베이스 초기화 실패: {str(e)}")



##################################
##### API 요청/응답 모델 정의 #####

class SearchRequest(BaseModel):
    query: str = Field(..., description="검색 쿼리 텍스트")
    k: int = Field(3, ge=1, le=10, description="반환할 결과 개수")

class SearchResult(BaseModel):
    content: str
    distance: float

class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str
    count: int



##############################
##### API 엔드포인트 정의 #####

@app.post("/v1/search/", response_model=SearchResponse)
async def search(request: SearchRequest):
    """RAG API 검색 엔드포인트"""
    global VECTOR_DB
    
    if VECTOR_DB is None:
        raise HTTPException(status_code=500, detail="벡터 데이터베이스가 초기화되지 않음")
    
    try:
        # 데이터베이스 검색함
        results_df = VECTOR_DB.search(request.query, k=request.k)
        
        # 결과를 응답 형식으로 변환함
        results = [
            SearchResult(
                content=row["content"],
                distance=float(row["distance"])
            )
            for _, row in results_df.iterrows()
        ]
        
        # 응답 생성함
        return SearchResponse(
            results=results,
            query=request.query,
            count=len(results)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 중 오류 발생: {str(e)}")


@app.get("/v1/search/", response_model=SearchResponse)
async def search_get(
        query: str = Query(..., description="검색 쿼리 텍스트"),
        k: int = Query(3, ge=1, le=10, description="반환할 결과 개수")
    ):
    """GET 메서드 검색 엔드포인트 (POST와 동일한 기능 제공)"""
    request = SearchRequest(query=query, k=k)
    return await search(request)



@app.get("/v1/health/")
async def health():
    """헬스 체크 엔드포인트"""
    return {"status": "ok", "message": "ADaM RAG API가 실행 중", "start": START_TIME, "timezone": SERVER_TIMEZONE, "db_file": DB_NAME}


# @app.get("/")
# async def root():
#     """루트 엔드포인트"""
#     # NOTE: 현재 버전에서는 health로 리다이렉트함
#     return RedirectResponse(status_code=301, url="/v1/health/")
#     # return JSONResponse(status_code=301, content={"message": "Redirecting to /v1/health/"}, headers={"Location": "/v1/health/"})




# 개인정보 처리방침 엔드포인트
class PrivacyPolicy(BaseModel):
    privacy_policy: str
    data_usage_policy: str
    last_updated: str


@app.get("/v1/privacy-policy/", response_model=PrivacyPolicy)
async def privacy_policy():
    """개인정보 처리방침 조회 엔드포인트"""
    return PrivacyPolicy(
        privacy_policy="""
ADaM RAG API 개인정보 처리방침

1. 수집하는 개인정보
   - 본 API는 사용자가 제공하는 검색 쿼리만을 처리하며, 별도의 개인식별정보를 수집하지 않습니다.

2. 개인정보의 이용 목적
   - 수집된 검색 쿼리는 사용자가 요청한 채용정보 검색 서비스 제공 목적으로만 사용됩니다.

3. 제3자 제공
   - 본 API는 사용자 정보를 제3자에게 제공하지 않습니다.
        """,
        data_usage_policy="""
ADaM RAG API 데이터 이용 정책

1. 제공된 채용정보는 참고용으로만 사용되어야 합니다.
2. 채용정보의 정확성은 원본 채용공고를 통해 확인해야 합니다.
3. 본 API를 통해 제공된 정보를 상업적 목적으로 무단 재배포하는 것은 금지됩니다.
4. API 서비스의 안정적 운영을 위해 과도한 요청은 제한될 수 있습니다.
5. 본 API를 통해 얻은 정보는 사용자의 책임 하에 활용되어야 합니다.
        """,
        last_updated="2025-03-31"
    )