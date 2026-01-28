from __future__ import annotations

import os
from typing import Any, Optional

import requests

TODOIST_API_BASE = "https://api.todoist.com/rest/v2"


def _key() -> Optional[str]:
    return os.getenv("TODOIST_API_KEY")


def _headers() -> dict[str, str]:
    k = _key()
    return {"Authorization": f"Bearer {k}"} if k else {}


def list_tasks() -> list[dict[str, Any]]:
    if not _key():
        return []
    r = requests.get(f"{TODOIST_API_BASE}/tasks", headers=_headers(), timeout=15)
    r.raise_for_status()
    return r.json()


def add_task(content: str) -> dict[str, Any]:
    if not _key():
        return {"error": "TODOIST_API_KEY not configured"}
    r = requests.post(
        f"{TODOIST_API_BASE}/tasks",
        headers={**_headers(), "Content-Type": "application/json"},
        json={"content": content},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def close_task(task_id: str) -> dict[str, Any]:
    if not _key():
        return {"error": "TODOIST_API_KEY not configured"}
    r = requests.post(f"{TODOIST_API_BASE}/tasks/{task_id}/close", headers=_headers(), timeout=15)
    if r.status_code == 204:
        return {"ok": True}
    r.raise_for_status()
    return {"ok": True}
