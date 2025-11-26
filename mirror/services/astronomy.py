from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import floor
from typing import Optional


@dataclass
class AstronomySummary:
    moon_phase: str
    illumination_pct: float
    earth_image: str
    moon_image: str
    updated_at: datetime

    def format_brief(self) -> str:
        illum = f"{self.illumination_pct:.0f}% lit"
        return f"Moon: {self.moon_phase} ({illum})"


class AstronomyService:
    """Lightweight moon phase calculator with static 3D Earth/Moon imagery."""

    def __init__(self, location: Optional[str] = None) -> None:
        self.location = location

    def fetch(self) -> AstronomySummary:
        try:
            now = datetime.now(timezone.utc)
            phase_name, illumination = self._compute_moon(now)
            return AstronomySummary(
                moon_phase=phase_name,
                illumination_pct=illumination,
                earth_image="https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=1200&q=80",
                moon_image="https://images.unsplash.com/photo-1445905595283-21f8ae8a33d2?auto=format&fit=crop&w=900&q=80",
                updated_at=now,
            )
        except Exception:
            return self._fallback()

    def _fallback(self) -> AstronomySummary:
        now = datetime.now(timezone.utc)
        return AstronomySummary(
            moon_phase="Waxing gibbous (offline)",
            illumination_pct=78.0,
            earth_image="https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=1200&q=80",
            moon_image="https://images.unsplash.com/photo-1445905595283-21f8ae8a33d2?auto=format&fit=crop&w=900&q=80",
            updated_at=now,
        )

    def _compute_moon(self, now: datetime) -> tuple[str, float]:
        # Meeus/Jenkin's method approximation for moon phase and illumination
        diff = now - datetime(2001, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        days = diff.total_seconds() / 86400
        lunations = days / 29.53058867
        pos = lunations % 1
        index = floor(pos * 8 + 0.5)
        phase_names = [
            "New moon",
            "Waxing crescent",
            "First quarter",
            "Waxing gibbous",
            "Full moon",
            "Waning gibbous",
            "Last quarter",
            "Waning crescent",
        ]
        phase_name = phase_names[index % 8]
        illumination = (1 - abs(2 * pos - 1)) * 100
        return phase_name, illumination


__all__ = ["AstronomyService", "AstronomySummary"]
