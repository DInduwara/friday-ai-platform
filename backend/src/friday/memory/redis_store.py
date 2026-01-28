from __future__ import annotations

import json
import logging

from redis import Redis

from friday.memory.base import ConversationMemory, MemoryMessage

log = logging.getLogger(__name__)


def _key(conversation_id: str) -> str:
    return f"friday:conversation:{conversation_id}"


class RedisConversationMemory(ConversationMemory):
    def __init__(self, redis: Redis, ttl_seconds: int = 86400, max_messages: int = 50) -> None:
        self._redis = redis
        self._ttl = ttl_seconds
        self._max = max_messages  # prevent unbounded growth

    def load(self, conversation_id: str) -> list[MemoryMessage]:
        k = _key(conversation_id)
        raw_items = self._redis.lrange(k, 0, -1)
        out: list[MemoryMessage] = []
        for b in raw_items:
            try:
                obj = json.loads(b.decode("utf-8"))
                out.append(MemoryMessage(role=obj["role"], content=obj["content"]))
            except Exception:
                log.exception("Failed to decode memory message from Redis")
        return out

    def append(self, conversation_id: str, message: MemoryMessage) -> None:
        k = _key(conversation_id)
        payload = json.dumps({"role": message.role, "content": message.content}).encode("utf-8")

        pipe = self._redis.pipeline()
        pipe.rpush(k, payload)

        # keep last N messages only (trim left side)
        pipe.ltrim(k, max(0, -self._max), -1)

        # refresh TTL
        pipe.expire(k, self._ttl)

        pipe.execute()

    def clear(self, conversation_id: str) -> None:
        self._redis.delete(_key(conversation_id))
