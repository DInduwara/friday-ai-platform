from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal


Role = Literal["system", "user", "assistant"]


@dataclass(frozen=True)
class MemoryMessage:
    role: Role
    content: str


class ConversationMemory(ABC):
    @abstractmethod
    def load(self, conversation_id: str) -> list[MemoryMessage]:
        raise NotImplementedError

    @abstractmethod
    def append(self, conversation_id: str, message: MemoryMessage) -> None:
        raise NotImplementedError

    @abstractmethod
    def clear(self, conversation_id: str) -> None:
        raise NotImplementedError
