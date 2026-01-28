from __future__ import annotations

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from friday.db.models import User, Conversation, Message


async def ensure_user(session: AsyncSession, user_id: str) -> None:
    existing = await session.get(User, user_id)
    if existing:
        return
    session.add(User(id=user_id))
    await session.commit()


async def list_conversations(session: AsyncSession, user_id: str) -> list[Conversation]:
    q = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    return list((await session.execute(q)).scalars().all())


async def create_conversation(session: AsyncSession, user_id: str, title: str = "New chat") -> Conversation:
    c = Conversation(user_id=user_id, title=title)
    session.add(c)
    await session.commit()
    await session.refresh(c)
    return c


async def rename_conversation(session: AsyncSession, user_id: str, conversation_id: str, title: str) -> None:
    q = (
        update(Conversation)
        .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
        .values(title=title)
    )
    await session.execute(q)
    await session.commit()


async def delete_conversation(session: AsyncSession, user_id: str, conversation_id: str) -> None:
    q = delete(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user_id)
    await session.execute(q)
    await session.commit()


async def get_messages(session: AsyncSession, user_id: str, conversation_id: str) -> list[Message]:
    # ensure conversation belongs to user
    cq = select(Conversation.id).where(Conversation.id == conversation_id, Conversation.user_id == user_id)
    ok = (await session.execute(cq)).scalar_one_or_none()
    if not ok:
        return []

    q = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    return list((await session.execute(q)).scalars().all())


async def add_message(session: AsyncSession, user_id: str, conversation_id: str, role: str, content: str) -> None:
    # ensure conversation belongs to user
    cq = select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user_id)
    conv = (await session.execute(cq)).scalar_one_or_none()
    if not conv:
        # auto-create conversation if missing (safe default for stream endpoint)
        conv = await create_conversation(session, user_id, title="New chat")

    session.add(Message(conversation_id=conv.id, role=role, content=content))
    # bump updated_at
    conv.title = conv.title or "New chat"
    await session.commit()
