import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()  # Ensure environment variables are loaded if you're using a .env file


class AgentSettings(BaseSettings):
    PROJECT_NAME: str = "NF Planing Agent"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1/"

    # Tavily
    TAVILY_TOKEN: str = os.environ.get("TAVILY_TOKEN")

    # MongoDB
    MONGODB_URI: str = os.environ.get("MONGODB_URI")
    MONGODB_DB_NAME: str = os.environ.get("MONGODB_DB_NAME")
    MONGODB_COLL_NAME: str = os.environ.get("MONGODB_COLL_NAME")

    # Milvus
    MILVUS_URI: str = os.environ.get("MILVUS_URI")
    MILVUS_DB_NAME: str = os.environ.get("MILVUS_DB_NAME")
    MILVUS_COLL_NAME: str = os.environ.get("MILVUS_COLL_NAME")

    # BM25
    BM25_PERSIST: str = os.environ.get("BM25_PERSIST")
    BM25_CHUNK_SIZE: int = os.environ.get("BM25_CHUNK_SIZE")
    BM25_CHUNK_OVERLAP: int = os.environ.get("BM25_CHUNK_OVERLAP")

    # Chat LLM settings
    CHAT_LLM_BASE_URL: str = os.getenv("CHAT_LLM_BASE_URL", "http://127.0.0.1:8000/v1")
    CHAT_LLM_API_KEY: str = os.getenv("CHAT_LLM_API_KEY", "aaa")
    CHAT_LLM_MODEL: str = os.getenv("CHAT_LLM_MODEL", "model")

    # Embedding model settings
    EMBEDDING_MODEL_BASE_URL: str = os.getenv("EMBEDDING_MODEL_BASE_URL", "http://127.0.0.1:8000/v1")
    EMBEDDING_MODEL_API_KEY: str = os.getenv("EMBEDDING_MODEL_API_KEY", "aaa")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "model")

    class Config:
        case_sensitive = True


class ChatLLMSettings(AgentSettings):
    # Only add the settings that are unique to ChatLLMSettings
    temperature: float = 0.1
    top_p: float = 0.6
    max_tokens: int = 32768


class EmbeddingModelSettings(AgentSettings):
    # Only add the settings that are unique to ChatLLMSettings
    embedding_dim: int = 1024


class MilvusSettings(AgentSettings):
    embedding_field: str = "doc_embedding"
    similarity_metric: str = "L2"
    index_config: dict = {"index_type": "GPU_CAGRA",
                          "intermediate_graph_degree": 64,
                          "graph_degree": 32
                          }
    similarity_top_k: int = 5


# Instantiate settings to be imported in other modules
agent_settings = AgentSettings()
chat_llm_settings = ChatLLMSettings()
embedding_model_settings = EmbeddingModelSettings()
milvus_settings = MilvusSettings()
