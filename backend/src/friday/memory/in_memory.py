from __future__ import annotations

from collections import defaultdict

from friday.memory.base import ConversationMemory, MemoryMessage


class InMemoryConversationMemory(ConversationMemory):
    def __init__(self) -> None:
        self._store: dict[str, list[MemoryMessage]] = defaultdict(list)

    def load(self, conversation_id: str) -> list[MemoryMessage]:
        return list(self._store.get(conversation_id, []))

    def append(self, conversation_id: str, message: MemoryMessage) -> None:
        self._store[conversation_id].append(message)

    def clear(self, conversation_id: str) -> None:
        self._store.pop(conversation_id, None)
