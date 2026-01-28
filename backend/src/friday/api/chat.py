from __future__ import annotations

import json
from typing import Generator

from fastapi import APIRouter, Depends, HTTPException
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
        try:
            await repo.add_message(session, user_id, req.conversation_id, role="user", content=req.prompt)
        except ValueError:
            raise HTTPException(status_code=404, detail="Conversation not found")

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
    # Persist user message before streaming (this triggers auto-rename if first msg)
    async with SessionLocal() as session:
        await repo.ensure_user(session, user_id)
        try:
            await repo.add_message(session, user_id, req.conversation_id, role="user", content=req.prompt)
        except ValueError:
            raise HTTPException(status_code=404, detail="Conversation not found")

    final_holder = {"final": ""}

    def gen() -> Generator[bytes, None, None]:
        for item in supervisor.stream(req.prompt, req.conversation_id):
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

    async def streaming():
        for chunk in gen():
            yield chunk
        await finalize_save()

    return StreamingResponse(streaming(), media_type="text/event-stream")
