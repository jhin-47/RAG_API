# ADaM RAG API

> ADaM의 챗봇에 사용할 채용공고 기반 RAG API


## 개요

#### 주요 기능

- API를 통해 받은 쿼리에 대해 관련되 채용공고 정보를 반환한다
- SQLiteVec에 정보를 사전에 임베딩하여 저장한다
- 

#### 기술 스택

- 


#### 폴더구조

- api/: ADaM RAG API의 소스코드 디렉토리
    - module/: 임베딩, 벡터DB 등의 기능을 구현한 모듈의 위치
    - main.py: fastapi 
- database/: SQLite 데이터베이스 파일이 위치하는 디렉토리 (자동으로 해당 디렉토리의 파일 중 내림차순 정렬하여 1개를 받아옴)
- jupter/
    - Generate_RAG_DB.ipynb: RAG API를 위한 database파일을 만드는 주피터 파일 (예제)
- tests/: api, module의 테스트 파일이 위치한 디렉토리
- .env: 환경변수 설정값 목록
- .example.env: 환경변수 예제
- load_env.py: 설정값 로드


#### 패키지 목록

```
pandas
dotenv
sqlite-vec
langchain-google-genai
langchain-openai
fastapi
uvicorn
```

`pip install pandas dotenv sqlite-vec langchain-google-genai langchain-openai fastapi uvicorn`



## 버전관리 관련

#### 개요
- Git + Github 조합으로 버전관리를 수행한다
- 최신 소스코드는 main에서 관리되고, 배포
- 각 작업자별로 분리된 개별 브렌치에서 작업한다

#### 브랜치 전략
- (추가 예정, 작업자별 브랜치를 사용하는 형식)


## 도커 빌드 및 테스트 커맨드
```bash

```
