from __future__ import annotations

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="FRIDAY_",
        env_file=".env",
        extra="ignore",
    )

    ENV: str = "dev"
    LOG_LEVEL: str = "INFO"
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    FULL_AI_TRACE: bool = False

    # LLM
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Redis conversation memory (still used for short-term tool memory, optional)
    REDIS_URL: str = "redis://localhost:6379/0"
    MEMORY_TTL_SECONDS: int = 86400
    MEMORY_BACKEND: str = "redis"  # "redis" | "in_memory"
    MEMORY_MAX_MESSAGES: int = 50

    # Clerk Auth
    CLERK_ISSUER: str | None = None
    CLERK_JWKS_URL: str | None = None

    # PostgreSQL
    DATABASE_URL: str = "postgresql+asyncpg://friday:friday@localhost:5432/friday"
    DB_ECHO: bool = False
    DB_AUTO_CREATE: bool = True  # dev convenience: auto create tables at startup

    @property
    def allowed_origins_list(self) -> list[str]:
        return [x.strip() for x in self.ALLOWED_ORIGINS.split(",") if x.strip()]

    @property
    def groq_api_key(self) -> str | None:
        return os.getenv("GROQ_API_KEY") or os.getenv("FRIDAY_GROQ_API_KEY")


settings = Settings()
