import os
from typing import List, Dict, Any
from app.llm.base import LLMProvider

try:
    from groq import Groq
except ImportError:
    Groq = None


class GroqClient(LLMProvider):
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your-groq-key-here":
            self.client = None
        else:
            self.client = Groq(api_key=api_key)

    def generate(
        self, system: str, messages: List[Dict[str, str]], max_tokens: int = 1000
    ) -> Dict[str, Any]:
        if not self.client:
            return {
                "text": "Error: GROQ_API_KEY is missing.",
                "tokens_in": 0,
                "tokens_out": 0,
            }

        formatted_messages = [{"role": "system", "content": system}]
        formatted_messages.extend(messages)

        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Or another available model
            messages=formatted_messages,
            max_tokens=max_tokens,
            temperature=0.0,
        )

        return {
            "text": response.choices[0].message.content,
            "tokens_in": response.usage.prompt_tokens,
            "tokens_out": response.usage.completion_tokens,
        }
