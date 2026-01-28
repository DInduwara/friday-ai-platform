from __future__ import annotations

import logging
import re
from typing import Any, Generator

from redis import Redis

from friday.agents.launch_vehicle_agent import LaunchVehicleAgent
from friday.agents.math_agent import MathAgent
from friday.agents.poem_agent import PoemAgent
from friday.agents.todoist_agent import TodoistAgent
from friday.agents.weather_agent import WeatherAgent
from friday.core.config import settings
from friday.core.errors import FridayError
from friday.engine.types import StepEvent
from friday.llm.groq_client import ChatMessage, get_groq_client
from friday.memory import ConversationMemory, InMemoryConversationMemory, MemoryMessage, RedisConversationMemory

log = logging.getLogger(__name__)


def build_memory() -> ConversationMemory:
    backend = (settings.MEMORY_BACKEND or "redis").lower().strip()
    if backend == "in_memory":
        log.info("Memory backend: in_memory")
        return InMemoryConversationMemory()

    # default redis
    try:
        r = Redis.from_url(settings.REDIS_URL, decode_responses=False)
        r.ping()
        log.info("Memory backend: redis (%s)", settings.REDIS_URL)
        return RedisConversationMemory(
            redis=r,
            ttl_seconds=settings.MEMORY_TTL_SECONDS,
            max_messages=settings.MEMORY_MAX_MESSAGES,
        )
    except Exception:
        log.exception("Redis unavailable, falling back to in_memory")
        return InMemoryConversationMemory()


class Supervisor:
    def __init__(self, memory: ConversationMemory) -> None:
        self.memory = memory
        self.agents = {
            "math": MathAgent(),
            "poem": PoemAgent(),
            "weather": WeatherAgent(),
            "launch": LaunchVehicleAgent(),
            "todoist": TodoistAgent(),
        }

    def route(self, prompt: str) -> str:
        p = prompt.lower()

        if "poem" in p or "write a poem" in p or "lyrics" in p:
            return "poem"
        if "weather" in p or "temperature" in p or re.search(r"\b(in|at)\s+[A-Za-z]", prompt):
            if "weather" in p or "temperature" in p or "humidity" in p:
                return "weather"
        if "launch" in p or "rocket" in p or "space" in p:
            return "launch"
        if "todo" in p or "task" in p or "todoist" in p:
            return "todoist"
        if re.search(r"\d\s*[\+\-\*\/]\s*\d", prompt) or "calculate" in p:
            return "math"
        return "default"

    def clear(self, conversation_id: str) -> None:
        self.memory.clear(conversation_id)

    def run(self, prompt: str, conversation_id: str) -> tuple[str, list[StepEvent]]:
        steps: list[StepEvent] = []
        route = self.route(prompt)
        steps.append(StepEvent(kind="route", data={"agent": route, "conversation_id": conversation_id}))

        # ✅ Default route uses Redis-backed memory
        if route == "default":
            client = get_groq_client()
            if client is None:
                return (
                    "GROQ_API_KEY is not configured. Add it to backend/.env to enable chat features.",
                    steps,
                )

            mem = self.memory.load(conversation_id)
            steps.append(StepEvent(kind="memory", data={"messages_loaded": len(mem)}))

            messages: list[ChatMessage] = [
                ChatMessage(role="system", content="You are FRIDAY: helpful, concise, a little witty.")
            ]

            # replay memory
            for m in mem:
                messages.append(ChatMessage(role=m.role, content=m.content))

            # add current prompt
            messages.append(ChatMessage(role="user", content=prompt))

            out = client.chat(messages, temperature=0.7)
            reply = out.strip()

            # persist (user + assistant)
            self.memory.append(conversation_id, MemoryMessage(role="user", content=prompt))
            self.memory.append(conversation_id, MemoryMessage(role="assistant", content=reply))
            steps.append(StepEvent(kind="memory", data={"messages_saved": 2}))

            steps.append(StepEvent(kind="agent", data={"agent": "default", "chars": len(reply)}))
            return (reply, steps)

        # Tool agents stay stateless for now (clean + safe)
        agent = self.agents[route]
        reply, agent_steps = agent.run(prompt)
        steps.extend(agent_steps)

        # Optionally store tool-agent chats too (recommended)
        self.memory.append(conversation_id, MemoryMessage(role="user", content=prompt))
        self.memory.append(conversation_id, MemoryMessage(role="assistant", content=reply))
        steps.append(StepEvent(kind="memory", data={"messages_saved": 2}))

        return (reply, steps)

    def stream(self, prompt: str, conversation_id: str) -> Generator[dict[str, Any], None, None]:
        try:
            reply, steps = self.run(prompt, conversation_id)

            history: list[dict[str, Any]] = []
            for s in steps:
                item = {"kind": s.kind, "data": s.data}
                history.append(item)
                yield {"response": item, "step": history, "done": False}

            yield {"response": {"kind": "final", "data": {"content": reply}}, "step": history, "done": True}

        except FridayError as e:
            yield {
                "response": {"kind": "error", "data": {"code": e.code, "message": e.message}},
                "step": [],
                "done": True,
            }


#  global supervisor using configured memory
supervisor = Supervisor(memory=build_memory())
