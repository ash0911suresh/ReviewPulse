from app.config import settings
from app.services.llm.base import BaseLLMAdapter

def get_llm_adapter() -> BaseLLMAdapter:
    if settings.llm_provider == "groq":
        from app.services.llm.groq_adapter import GroqAdapter
        return GroqAdapter()
    raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")
