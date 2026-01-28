from __future__ import annotations

import json
from typing import Generator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from friday.core.auth import require_user
from friday.engine.supervisor import supervisor
from friday.db.session import SessionLocal
from friday.db import repo

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=8000)
    conversation_id: str = Field(min_length=1, max_length=200)


class ChatResponse(BaseModel):
    ok: bool
    reply: str


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest, user_id: str = Depends(require_user)) -> ChatResponse:
    async with SessionLocal() as session:
        await repo.ensure_user(session, user_id)
        await repo.add_message(session, user_id, req.conversation_id, role="user", content=req.prompt)

    final = ""
    for item in supervisor.stream(req.prompt, req.conversation_id):
        if item.get("done"):
            resp = item.get("response") or {}
            if resp.get("kind") == "final":
                final = (resp.get("data") or {}).get("content", "")
            break

    if final:
        async with SessionLocal() as session:
            await repo.ensure_user(session, user_id)
            await repo.add_message(session, user_id, req.conversation_id, role="assistant", content=final)

    return ChatResponse(ok=True, reply=final)


@router.post("/stream")
async def chat_stream(req: ChatRequest, user_id: str = Depends(require_user)):
    # Persist user message before streaming
    async with SessionLocal() as session:
        await repo.ensure_user(session, user_id)
        await repo.add_message(session, user_id, req.conversation_id, role="user", content=req.prompt)

    # We will capture final response and persist after stream ends (best-effort)
    final_holder = {"final": ""}

    def gen() -> Generator[bytes, None, None]:
        for item in supervisor.stream(req.prompt, req.conversation_id):
            # capture final text for DB
            if item.get("done"):
                resp = item.get("response") or {}
                if resp.get("kind") == "final":
                    final_holder["final"] = (resp.get("data") or {}).get("content", "")
            yield b"data: " + json.dumps(item).encode("utf-8") + b"\n\n"

    async def finalize_save():
        final = final_holder["final"].strip()
        if not final:
            return
        async with SessionLocal() as session:
            await repo.ensure_user(session, user_id)
            await repo.add_message(session, user_id, req.conversation_id, role="assistant", content=final)

    # FastAPI doesn't provide a native "on close" hook for StreamingResponse.
    # In practice, response completes normally; we save after generator runs.
    async def streaming():
        for chunk in gen():
            yield chunk
        await finalize_save()

    return StreamingResponse(streaming(), media_type="text/event-stream")
