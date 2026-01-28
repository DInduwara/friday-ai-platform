from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol


@dataclass(frozen=True)
class StepEvent:
    kind: str  # "route" | "tool" | "agent" | "final" | "error"
    data: dict[str, Any]


ToolFn = Callable[..., Any]


class Agent(Protocol):
    name: str
    description: str

    def run(self, prompt: str) -> tuple[str, list[StepEvent]]: ...
