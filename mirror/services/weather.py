from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import requests


@dataclass
class WeatherSummary:
    description: str
    temperature_c: float
    feels_like_c: float
    humidity: int
    wind_kph: float
    updated_at: datetime

    def format_brief(self) -> str:
        return f"{self.description} {self.temperature_c:.0f}°C (feels {self.feels_like_c:.0f}°C)"


class WeatherService:
    """Fetch current weather from OpenWeatherMap with a fallback stub."""

    def __init__(self, api_key: Optional[str], location: str, units: str = "metric") -> None:
        self.api_key = api_key
        self.location = location
        self.units = units

    def fetch(self) -> WeatherSummary:
        if not self.api_key:
            return self._fallback()

        try:
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {"q": self.location, "appid": self.api_key, "units": self.units}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            main = data.get("main", {})
            wind = data.get("wind", {})
            desc = data.get("weather", [{}])[0].get("description", "Unknown").title()

            return WeatherSummary(
                description=desc,
                temperature_c=float(main.get("temp", 0.0)),
                feels_like_c=float(main.get("feels_like", main.get("temp", 0.0))),
                humidity=int(main.get("humidity", 0)),
                wind_kph=float(wind.get("speed", 0.0)) * 3.6,
                updated_at=datetime.utcnow(),
            )
        except Exception:
            return self._fallback()

    def _fallback(self) -> WeatherSummary:
        return WeatherSummary(
            description="Partly Cloudy (offline)",
            temperature_c=14.0,
            feels_like_c=14.0,
            humidity=65,
            wind_kph=9.0,
            updated_at=datetime.utcnow(),
        )
