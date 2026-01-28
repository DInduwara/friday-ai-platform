from __future__ import annotations

from friday.engine.types import Agent, StepEvent
from friday.tools.launch_vehicle_tool import next_launch


class LaunchVehicleAgent(Agent):
    name = "launch"
    description = "Gets upcoming rocket launch info (Launch Library 2)."

    def run(self, prompt: str) -> tuple[str, list[StepEvent]]:
        steps: list[StepEvent] = []
        # optional keyword search: everything after 'for'
        rocket_name = None
        if "for" in prompt.lower():
            rocket_name = prompt.split("for", 1)[1].strip() or None

        info = next_launch(rocket_name=rocket_name)
        steps.append(StepEvent(kind="tool", data={"tool": "next_launch", "rocket_name": rocket_name, "result": info}))

        if not info.get("found"):
            return ("Couldn't find an upcoming launch for that query.", steps)

        return (
            f"Next launch: {info.get('name')}\nNET: {info.get('net')}\nStatus: {info.get('status')}\nLocation: {info.get('location')}\n",
            steps,
        )
