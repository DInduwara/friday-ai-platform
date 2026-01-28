from __future__ import annotations

import os
from typing import Optional, TypedDict

import requests


class WeatherOutput(TypedDict):
    temperature: float
    description: str
    humidity: int
    wind_speed: float
    unit: str


def _get_openweather_key() -> Optional[str]:
    return os.getenv("OPENWEATHER_API_KEY") or os.getenv("WHEATHER_API_KEY")


def get_weather(location: str) -> Optional[WeatherOutput]:
    api_key = _get_openweather_key()
    if not api_key:
        return None

    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": location, "appid": api_key, "units": "metric"}

    try:
        r = requests.get(base_url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        return {
            "temperature": float(data["main"]["temp"]),
            "description": str(data["weather"][0]["description"]),
            "humidity": int(data["main"]["humidity"]),
            "wind_speed": float(data["wind"]["speed"]),
            "unit": "Celsius",
        }
    except Exception:
        return None
