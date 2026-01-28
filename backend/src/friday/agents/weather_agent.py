from __future__ import annotations

import re

from friday.engine.types import Agent, StepEvent
from friday.tools.weather_tool import get_weather


class WeatherAgent(Agent):
    name = "weather"
    description = "Fetches current weather for a given location (requires OPENWEATHER_API_KEY)."

    def run(self, prompt: str) -> tuple[str, list[StepEvent]]:
        steps: list[StepEvent] = []

        # naive location extraction: take last word chunk after 'in'
        m = re.search(r"\bin\s+(.+)$", prompt, re.IGNORECASE)
        location = (m.group(1).strip() if m else prompt.strip())

        data = get_weather(location)
        steps.append(StepEvent(kind="tool", data={"tool": "get_weather", "location": location, "result": data}))

        if not data:
            return (
                "I couldn't fetch weather. Make sure `OPENWEATHER_API_KEY` is set and the location is valid.",
                steps,
            )

        return (
            f"Weather in {location}: {data['temperature']}°C, {data['description']} (humidity {data['humidity']}%).",
            steps,
        )
