from __future__ import annotations

import re
from typing import Any

from friday.engine.types import Agent, StepEvent
from friday.tools.todoist_tools import add_task, close_task, list_tasks


class TodoistAgent(Agent):
    name = "todoist"
    description = "Manages Todoist tasks (requires TODOIST_API_KEY)."

    def run(self, prompt: str) -> tuple[str, list[StepEvent]]:
        steps: list[StepEvent] = []
        p = prompt.lower().strip()

        if p.startswith("add ") or "add task" in p:
            content = re.sub(r"^add\s+", "", prompt, flags=re.IGNORECASE).strip()
            res = add_task(content)
            steps.append(StepEvent(kind="tool", data={"tool": "add_task", "content": content, "result": res}))
            if res.get("error"):
                return (str(res["error"]), steps)
            return (f"Added task: {res.get('content','(created)')}", steps)

        if "close" in p or "complete" in p:
            m = re.search(r"(\d+)", prompt)
            if not m:
                return ("Tell me the task id to close.", steps)
            task_id = m.group(1)
            res = close_task(task_id)
            steps.append(StepEvent(kind="tool", data={"tool": "close_task", "task_id": task_id, "result": res}))
            if res.get("error"):
                return (str(res["error"]), steps)
            return ("Closed the task.", steps)

        tasks = list_tasks()
        steps.append(StepEvent(kind="tool", data={"tool": "list_tasks", "result_count": len(tasks)}))
        if not tasks:
            return ("No tasks found (or TODOIST_API_KEY not configured).", steps)

        lines = [f"- [{t.get('id')}] {t.get('content')}" for t in tasks[:15]]
        return ("Your tasks:\n" + "\n".join(lines), steps)
