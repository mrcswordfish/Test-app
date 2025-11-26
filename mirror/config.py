import os
from dataclasses import dataclass
from typing import Optional


def _env(key: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(key)
    return value if value not in {None, ""} else default


@dataclass
class WeatherConfig:
    api_key: Optional[str]
    location: str
    units: str = "metric"


@dataclass
class CalendarConfig:
    ics_url: Optional[str]


@dataclass
class BCTransitConfig:
    api_key: Optional[str]
    region: Optional[str]
    stop_id: Optional[str]


@dataclass
class VoiceAssistantConfig:
    language: str = "en-CA"
    wake_phrase: str = "hey mirror"
    tts_backend: str = "pyttsx3"  # options: "pyttsx3" (offline) or "openai"
    openai_api_key: Optional[str] = None
    openai_voice: str = "alloy"
    openai_model: str = "gpt-4o-mini-tts"


@dataclass
class MotionConfig:
    enabled: bool = True
    gpio_pin: int = 17
    absence_cooldown: int = 45  # seconds after last motion to switch to slideshow


@dataclass
class SlideshowConfig:
    image_dir: str = "slides"
    interval_seconds: int = 30


@dataclass
class MediaConfig:
    video_player: str = "mpv"
    audio_player: str = "mpv"
    default_music_query: str = "lofi hip hop radio"
    default_video_query: str = "news livestream"


@dataclass
class AstronomyConfig:
    location: Optional[str] = None


@dataclass
class AuroraConfig:
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass
class MirrorConfig:
    weather: WeatherConfig
    calendar: CalendarConfig
    transit: BCTransitConfig
    voice: VoiceAssistantConfig
    motion: MotionConfig
    slideshow: SlideshowConfig
    media: MediaConfig
    astronomy: AstronomyConfig
    aurora: AuroraConfig
    refresh_seconds: int = 60

    @classmethod
    def from_env(cls) -> "MirrorConfig":
        aurora_lat = _env("AURORA_LAT")
        aurora_lon = _env("AURORA_LON")

        return cls(
            weather=WeatherConfig(
                api_key=_env("OPENWEATHER_API_KEY"),
                location=_env("WEATHER_LOCATION", "Victoria,CA"),
                units=_env("WEATHER_UNITS", "metric"),
            ),
            calendar=CalendarConfig(ics_url=_env("CALENDAR_ICS_URL")),
            transit=BCTransitConfig(
                api_key=_env("BC_TRANSIT_API_KEY"),
                region=_env("BC_TRANSIT_REGION"),
                stop_id=_env("BC_TRANSIT_STOP_ID"),
            ),
            voice=VoiceAssistantConfig(
                language=_env("VOICE_ASSISTANT_LANG", "en-CA") or "en-CA",
                wake_phrase=_env("VOICE_ASSISTANT_WAKE", "hey mirror") or "hey mirror",
                tts_backend=_env("VOICE_TTS_BACKEND", "pyttsx3") or "pyttsx3",
                openai_api_key=_env("OPENAI_API_KEY"),
                openai_voice=_env("VOICE_TTS_VOICE", "alloy") or "alloy",
                openai_model=_env("VOICE_TTS_MODEL", "gpt-4o-mini-tts") or "gpt-4o-mini-tts",
            ),
            motion=MotionConfig(
                enabled=_env("MOTION_ENABLED", "true").lower() != "false",
                gpio_pin=int(_env("MOTION_GPIO_PIN", "17")),
                absence_cooldown=int(_env("MOTION_ABSENCE_COOLDOWN", "45")),
            ),
            slideshow=SlideshowConfig(
                image_dir=_env("SLIDESHOW_DIR", "slides") or "slides",
                interval_seconds=int(_env("SLIDESHOW_INTERVAL", "30")),
            ),
            media=MediaConfig(
                video_player=_env("MEDIA_VIDEO_PLAYER", "mpv") or "mpv",
                audio_player=_env("MEDIA_AUDIO_PLAYER", "mpv") or "mpv",
                default_music_query=_env("MEDIA_DEFAULT_MUSIC", "lofi hip hop radio")
                or "lofi hip hop radio",
                default_video_query=_env("MEDIA_DEFAULT_VIDEO", "news livestream")
                or "news livestream",
            ),
            astronomy=AstronomyConfig(location=_env("ASTRONOMY_LOCATION")),
            aurora=AuroraConfig(
                latitude=float(aurora_lat) if aurora_lat else None,
                longitude=float(aurora_lon) if aurora_lon else None,
            ),
            refresh_seconds=int(_env("REFRESH_SECONDS", "60")),
        )
