from __future__ import annotations

import re
from typing import Any, Generator

from friday.agents.launch_vehicle_agent import LaunchVehicleAgent
from friday.agents.math_agent import MathAgent
from friday.agents.poem_agent import PoemAgent
from friday.agents.todoist_agent import TodoistAgent
from friday.agents.weather_agent import WeatherAgent
from friday.engine.types import StepEvent
from friday.llm.groq_client import ChatMessage, get_groq_client
from friday.core.errors import FridayError


class Supervisor:
    def __init__(self) -> None:
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
            # only treat as weather if explicitly asks weather
            if "weather" in p or "temperature" in p or "humidity" in p:
                return "weather"
        if "launch" in p or "rocket" in p or "space" in p:
            return "launch"
        if "todo" in p or "task" in p or "todoist" in p:
            return "todoist"
        if re.search(r"\d\s*[\+\-\*\/]\s*\d", prompt) or "calculate" in p:
            return "math"
        return "default"

    def run(self, prompt: str) -> tuple[str, list[StepEvent]]:
        steps: list[StepEvent] = []
        route = self.route(prompt)
        steps.append(StepEvent(kind="route", data={"agent": route}))

        if route == "default":
            client = get_groq_client()
            if client is None:
                return (
                    "GROQ_API_KEY is not configured. Add it to backend/.env to enable chat features.",
                    steps,
                )
            out = client.chat(
                [
                    ChatMessage(role="system", content="You are FRIDAY: helpful, concise, a little witty."),
                    ChatMessage(role="user", content=prompt),
                ],
                temperature=0.7,
            )
            steps.append(StepEvent(kind="agent", data={"agent": "default", "chars": len(out)}))
            return (out.strip(), steps)

        agent = self.agents[route]
        reply, agent_steps = agent.run(prompt)
        steps.extend(agent_steps)
        return (reply, steps)

    def stream(self, prompt: str) -> Generator[dict[str, Any], None, None]:
        try:
            reply, steps = self.run(prompt)
            # stream steps first
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


supervisor = Supervisor()
