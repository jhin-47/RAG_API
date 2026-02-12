import time
import json
import os
from pathlib import Path
from typing import Optional, Callable, List, Dict, Any, Union

import sqlite3
import sqlite_vec
import pandas as pd




class SQLiteVecDB:
    """임베딩 벡터를 SQLite 데이터베이스에 저장하고 검색하는 클래스

    sqlite-vec 확장을 활용하여 벡터 유사도 검색을 지원하는 벡터 데이터베이스를 구현
    텍스트 쿼리와 내용을 임베딩 벡터와 함께 저장하고, 유사도 기반 검색 기능을 제공
    
    Attributes:
        db_filepath (str): SQLite 데이터베이스 파일 경로
        embed (Callable[[str], List[float]]): 텍스트를 벡터로 변환하는 임베딩 함수
        embedding_size (int): 임베딩 벡터의 차원 크기
    """
    
    def __init__(self, db_filepath: str, embedding_size: Optional[int] = None, 
                 embedding_function: Optional[Callable[[str], List[float]]] = None, 
                 init_db: bool = False) -> None:
        """SQLiteVecDB 클래스의 인스턴스를 초기화함
        
        Args:
            db_filepath (str): SQLite 데이터베이스 파일 경로임
            embedding_size (Optional[int], optional): 임베딩 벡터의 차원 크기임. 제공되지 않으면 자동 계산함
            embedding_function (Optional[Callable[[str], List[float]]], optional): 텍스트를 벡터로 변환하는 함수
            init_db (bool, optional): True이면 데이터베이스를 초기화함. 기본값은 False
        """
        self.db_filepath = db_filepath
        self.embed = embedding_function  # 실행 시 한 문장을 임베딩하는 함수

        # 임베딩 사이즈가 주어지지 않았을 경우, 임베딩 함수를 통해 임베딩 사이즈를 추출
        if embedding_size is None:
            embedding = self.embed("test")
            self.embedding_size = len(embedding)
        else:
            self.embedding_size = embedding_size
        
        # 완전 초기화
        if init_db:
            self.initialize_table(remove_old_table=True)
        
    def connect_sqlitevec(self) -> sqlite3.Connection:
        """sqlite-vec 확장을 로드한 SQLite 연결을 생성함
        
        Returns:
            sqlite3.Connection: sqlite-vec 확장이 활성화된 데이터베이스 연결 객체
        """
        db = sqlite3.connect(self.db_filepath)
        db.enable_load_extension(True)
        sqlite_vec.load(db)
        db.enable_load_extension(False)
        return db
    

    def initialize_table(self, remove_old_table: bool = False) -> None:
        """벡터 저장을 위한 테이블을 초기화함
        
        임베딩 벡터, 쿼리, 콘텐츠, 타임스탬프를 저장하는 가상 테이블을 생성함
        
        Args:
            remove_old_table (bool, optional): True이면 기존 테이블을 삭제함. 기본값은 False임
        """
        db = self.connect_sqlitevec()
        # 기존 테이블 삭제 (존재할 경우)
        if remove_old_table:
            db.execute("DROP TABLE IF EXISTS vectors")
        # 테이블이 없을 경우 생성
        db.execute(f'''
        CREATE VIRTUAL TABLE IF NOT EXISTS vectors USING vec0(
           embedding float[{self.embedding_size}],
           +query TEXT,
           +content TEXT,
           timestamp FLOAT
        )''')
        db.commit()
        db.close()
    
    
    def add_one(self, query: str, content: str) -> None:
        """단일 쿼리-콘텐츠 쌍을 데이터베이스에 추가함
        
        쿼리 텍스트를 임베딩하고 관련 콘텐츠와 함께 데이터베이스에 저장함
        
        Args:
            query (str): 임베딩할 쿼리 텍스트
            content (str): 쿼리와 연관된 콘텐츠 텍스트
        """
        db = self.connect_sqlitevec()
        embedding = self.embed(query)
        embedding = embedding[:self.embedding_size]
        timestamp = time.time()
        db.execute('INSERT INTO vectors (embedding, query, content, timestamp) VALUES (?, ?, ?, ?)',
                   (sqlite_vec.serialize_float32(embedding), query, content, timestamp))
        db.commit()
        db.close()
    
    
    def get_all(self) -> pd.DataFrame:
        """데이터베이스에 저장된 모든 벡터 데이터를 반환함
        
        Returns:
            pd.DataFrame: 임베딩, 쿼리, 콘텐츠, 타임스탬프를 포함하는 데이터프레임
        """
        db = self.connect_sqlitevec()
        query = "SELECT vec_to_json(embedding), query, content, timestamp FROM vectors ORDER BY timestamp ASC;"
        results = db.execute(query).fetchall()
        rows = []
        for embed_str, query, content, timestamp in results:
            embedding = json.loads(embed_str)
            row = {}
            row["embedding"] = embedding
            row["query"] = query
            row["content"] = content
            row["timestamp"] = timestamp
            rows.append(row)
            
        df = pd.DataFrame(rows)
        db.close()
        return df
    
    
    def search(self, query: str, k: int = 3) -> pd.DataFrame:
        """쿼리와 유사한 상위 k개의 항목을 검색함
        
        Args:
            query (str): 검색할 쿼리 텍스트임
            k (int, optional): 반환할 최대 항목 수임. 기본값은 3임
            
        Returns:
            pd.DataFrame: 검색 결과를 포함하는 데이터프레임 (컬럼: [order(index), query, content, distance])

        """
        db = self.connect_sqlitevec()
        
        embedding = self.embed(query)
        embedding = embedding[:self.embedding_size]
        
        results = db.execute(
                  """SELECT query, content, distance FROM vectors WHERE embedding MATCH ? AND k = ? ORDER BY distance ASC""",
                   [sqlite_vec.serialize_float32(embedding), k]
        ).fetchall()
        db.close()
        
        cols = ["query", "content", "distance"]
        df = pd.DataFrame(results, columns=cols)
        df.index += 1
        df.index.name = "order"
        return df



