from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from friday.core.auth import require_user
from friday.db.session import SessionLocal
from friday.db import repo

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


class ConversationOut(BaseModel):
    id: str
    title: str


class CreateConversationIn(BaseModel):
    title: str = Field(default="New chat", min_length=1, max_length=120)


class RenameConversationIn(BaseModel):
    title: str = Field(min_length=1, max_length=120)


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    created_at: str


@router.get("", response_model=list[ConversationOut])
async def list_all(user_id: str = Depends(require_user)):
    async with SessionLocal() as session:
        await repo.ensure_user(session, user_id)
        items = await repo.list_conversations(session, user_id)
        return [ConversationOut(id=c.id, title=c.title) for c in items]


@router.post("", response_model=ConversationOut)
async def create(payload: CreateConversationIn, user_id: str = Depends(require_user)):
    async with SessionLocal() as session:
        await repo.ensure_user(session, user_id)
        c = await repo.create_conversation(session, user_id, payload.title)
        return ConversationOut(id=c.id, title=c.title)


@router.patch("/{conversation_id}")
async def rename(conversation_id: str, payload: RenameConversationIn, user_id: str = Depends(require_user)):
    async with SessionLocal() as session:
        await repo.ensure_user(session, user_id)
        await repo.rename_conversation(session, user_id, conversation_id, payload.title)
        return {"ok": True}


@router.delete("/{conversation_id}")
async def remove(conversation_id: str, user_id: str = Depends(require_user)):
    async with SessionLocal() as session:
        await repo.ensure_user(session, user_id)
        await repo.delete_conversation(session, user_id, conversation_id)
        return {"ok": True}


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def messages(conversation_id: str, user_id: str = Depends(require_user)):
    async with SessionLocal() as session:
        await repo.ensure_user(session, user_id)
        msgs = await repo.get_messages(session, user_id, conversation_id)
        return [
            MessageOut(
                id=m.id,
                role=m.role,
                content=m.content,
                created_at=m.created_at.isoformat(),
            )
            for m in msgs
        ]
