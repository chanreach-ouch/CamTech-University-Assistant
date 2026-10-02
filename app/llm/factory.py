from app.llm.groq_client import GroqClient
from app.llm.gemini_client import GeminiClient
from app.config import settings


def get_llm():
    provider = settings.LLM_PROVIDER.lower()
    if provider == "groq":
        return GroqClient()
    elif provider == "gemini":
        return GeminiClient()
    else:
        # Fallback to Groq
        return GroqClient()
