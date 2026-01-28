from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from friday.core.auth import require_user
from friday.db.session import SessionLocal
from friday.db import repo

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


class CreateConversationRequest(BaseModel):
    title: str | None = Field(default="New chat", max_length=120)


@router.get("")
async def list_conversations(
    q: str | None = Query(default=None, max_length=120),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    user_id: str = Depends(require_user),
):
    async with SessionLocal() as session:
        total, convos = await repo.list_conversations(session, user_id, q=q, limit=limit, offset=offset)
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": [
                {
                    "id": c.id,
                    "title": c.title,
                    "created_at": c.created_at,
                    "updated_at": c.updated_at,
                }
                for c in convos
            ],
        }


@router.post("")
async def create_conversation(body: CreateConversationRequest, user_id: str = Depends(require_user)):
    async with SessionLocal() as session:
        await repo.ensure_user(session, user_id)
        convo = await repo.create_conversation(session, user_id, body.title or "New chat")
        return {
            "id": convo.id,
            "title": convo.title,
            "created_at": convo.created_at,
            "updated_at": convo.updated_at,
        }


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str, user_id: str = Depends(require_user)):
    async with SessionLocal() as session:
        ok = await repo.delete_conversation(session, user_id, conversation_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return {"ok": True}


@router.get("/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    limit: int = Query(default=30, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    user_id: str = Depends(require_user),
):
    async with SessionLocal() as session:
        total, msgs = await repo.list_messages(session, user_id, conversation_id, limit=limit, offset=offset)

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "created_at": m.created_at,
                }
                for m in msgs
            ],
        }
