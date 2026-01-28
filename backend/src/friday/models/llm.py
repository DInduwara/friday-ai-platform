from __future__ import annotations

import os
from typing import Optional

from langchain_groq import ChatGroq

from friday.core.config import settings


def get_groq_key() -> Optional[str]:
    # prefer correct name; support legacy typo from old repo just in case
    return os.getenv("GROQ_API_KEY") or os.getenv("FRIDAY_GROQ_API_KEY")


def get_llm():
    key = get_groq_key()
    if not key:
        # We intentionally do NOT crash the whole API when keys are missing.
        # Endpoints will return a helpful error instead.
        return None

    return ChatGroq(
        model=settings.GROQ_MODEL,
        groq_api_key=key,
        temperature=0.7,
    )
