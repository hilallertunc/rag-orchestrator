from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "RAG Orchestrator"
    app_version: str = "0.1.0"
    debug: bool = True
    groq_api_key: str = ""
    database_url: str = ""
    upstash_redis_url: str = ""
    upstash_redis_token: str = ""

    class Config:
        env_file = ".env"

settings = Settings()