from __future__ import annotations

import argparse
import time
from typing import Optional

from dotenv import load_dotenv

from .config import MirrorConfig
from .services.assistant import VoiceAssistant
from .services.astronomy import AstronomyService
from .services.aurora import AuroraService
from .services.bc_transit import BCTransitService
from .services.calendar import CalendarService
from .services.media import MediaController
from .services.motion import MotionController
from .services.slideshow import SlideshowService
from .services.weather import WeatherService
from .ui.display import DisplayRenderer


class MirrorApp:
    def __init__(self, config: MirrorConfig, enable_assistant: bool = True) -> None:
        self.config = config
        self.weather = WeatherService(
            api_key=config.weather.api_key,
            location=config.weather.location,
            units=config.weather.units,
        )
        self.calendar = CalendarService(config.calendar.ics_url)
        self.transit = BCTransitService(
            api_key=config.transit.api_key,
            region=config.transit.region,
            stop_id=config.transit.stop_id,
        )
        self.astronomy = AstronomyService(location=config.astronomy.location)
        self.aurora = AuroraService(
            latitude=config.aurora.latitude, longitude=config.aurora.longitude
        )
        self.motion = MotionController(
            gpio_pin=config.motion.gpio_pin,
            absence_cooldown=config.motion.absence_cooldown,
            enabled=config.motion.enabled,
        )
        self.slideshow = SlideshowService(
            directory=config.slideshow.image_dir,
            interval_seconds=config.slideshow.interval_seconds,
        )
        self.media = MediaController(
            video_player=config.media.video_player,
            audio_player=config.media.audio_player,
            default_music_query=config.media.default_music_query,
            default_video_query=config.media.default_video_query,
        )
        self.renderer = DisplayRenderer()
        self.assistant: Optional[VoiceAssistant] = None
        if enable_assistant:
            self.assistant = VoiceAssistant(
                wake_phrase=config.voice.wake_phrase,
                language=config.voice.language,
                weather=self.weather,
                calendar=self.calendar,
                transit=self.transit,
                media=self.media,
                astronomy=self.astronomy,
                aurora=self.aurora,
                on_error=lambda exc: print(f"[assistant] {exc}"),
                tts_backend=config.voice.tts_backend,
                openai_api_key=config.voice.openai_api_key,
                openai_voice=config.voice.openai_voice,
                openai_model=config.voice.openai_model,
            )

    def run_once(self) -> None:
        presence = self.motion.detect_presence()
        slide = None if presence else self.slideshow.next_image()
        weather = self.weather.fetch()
        events = self.calendar.upcoming()
        predictions = self.transit.predictions()
        astronomy = self.astronomy.fetch()
        aurora = self.aurora.fetch()
        self.renderer.render(
            weather,
            events,
            predictions,
            astronomy,
            aurora,
            presence=presence,
            slide=slide,
        )

    def run_forever(self) -> None:
        if self.assistant:
            self.assistant.start()
        try:
            while True:
                self.run_once()
                time.sleep(self.config.refresh_seconds)
        finally:
            if self.assistant:
                self.assistant.stop()


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Run the Smart Mirror application")
    parser.add_argument("--once", action="store_true", help="Refresh once and exit")
    parser.add_argument("--no-voice", action="store_true", help="Disable the voice assistant")
    args = parser.parse_args()

    config = MirrorConfig.from_env()
    app = MirrorApp(config=config, enable_assistant=not args.no_voice and not args.once)

    if args.once:
        app.run_once()
    else:
        app.run_forever()


if __name__ == "__main__":
    main()