# def get_sqlite_db_path(db_file_name: Optional[str] = None) -> str:
#     """SQLite 데이터베이스 파일 경로를 반환함
    
#     현재 파일 위치에서 상위 디렉토리로 이동하여 환경변수에 지정된 
#     데이터베이스 디렉토리에서 DB 파일을 찾음.
#     db_file_name이 None이나 'default'인 경우 가장 최신 파일을 반환하고,
#     그 외의 경우 지정된 파일명과 일치하는 파일의 경로를 반환함
    
#     Args:
#         db_file_name (Optional[str], optional): 찾을 데이터베이스 파일명. 기본값은 None임
            
#     Returns:
#         str: SQLite 데이터베이스 파일의 절대 경로
#     """
#     # 현재 파일 위치에서 프로젝트 루트 디렉토리 찾기
#     current_dir = Path(__file__).resolve().parent  # /module
#     project_root = current_dir.parent.parent  # /ADaM_RAG_API
    
#     # 환경변수에서 DB 디렉토리 경로 가져오기
#     db_dir = os.getenv("RAG_DB_DIR", "database")
#     db_path = os.path.join(project_root, db_dir)
#     print(f"DB directory: {db_path}")
    
#     # DB 디렉토리 존재 확인
#     if not os.path.exists(db_path):
#         raise FileNotFoundError(f"Database directory not found: {db_path}")
    
#     # DB 파일 목록 가져오기 (.sqlite 확장자만)
#     db_files = list(Path(db_path).glob("*.sqlite"))
#     if not db_files:
#         raise FileNotFoundError(f"No database files found in: {db_path}")
    
#     # 파일명이 None이거나 'default'인 경우 최신 파일 반환
#     if db_file_name is None or db_file_name.lower() == "default":
#         latest_file = max(db_files, key=lambda x: x.stat().st_mtime)
#         return str(latest_file.resolve())  # 절대 경로로 반환
    
#     # 지정된 파일명 찾기
#     target_file = db_path / db_file_name
#     target_file = os.path.join(db_path, db_file_name)
#     if not os.path.exists(target_file):
#         raise ValueError(f"Database file not found: {target_file}")
    
#     return target_file  # 절대 경로로 반환


def get_sqlite_db_path(db_file_name: Optional[str] = None) -> str:
    """SQLite 데이터베이스 파일 경로를 반환함
    
    디렉토리를 여러 가능한 위치에서 검색하여 데이터베이스 파일을 찾음
    
    Args:
        db_file_name (Optional[str], optional): 찾을 데이터베이스 파일명. 기본값은 None임
            
    Returns:
        str: SQLite 데이터베이스 파일의 절대 경로
    """
    rag_db_dir = str(os.environ["RAG_DB_DIR"])

    # 현재 모듈 기준 경로
    module_dir = Path(__file__).resolve().parent  # /api/module
    project_root = module_dir.parent.parent  # /project_root
    db_path = project_root / rag_db_dir
    
    # DB 파일 목록 가져오기 (.sqlite 확장자만)
    db_files = list(db_path.glob("*.sqlite"))
    if not db_files:
        raise FileNotFoundError(f"No database files found in: {db_path}")
    
    # 파일명이 None이거나 'default'인 경우 최신 파일 반환
    if db_file_name is None or db_file_name.lower() == "default":
        latest_file = max(db_files, key=lambda x: x.stat().st_mtime)
        return str(latest_file.resolve())
    
    # 지정된 파일명 찾기
    target_file = db_path / db_file_name
    if not target_file.exists():
        raise ValueError(f"Database file not found: {target_file}")
    
    return str(target_file.resolve())