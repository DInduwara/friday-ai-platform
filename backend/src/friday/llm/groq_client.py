from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional

import requests

from friday.core.config import settings
from friday.core.errors import FridayError


@dataclass(frozen=True)
class ChatMessage:
    role: str  # "system" | "user" | "assistant"
    content: str


class GroqClient:
    """Minimal Groq Chat Completions client using the OpenAI-compatible API surface.

    Note: Groq's API is designed to be compatible with OpenAI's chat completions schema.
    """

    def __init__(self, api_key: str, model: str | None = None) -> None:
        self.api_key = api_key
        self.model = model or settings.GROQ_MODEL
        self.base_url = "https://api.groq.com/openai/v1"

    def chat(self, messages: list[ChatMessage], temperature: float = 0.7) -> str:
        url = f"{self.base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
        }
        try:
            r = requests.post(
                url,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=30,
            )
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            raise FridayError(f"LLM call failed: {e}", code="LLM_ERROR", status_code=502) from e


def get_groq_client() -> Optional[GroqClient]:
    key = settings.groq_api_key
    if not key:
        return None
    return GroqClient(api_key=key, model=settings.GROQ_MODEL)
