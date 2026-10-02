from abc import ABC, abstractmethod
from typing import List, Dict, Any


class LLMProvider(ABC):
    @abstractmethod
    def generate(
        self, system: str, messages: List[Dict[str, str]], max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Returns a dict:
        {
            "text": str,
            "tokens_in": int,
            "tokens_out": int
        }
        """
        pass
