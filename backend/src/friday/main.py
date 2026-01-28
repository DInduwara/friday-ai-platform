from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from friday.api import chat_router, health_router, conversations_router
from friday.core.config import settings
from friday.core.errors import FridayError, friday_error_handler
from friday.core.logging import configure_logging

from friday.db.session import engine
from friday.db.models import Base


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="FRIDAY", version="1.0.0")

    app.add_exception_handler(FridayError, friday_error_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def _startup():
        if settings.DB_AUTO_CREATE:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(conversations_router)
    return app


app = create_app()
