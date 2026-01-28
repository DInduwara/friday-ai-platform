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

    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [x.strip() for x in self.ALLOWED_ORIGINS.split(",") if x.strip()]

    @property
    def groq_api_key(self) -> str | None:
        return os.getenv("GROQ_API_KEY") or os.getenv("FRIDAY_GROQ_API_KEY")


settings = Settings()
