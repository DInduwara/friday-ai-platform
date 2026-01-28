from __future__ import annotations

from typing import Any, Optional

import requests

BASE = "https://ll.thespacedevs.com/2.2.0"


def next_launch(rocket_name: Optional[str] = None) -> dict[str, Any]:
    params = {"limit": 1}
    if rocket_name:
        params["search"] = rocket_name

    r = requests.get(f"{BASE}/launch/upcoming/", params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    if not data.get("results"):
        return {"found": False}
    item = data["results"][0]
    return {
        "found": True,
        "name": item.get("name"),
        "net": item.get("net"),
        "status": (item.get("status") or {}).get("name"),
        "pad": ((item.get("pad") or {}).get("name")),
        "location": (((item.get("pad") or {}).get("location") or {}).get("name")),
        "mission": ((item.get("mission") or {}).get("description")),
        "url": item.get("url"),
    }
