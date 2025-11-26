from __future__ import annotations

from datetime import datetime
from typing import Iterable

from ..services.astronomy import AstronomySummary
from ..services.aurora import AuroraForecast
from ..services.bc_transit import TransitPrediction
from ..services.calendar import CalendarEvent
from ..services.weather import WeatherSummary


class DisplayRenderer:
    """Simple console renderer. Swap with a GUI/HTML renderer for the real mirror."""

    def render(
        self,
        weather: WeatherSummary,
        events: Iterable[CalendarEvent],
        predictions: Iterable[TransitPrediction],
        astronomy: AstronomySummary,
        aurora: AuroraForecast,
        presence: bool = True,
        slide: str | None = None,
    ) -> None:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        mode = "FULL" if presence else "AMBIENT SLIDESHOW"
        print("\n=== SMART MIRROR DASHBOARD (Portrait) ===")
        print(f"Updated: {now} | Mode: {mode}")
        print(
            f"Weather: {weather.format_brief()} | Humidity {weather.humidity}% | Wind {weather.wind_kph:.0f} kph"
        )
        print(astronomy.format_brief())
        print(f"Aurora: {aurora.format_brief()}")

        print("\nNext events:")
        for event in events:
            print(f" - {event.format_brief()}")

        print("\nBC Transit:")
        for pred in predictions:
            print(f" - {pred.format_brief()}")

        if not presence:
            print("\nAmbient slideshow (fullscreen, widgets minimized):")
            print(f" - {slide or 'No images found; add files to the slideshow directory.'}")

        print("==============================\n")


__all__ = ["DisplayRenderer"]
