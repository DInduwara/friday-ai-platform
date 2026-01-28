from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from friday.db.models import User, Conversation, Message


# ---------- USERS ----------

async def ensure_user(session: AsyncSession, user_id: str) -> User:
    user = await session.get(User, user_id)
    if user:
        return user

    user = User(id=user_id)
    session.add(user)
    await session.commit()
    return user


# ---------- CONVERSATIONS ----------

async def create_conversation(
    session: AsyncSession, user_id: str, title: str = "New chat"
) -> Conversation:
    convo = Conversation(user_id=user_id, title=title)
    session.add(convo)
    await session.commit()
    await session.refresh(convo)
    return convo


async def list_conversations(session: AsyncSession, user_id: str) -> list[Conversation]:
    q = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    res = await session.execute(q)
    return list(res.scalars())


async def get_conversation(
    session: AsyncSession, user_id: str, conversation_id: str
) -> Conversation | None:
    convo = await session.get(Conversation, conversation_id)
    if not convo or convo.user_id != user_id:
        return None
    return convo


# ---------- MESSAGES ----------

async def add_message(
    session: AsyncSession,
    user_id: str,
    conversation_id: str,
    role: str,
    content: str,
) -> Message:
    convo = await get_conversation(session, user_id, conversation_id)
    if not convo:
        raise ValueError("Conversation not found")

    msg = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )
    session.add(msg)
    await session.commit()
    return msg


async def list_messages(
    session: AsyncSession, user_id: str, conversation_id: str
) -> list[Message]:
    convo = await get_conversation(session, user_id, conversation_id)
    if not convo:
        return []

    q = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    res = await session.execute(q)
    return list(res.scalars())
