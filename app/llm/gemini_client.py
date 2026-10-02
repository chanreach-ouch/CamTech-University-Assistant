import os
from typing import List, Dict, Any
from app.llm.base import LLMProvider

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None


class GeminiClient(LLMProvider):
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your-gemini-key-here":
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)

    def generate(
        self, system: str, messages: List[Dict[str, str]], max_tokens: int = 1000
    ) -> Dict[str, Any]:
        if not self.client:
            return {
                "text": "Error: GEMINI_API_KEY is missing.",
                "tokens_in": 0,
                "tokens_out": 0,
            }

        formatted_contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            formatted_contents.append(
                types.Content(
                    role=role, parts=[types.Part.from_text(text=msg["content"])]
                )
            )

        config = types.GenerateContentConfig(
            system_instruction=system, max_output_tokens=max_tokens, temperature=0.0
        )

        response = self.client.models.generate_content(
            model="gemini-2.5-flash", contents=formatted_contents, config=config
        )

        return {
            "text": response.text,
            "tokens_in": response.usage_metadata.prompt_token_count
            if response.usage_metadata
            else 0,
            "tokens_out": response.usage_metadata.candidates_token_count
            if response.usage_metadata
            else 0,
        }
