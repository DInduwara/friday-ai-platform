from __future__ import annotations

import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from sqlalchemy.exc import OperationalError

from friday.api import chat_router, health_router, conversations_router
from friday.core.config import settings
from friday.core.errors import FridayError, friday_error_handler
from friday.core.logging import configure_logging
from friday.db.models import Base
from friday.db.session import engine

log = logging.getLogger(__name__)


def _custom_openapi(app: FastAPI):
    """
    Adds a BearerAuth security scheme so Swagger UI shows an 'Authorize' button.
    This lets you paste a Clerk JWT and test protected endpoints in /docs.
    """
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )

    schema.setdefault("components", {}).setdefault("securitySchemes", {})["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }

    # Apply globally so all endpoints accept the token in Swagger.
    # If you prefer per-route, remove this line.
    schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = schema
    return app.openapi_schema


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="FRIDAY", version="1.0.0")

    # Enable Swagger "Authorize"
    app.openapi = lambda: _custom_openapi(app)

    app.add_exception_handler(FridayError, friday_error_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup_db():
        if not settings.DB_AUTO_CREATE:
            return

        retries = 10
        delay = 2

        for attempt in range(1, retries + 1):
            try:
                log.info("Connecting to database (attempt %s/%s)...", attempt, retries)
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                log.info("Database ready")
                return
            except OperationalError as e:
                log.warning("Database not ready yet: %s", e)
                if attempt == retries:
                    log.error("Database failed to start after retries")
                    raise
                await asyncio.sleep(delay)

    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(conversations_router)

    return app


app = create_app()
