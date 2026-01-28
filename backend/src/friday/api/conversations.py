from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from friday.core.auth import require_user
from friday.db.session import SessionLocal
from friday.db import repo

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


class CreateConversationRequest(BaseModel):
    title: str | None = "New chat"


@router.get("")
async def list_conversations(user_id: str = Depends(require_user)):
    async with SessionLocal() as session:
        convos = await repo.list_conversations(session, user_id)
        return [
            {
                "id": c.id,
                "title": c.title,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
            }
            for c in convos
        ]


@router.post("")
async def create_conversation(
    body: CreateConversationRequest,
    user_id: str = Depends(require_user),
):
    async with SessionLocal() as session:
        await repo.ensure_user(session, user_id)
        convo = await repo.create_conversation(session, user_id, body.title or "New chat")
        return {
            "id": convo.id,
            "title": convo.title,
            "created_at": convo.created_at,
        }


@router.get("/{conversation_id}/messages")
async def get_messages(conversation_id: str, user_id: str = Depends(require_user)):
    async with SessionLocal() as session:
        msgs = await repo.list_messages(session, user_id, conversation_id)
        return [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at,
            }
            for m in msgs
        ]
