from __future__ import annotations

import queue
import threading
import tempfile
from pathlib import Path
from typing import Callable, Optional

import pyttsx3
import simpleaudio as sa
import speech_recognition as sr
from openai import OpenAI

from .astronomy import AstronomyService
from .aurora import AuroraService
from .bc_transit import BCTransitService
from .calendar import CalendarService
from .media import MediaController
from .weather import WeatherService


class VoiceAssistant:
    """
    Lightweight voice assistant that listens for a wake phrase and answers
    a few mirror-specific intents.
    """

    def __init__(
        self,
        wake_phrase: str,
        language: str,
        weather: WeatherService,
        calendar: CalendarService,
        transit: BCTransitService,
        media: Optional[MediaController] = None,
        astronomy: Optional[AstronomyService] = None,
        aurora: Optional[AuroraService] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        tts_backend: str = "pyttsx3",
        openai_api_key: Optional[str] = None,
        openai_voice: str = "alloy",
        openai_model: str = "gpt-4o-mini-tts",
    ) -> None:
        self.wake_phrase = wake_phrase.lower()
        self.language = language
        self.recognizer = sr.Recognizer()
        self.tts_backend = tts_backend
        self.openai_api_key = openai_api_key
        self.openai_voice = openai_voice
        self.openai_model = openai_model
        self.tts_engine = self._init_tts_engine()
        self.weather = weather
        self.calendar = calendar
        self.transit = transit
        self.media = media
        self.astronomy = astronomy
        self.aurora = aurora
        self.on_error = on_error
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._phrase_queue: "queue.Queue[str]" = queue.Queue()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)

    def _run_loop(self) -> None:
        mic = sr.Microphone()
        with mic as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while not self._stop_event.is_set():
                try:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                except sr.WaitTimeoutError:
                    continue

                try:
                    phrase = self.recognizer.recognize_google(audio, language=self.language)
                    normalized = phrase.lower().strip()
                    if self.wake_phrase in normalized:
                        self._phrase_queue.put(normalized)
                        self.respond_to_command()
                except Exception as exc:  # speech recognition errors are common
                    if self.on_error:
                        self.on_error(exc)

    def respond_to_command(self) -> None:
        try:
            self.speak("I'm listening")
            phrase = self._phrase_queue.get(timeout=1)
            intent, payload = self._detect_intent(phrase)
            if intent == "weather":
                summary = self.weather.fetch()
                self.speak(summary.format_brief())
            elif intent == "bus":
                trips = self.transit.predictions()
                lines = ", ".join(pred.format_brief() for pred in trips)
                self.speak(f"Next departures: {lines}")
            elif intent == "agenda":
                events = self.calendar.upcoming()
                lines = "; ".join(ev.format_brief() for ev in events)
                self.speak(f"Upcoming: {lines}")
            elif intent == "moon" and self.astronomy:
                astro = self.astronomy.fetch()
                self.speak(astro.format_brief())
            elif intent == "aurora" and self.aurora:
                forecast = self.aurora.fetch()
                self.speak(forecast.format_brief())
            elif intent == "music" and self.media:
                self.media.play_music(payload)
                self.speak(f"Playing {payload or 'your music mix'}")
            elif intent == "video" and self.media:
                self.media.play_video(payload)
                self.speak(f"Playing {payload or 'a YouTube video'}")
            else:
                self.speak(
                    "Try asking for weather, next bus, agenda, moon phase, aurora, play music, or play a YouTube video."
                )
        except Exception as exc:
            if self.on_error:
                self.on_error(exc)

    def _detect_intent(self, phrase: str) -> tuple[str, Optional[str]]:
        lower = phrase.lower()
        if "weather" in phrase:
            return "weather", None
        if "bus" in phrase or "transit" in phrase:
            return "bus", None
        if "agenda" in phrase or "calendar" in phrase or "events" in phrase:
            return "agenda", None
        if "moon" in lower:
            return "moon", None
        if "aurora" in lower or "northern lights" in lower:
            return "aurora", None
        if "music" in lower or "song" in lower or "play" in lower:
            payload = self._extract_payload(lower, ["music", "song", "play"])
            return "music", payload
        if "youtube" in lower or "video" in lower:
            payload = self._extract_payload(lower, ["youtube", "video", "play"])
            return "video", payload
        return "unknown", None

    def _extract_payload(self, phrase: str, keywords: list[str]) -> Optional[str]:
        for key in keywords:
            if key in phrase:
                tail = phrase.split(key, 1)[1].strip()
                if tail:
                    return tail
        return None

    def speak(self, text: str) -> None:
        self.tts_engine(text)

    def _init_tts_engine(self) -> Callable[[str], None]:
        if self.tts_backend == "openai" and self.openai_api_key:
            client = OpenAI(api_key=self.openai_api_key)

            def speak_with_openai(text: str) -> None:
                response = client.audio.speech.create(
                    model=self.openai_model,
                    voice=self.openai_voice,
                    input=text,
                    response_format="wav",
                )
                audio_bytes = response.read()
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(audio_bytes)
                    temp_path = Path(tmp.name)
                wave_obj = sa.WaveObject.from_wave_file(str(temp_path))
                play_obj = wave_obj.play()
                play_obj.wait_done()
                temp_path.unlink(missing_ok=True)

            return speak_with_openai

        tts = pyttsx3.init()

        def speak_with_pyttsx3(text: str) -> None:
            tts.say(text)
            tts.runAndWait()

        return speak_with_pyttsx3


__all__ = ["VoiceAssistant"]
