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

    # Chat LLM settings
    CHAT_LLM_BASE_URL: str = os.getenv("CHAT_LLM_BASE_URL", "http://127.0.0.1:8000/v1")
    CHAT_LLM_API_KEY: str = os.getenv("CHAT_LLM_API_KEY", "aaa")
    CHAT_LLM_MODEL: str = os.getenv("CHAT_LLM_MODEL", "model")

    class Config:
        case_sensitive = True


class ChatLLMSettings(AgentSettings):
    # Only add the settings that are unique to ChatLLMSettings
    temperature: float = 0.1
    top_p: float = 0.6
    max_tokens: int = 32768


# Instantiate settings to be imported in other modules
agent_settings = AgentSettings()
chat_llm_settings = ChatLLMSettings()
