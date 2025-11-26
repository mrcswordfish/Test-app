from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

import requests


@dataclass
class TransitPrediction:
    route: str
    destination: str
    departure_time: datetime

    def format_brief(self) -> str:
        mins = int((self.departure_time - datetime.now()).total_seconds() / 60)
        return f"{self.route} to {self.destination} in {max(mins, 0)} min"


class BCTransitService:
    """
    Fetch next departures from the BC Transit public API.

    The default endpoint mirrors the documented v1.2 TransitAPI predictions path. Adjust
    `base_url` if BC Transit updates their routes, or swap the implementation to use
    GTFS-realtime feeds if you prefer.
    """

    def __init__(
        self,
        api_key: Optional[str],
        region: Optional[str],
        stop_id: Optional[str],
        base_url: str = "https://api.bctransit.com/transitapi/v1.2/",
    ) -> None:
        self.api_key = api_key
        self.region = region
        self.stop_id = stop_id
        self.base_url = base_url.rstrip("/") + "/"

    def predictions(self, limit: int = 3) -> List[TransitPrediction]:
        if not all([self.api_key, self.region, self.stop_id]):
            return self._fallback()

        try:
            url = f"{self.base_url}{self.region}/stops/{self.stop_id}/predictions"
            response = requests.get(url, params={"apiKey": self.api_key}, timeout=10)
            response.raise_for_status()
            data = response.json()
            departures = data.get("Departures", []) or data.get("departures", [])

            predictions: List[TransitPrediction] = []
            for dep in departures:
                route = dep.get("RouteNo") or dep.get("route") or "Route"
                destination = dep.get("Destination") or dep.get("destination") or "Destination"
                departure_str = dep.get("ExpectedLeaveTime") or dep.get("departureTime")
                when = self._parse_time(departure_str)
                if when:
                    predictions.append(
                        TransitPrediction(route=route, destination=destination, departure_time=when)
                    )

            predictions.sort(key=lambda p: p.departure_time)
            return predictions[:limit] if predictions else self._fallback()
        except Exception:
            return self._fallback()

    def _parse_time(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        # BC Transit returns values like "7:20pm"; fall back to 10 minutes from now if parsing fails.
        try:
            return datetime.strptime(value, "%I:%M%p").replace(
                year=datetime.now().year, month=datetime.now().month, day=datetime.now().day
            )
        except Exception:
            return datetime.now() + timedelta(minutes=10)

    def _fallback(self) -> List[TransitPrediction]:
        now = datetime.now()
        return [
            TransitPrediction("14", "Downtown (offline)", now + timedelta(minutes=8)),
            TransitPrediction("26", "UVic (offline)", now + timedelta(minutes=15)),
        ]
