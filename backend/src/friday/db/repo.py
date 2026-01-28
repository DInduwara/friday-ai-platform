from __future__ import annotations

import re
from typing import Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from friday.db.models import User, Conversation, Message

DEFAULT_TITLE = "New chat"


def _make_title_from_first_message(text: str) -> str:
    t = (text or "").strip()
    t = re.sub(r"\s+", " ", t)
    if not t:
        return DEFAULT_TITLE
    max_len = 48
    return t if len(t) <= max_len else t[:max_len].rstrip() + "…"


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

async def create_conversation(session: AsyncSession, user_id: str, title: str = DEFAULT_TITLE) -> Conversation:
    convo = Conversation(user_id=user_id, title=title or DEFAULT_TITLE)
    session.add(convo)
    await session.commit()
    await session.refresh(convo)
    return convo


async def get_conversation(session: AsyncSession, user_id: str, conversation_id: str) -> Conversation | None:
    convo = await session.get(Conversation, conversation_id)
    if not convo or convo.user_id != user_id:
        return None
    return convo


async def delete_conversation(session: AsyncSession, user_id: str, conversation_id: str) -> bool:
    convo = await get_conversation(session, user_id, conversation_id)
    if not convo:
        return False
    await session.delete(convo)
    await session.commit()
    return True


async def list_conversations(
    session: AsyncSession,
    user_id: str,
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> Tuple[int, list[Conversation]]:
    limit = max(1, min(limit, 200))
    offset = max(0, offset)

    base = select(Conversation).where(Conversation.user_id == user_id)

    if q and q.strip():
        base = base.where(Conversation.title.ilike(f"%{q.strip()}%"))

    count_q = select(func.count()).select_from(base.subquery())
    total = int((await session.execute(count_q)).scalar() or 0)

    data_q = base.order_by(Conversation.updated_at.desc()).limit(limit).offset(offset)
    res = await session.execute(data_q)
    return total, list(res.scalars())


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

    # Auto-rename ONLY when first user message and still default title
    if role == "user" and (convo.title or DEFAULT_TITLE) == DEFAULT_TITLE:
        cnt_q = select(func.count()).select_from(
            select(Message.id).where(Message.conversation_id == conversation_id).subquery()
        )
        existing = int((await session.execute(cnt_q)).scalar() or 0)
        if existing == 0:
            convo.title = _make_title_from_first_message(content)

    msg = Message(conversation_id=conversation_id, role=role, content=content)
    session.add(msg)

    # keep updated_at fresh when new messages arrive
    convo.updated_at = func.now()

    await session.commit()
    return msg


async def list_messages(
    session: AsyncSession,
    user_id: str,
    conversation_id: str,
    limit: int = 30,
    offset: int = 0,
) -> Tuple[int, list[Message]]:
    convo = await get_conversation(session, user_id, conversation_id)
    if not convo:
        return 0, []

    limit = max(1, min(limit, 200))
    offset = max(0, offset)

    base = select(Message).where(Message.conversation_id == conversation_id)

    count_q = select(func.count()).select_from(base.subquery())
    total = int((await session.execute(count_q)).scalar() or 0)

    # IMPORTANT:
    # return newest messages first for ChatGPT-style pagination
    data_q = base.order_by(Message.created_at.desc()).limit(limit).offset(offset)
    res = await session.execute(data_q)
    items = list(res.scalars())
    return total, items
