from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    supabase_url: str
    supabase_service_key: str
    groq_api_key: str = ""
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "dev-secret-change-in-prod"
    llm_provider: str = "groq"

    class Config:
        env_file = ".env"

settings = Settings()
