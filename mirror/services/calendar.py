from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

import requests
from ics import Calendar


@dataclass
class CalendarEvent:
    title: str
    start: datetime
    end: datetime

    def format_brief(self) -> str:
        start_str = self.start.strftime("%a %b %d %H:%M")
        return f"{start_str} · {self.title}"


class CalendarService:
    """Fetch upcoming events from an ICS feed with offline fallback."""

    def __init__(self, ics_url: Optional[str]) -> None:
        self.ics_url = ics_url

    def upcoming(self, window: timedelta = timedelta(days=7)) -> List[CalendarEvent]:
        if not self.ics_url:
            return self._fallback()

        try:
            response = requests.get(self.ics_url, timeout=10)
            response.raise_for_status()
            cal = Calendar(response.text)
            now = datetime.now(cal.timezone) if cal.timezone else datetime.now()
            end = now + window

            events: List[CalendarEvent] = []
            for event in cal.events:
                if event.begin is None or event.end is None:
                    continue
                start_dt = event.begin.datetime
                end_dt = event.end.datetime
                if start_dt > end:
                    continue
                if end_dt < now:
                    continue
                events.append(
                    CalendarEvent(
                        title=event.name or "Untitled Event",
                        start=start_dt,
                        end=end_dt,
                    )
                )

            events.sort(key=lambda ev: ev.start)
            return events[:5]
        except Exception:
            return self._fallback()

    def _fallback(self) -> List[CalendarEvent]:
        now = datetime.now()
        return [
            CalendarEvent(
                title="Team Standup (offline)",
                start=now + timedelta(hours=1),
                end=now + timedelta(hours=2),
            )
        ]
