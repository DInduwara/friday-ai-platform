from __future__ import annotations

from friday.engine.types import Agent, StepEvent
from friday.llm.groq_client import ChatMessage, get_groq_client
from friday.core.errors import FridayError


class PoemAgent(Agent):
    name = "poem"
    description = "Creates poems / creative writing (uses Groq LLM)."

    def run(self, prompt: str) -> tuple[str, list[StepEvent]]:
        steps: list[StepEvent] = []
        client = get_groq_client()
        if client is None:
            raise FridayError(
                "GROQ_API_KEY is not configured. Add it to backend/.env to enable poem generation.",
                code="MISSING_API_KEY",
                status_code=503,
            )

        system = "You are a creative writing assistant. Write clean, vivid poems. Avoid explicit content."
        out = client.chat(
            [
                ChatMessage(role="system", content=system),
                ChatMessage(role="user", content=prompt),
            ],
            temperature=0.9,
        )
        steps.append(StepEvent(kind="agent", data={"agent": "poem", "chars": len(out)}))
        return (out.strip(), steps)
