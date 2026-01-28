from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse


class FridayError(Exception):
    def __init__(self, message: str, code: str = "FRIDAY_ERROR", status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


async def friday_error_handler(_: Request, exc: FridayError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"ok": False, "error": {"code": exc.code, "message": exc.message}},
    )
