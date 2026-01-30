from __future__ import annotations

import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="FRIDAY_",
        env_file=".env",          # loads locally
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ---- Basic ----
    ENV: str = Field(default="dev")  # dev | prod
    LOG_LEVEL: str = Field(default="INFO")

    # ---- CORS ----
    # Put this in .env / Render as:
    # FRIDAY_ALLOWED_ORIGINS=http://localhost:5173,https://friday-ai-platform.vercel.app
    ALLOWED_ORIGINS: str = Field(default="http://localhost:5173")

    # ---- Database ----
    # Put this in .env / Render:
    # FRIDAY_DATABASE_URL=postgresql+asyncpg://...
    DATABASE_URL: str | None = Field(default=None)

    DB_AUTO_CREATE: bool = Field(default=True)
    DB_ECHO: bool = Field(default=False)

    # ---- Redis (optional, depending on your memory backend) ----
    # FRIDAY_REDIS_URL=redis://....
    REDIS_URL: str | None = Field(default=None)

    # FRIDAY_MEMORY_BACKEND=redis  OR in_memory
    MEMORY_BACKEND: str = Field(default="in_memory")
    MEMORY_TTL_SECONDS: int = Field(default=86400)
    MEMORY_MAX_MESSAGES: int = Field(default=50)

    # ---- Clerk Auth (REQUIRED in prod) ----
    # FRIDAY_CLERK_ISSUER=https://<clerk-domain>
    # FRIDAY_CLERK_JWKS_URL=https://<clerk-domain>/.well-known/jwks.json
    CLERK_ISSUER: str | None = Field(default=None)
    CLERK_JWKS_URL: str | None = Field(default=None)

    # ---- LLM ----
    GROQ_MODEL: str = Field(default="llama-3.3-70b-versatile")

    @property
    def allowed_origins_list(self) -> list[str]:
        return [x.strip() for x in (self.ALLOWED_ORIGINS or "").split(",") if x.strip()]

    @property
    def groq_api_key(self) -> str | None:
        # Supports either GROQ_API_KEY or FRIDAY_GROQ_API_KEY
        return os.getenv("GROQ_API_KEY") or os.getenv("FRIDAY_GROQ_API_KEY")

    def validate_required(self) -> None:
        """
        Fail fast in production if critical env vars are missing.
        """
        is_prod = (self.ENV or "").lower() in ("prod", "production")

        if is_prod:
            missing = []

            if not self.DATABASE_URL:
                missing.append("FRIDAY_DATABASE_URL")
            if not self.CLERK_ISSUER:
                missing.append("FRIDAY_CLERK_ISSUER")
            if not self.CLERK_JWKS_URL:
                missing.append("FRIDAY_CLERK_JWKS_URL")

            # If you're using redis memory in prod, ensure redis url exists
            if (self.MEMORY_BACKEND or "").lower() == "redis" and not self.REDIS_URL:
                missing.append("FRIDAY_REDIS_URL (required because FRIDAY_MEMORY_BACKEND=redis)")

            if missing:
                raise RuntimeError(
                    "Missing required environment variables for production:\n- "
                    + "\n- ".join(missing)
                )


settings = Settings()
settings.validate_required()
