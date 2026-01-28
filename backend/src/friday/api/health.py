from __future__ import annotations

from fastapi import APIRouter

from friday.core.config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health() -> dict:
    return {"ok": True}


@router.get("/ready")
def ready() -> dict:
    groq = bool(settings.groq_api_key)
    return {"ok": True, "checks": {"groq_api_key_configured": groq}}
