from __future__ import annotations

import json
from typing import Generator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from friday.engine.supervisor import supervisor

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=8000)


class ChatResponse(BaseModel):
    ok: bool
    reply: str


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    final = ""
    for item in supervisor.stream(req.prompt):
        if item.get("done"):
            resp = item.get("response") or {}
            if resp.get("kind") == "final":
                final = (resp.get("data") or {}).get("content", "")
            break
    return ChatResponse(ok=True, reply=final)


@router.post("/stream")
def chat_stream(req: ChatRequest):
    def gen() -> Generator[bytes, None, None]:
        for item in supervisor.stream(req.prompt):
            yield b"data: " + json.dumps(item).encode("utf-8") + b"\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
