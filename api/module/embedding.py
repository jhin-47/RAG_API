from typing import Literal, List, Union, Any, Optional

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings


class Embedding:
    """OpenAI 또는 Google의 임베딩 모델을 사용하여 텍스트를 벡터로 변환하는 클래스임
    
    이 클래스는 OpenAI 또는 Google의 임베딩 API를 사용하여 텍스트 쿼리를 
    벡터 표현으로 변환함. LangChain 라이브러리와 통합됨
    
    Attributes:
        api_key (str): 임베딩 API에 접근하기 위한 API 키임
        source (str): 사용할 임베딩 제공자('openai' 또는 'google')임
        model (str): 사용할 임베딩 모델명임
    """
    
    def __init__(self, api_key: str, source: Literal["openai", "google"] = "openai", model: Optional[str] = None) -> None:
        """Embedding 클래스의 인스턴스를 초기화함
        
        Args:
            api_key (str): API 제공자의 인증 키임
            source (Literal["openai", "google"], optional): 임베딩 제공자('openai' 또는 'google')임. 기본값은 'openai'임
            model (Optional[str], optional): 사용할 특정 모델명임. None인 경우 소스별 기본 모델이 선택됨
        """
        self.api_key = api_key
        self.source = source.lower()  # openai, google
        
        if model is None:
            if source == "openai":
                self.model = "text-embedding-3-small"
            elif source == "google":
                self.model = "models/text-embedding-004"
            else:
                print("> invalid source")
        else:
            self.model = model
    
    
    def get_langchain_embeddings(self) -> Union[OpenAIEmbeddings, GoogleGenerativeAIEmbeddings]:
        """LangChain 임베딩 객체를 생성하여 반환함
        
        Returns:
            Union[OpenAIEmbeddings, GoogleGenerativeAIEmbeddings]: 설정된 제공자 및 모델에 해당하는 LangChain 임베딩 객체임
            
        Raises:
            ValueError: 유효하지 않은 소스가 지정된 경우 발생함
        """
        if self.source == "openai":
            embeddings = OpenAIEmbeddings(api_key=self.api_key, model=self.model)
        elif self.source == "google":
            embeddings = GoogleGenerativeAIEmbeddings(google_api_key=self.api_key, model=self.model)
        else:
            raise ValueError("invalid LLM API source")
        return embeddings
    
    
    def embed(self, query: str) -> List[float]:
        """텍스트 쿼리를 임베딩 벡터로 변환함
        
        Args:
            query (str): 임베딩할 텍스트 문자열임
            
        Returns:
            List[float]: 임베딩 벡터임
        """
        embeddings = self.get_langchain_embeddings()
        vector = embeddings.embed_query(query)
        return vector

