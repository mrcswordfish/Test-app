from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import requests


@dataclass
class AuroraForecast:
    kp_index: float
    likelihood: str
    map_image: str
    updated_at: datetime

    def format_brief(self) -> str:
        return f"Kp {self.kp_index:.1f} · {self.likelihood}"


class AuroraService:
    """Fetch aurora Kp and show the current oval map. Falls back to sample data."""

    def __init__(self, latitude: Optional[float] = None, longitude: Optional[float] = None) -> None:
        self.latitude = latitude
        self.longitude = longitude

    def fetch(self) -> AuroraForecast:
        try:
            response = requests.get(
                "https://services.swpc.noaa.gov/json/ovation_aurora_latest.json", timeout=10
            )
            response.raise_for_status()
            data = response.json()
            kp = float(data.get("Kp", 4.0))
            likelihood = self._describe_likelihood(kp)
            return AuroraForecast(
                kp_index=kp,
                likelihood=likelihood,
                map_image="https://services.swpc.noaa.gov/images/aurora-forecast-northern-hemisphere.jpg",
                updated_at=datetime.now(timezone.utc),
            )
        except Exception:
            return self._fallback()

    def _fallback(self) -> AuroraForecast:
        return AuroraForecast(
            kp_index=4.0,
            likelihood="Active aurora likely across higher latitudes (offline sample)",
            map_image="https://services.swpc.noaa.gov/images/aurora-forecast-northern-hemisphere.jpg",
            updated_at=datetime.now(timezone.utc),
        )

    def _describe_likelihood(self, kp: float) -> str:
        if kp >= 7:
            return "Severe storm: aurora possible at mid-latitudes"
        if kp >= 5:
            return "G-level storm: strong aurora likely"
        if kp >= 4:
            return "Active aurora likely for northern skies"
        if kp >= 3:
            return "Quiet to unsettled"
        return "Quiet"


__all__ = ["AuroraService", "AuroraForecast"]
