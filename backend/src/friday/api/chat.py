from __future__ import annotations

import json
from typing import Generator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from friday.core.auth import require_user
from friday.engine.supervisor import supervisor

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=8000)
    conversation_id: str = Field(default="default", min_length=1, max_length=200)


class ChatResponse(BaseModel):
    ok: bool
    reply: str


class ClearRequest(BaseModel):
    conversation_id: str = Field(min_length=1, max_length=200)


def _scoped_conversation_id(user_id: str, conversation_id: str) -> str:
    # User isolation: prevents seeing other users' memory/history
    return f"{user_id}:{conversation_id}"


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest, user_id: str = Depends(require_user)) -> ChatResponse:
    final = ""
    cid = _scoped_conversation_id(user_id, req.conversation_id)

    for item in supervisor.stream(req.prompt, cid):
        if item.get("done"):
            resp = item.get("response") or {}
            if resp.get("kind") == "final":
                final = (resp.get("data") or {}).get("content", "")
            break
    return ChatResponse(ok=True, reply=final)


@router.post("/stream")
def chat_stream(req: ChatRequest, user_id: str = Depends(require_user)):
    cid = _scoped_conversation_id(user_id, req.conversation_id)

    def gen() -> Generator[bytes, None, None]:
        for item in supervisor.stream(req.prompt, cid):
            yield b"data: " + json.dumps(item).encode("utf-8") + b"\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


@router.post("/clear")
def clear(req: ClearRequest, user_id: str = Depends(require_user)) -> dict:
    cid = _scoped_conversation_id(user_id, req.conversation_id)
    supervisor.clear(cid)
    return {"ok": True}
