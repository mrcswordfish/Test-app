# Smart Mirror for Raspberry Pi

This project provides a modular Python application for running an AI-enabled smart mirror on a Raspberry Pi. It includes weather, calendar, BC Transit schedule widgets, astronomy (Earth/Moon phases), northern lights forecast, motion-aware presentation, a portrait-first minimalist layout, and an extensible voice assistant. The code is designed to run headless for development (console output), but the render layer can be swapped for a GUI or display driver suited to your mirror hardware.

For a quick visual idea of the end result, open [`docs/dashboard_preview.html`](docs/dashboard_preview.html) in a browser. It now shows minimalist portrait frames for both presence (full module) and ambient slideshow layouts with Earth/Moon and aurora widgets overlaying a reflection-friendly background.

## Features
- Weather via OpenWeatherMap.
- Calendar using any public iCal/ICS feed (e.g., Google Calendar share link).
- BC Transit schedules through the BC Transit public API.
- Motion-aware display that switches between a full dashboard when someone is present and an ambient slideshow with minimized widgets when idle.
- Portrait-first, minimalist layout aimed at 32–42" panels with translucent text-only overlays that preserve your reflection (no bold text or heavy containers).
- Voice assistant hooks powered by speech recognition, text-to-speech, and voice-triggered YouTube video/music playback.
- Earth + Moon phase widget with 3D imagery references.
- Northern Lights (aurora) activity snapshot with Kp index and NOAA oval map link.
- Configuration through environment variables with sane defaults and graceful fallbacks when services are unavailable.

## Full installation guide (Raspberry Pi)
Follow these steps on a fresh Raspberry Pi OS Lite/Full image. Commands assume you are in the repo root.

1. **Update the OS and audio stack**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3-pip python3-venv portaudio19-dev libespeak1 ffmpeg mpv yt-dlp python3-gpiozero
   ```

2. **Create and activate a virtual environment** (keeps system Python clean)
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure the application**
   ```bash
   cp .env.example .env
   nano .env
   ```
   Populate:
   - `OPENWEATHER_API_KEY` and `WEATHER_LOCATION` (e.g., `Victoria,CA`).
   - `CALENDAR_ICS_URL` (public read-only ICS link).
   - `BC_TRANSIT_*` keys for your region/stop.
   - Voice options (see **Voice assistant** below). Save and exit.

5. **Test audio hardware**
   - Plug in your USB microphone and speaker/amp.
   - Verify capture: `arecord -l` and `arecord -D plughw:1,0 -d 3 test.wav`.
   - Verify playback: `aplay test.wav`.

6. **Run the mirror loop**
   ```bash
   python -m mirror
   ```
   The console renderer prints a dashboard snapshot every minute. Replace `DisplayRenderer` in `mirror/ui/display.py` with your own GUI for a physical mirror display.

7. **Enable on-boot launch (optional)**
   ```bash
   crontab -e
   # Add the line below and adjust the paths if needed:
   @reboot /home/pi/Test-app/.venv/bin/python -m mirror >> /home/pi/mirror.log 2>&1
   ```

## Portrait layout setup
- Use a portrait orientation on the Pi (`xrandr --output HDMI-1 --rotate right` on X11, or set `display_hdmi_rotate=3` in `/boot/config.txt` on newer Raspberry Pi OS releases).
- Keep the mirror background dark or translucent in your GUI renderer so you can still see your reflection, similar to the dashboard preview in `docs/dashboard_preview.html`.
- Target dimensions of 32–42" panels; scale fonts conservatively to avoid bold styles and retain readability at arm's length.

## Motion sensor and slideshow behavior
- A PIR motion sensor on GPIO 17 (default) keeps the dashboard in **full** mode when someone is present. After the cooldown (`MOTION_ABSENCE_COOLDOWN`), the mirror switches to an **ambient slideshow** where widgets shrink and your photos take the spotlight.
- Place slideshow images in the directory set by `SLIDESHOW_DIR` (default `slides/`). Supported formats: JPG, PNG, WEBP, BMP. The preview shows a full-screen slideshow with small overlay widgets for idle mode.
- If you're developing on a laptop or without the sensor installed, the app falls back to "always present" so you can iterate without hardware.

## Media playback with voice
- Install `mpv` and `yt-dlp` (see step 1) so the voice assistant can launch YouTube music or video. The defaults use `mpv`'s `ytdl://ytsearch:` scheme to resolve searches.
- Example commands after the wake phrase: "play music", "play relaxing piano", "play YouTube news", or "play the latest tech video".
- Defaults for the search queries can be set via `MEDIA_DEFAULT_MUSIC` and `MEDIA_DEFAULT_VIDEO`.

## Configuration
Environment variables (all optional but recommended):

| Variable | Purpose |
| --- | --- |
| `OPENWEATHER_API_KEY` | API key from https://openweathermap.org/ |
| `WEATHER_LOCATION` | City or `lat,lon` coordinate string (default: `Victoria,CA`). |
| `WEATHER_UNITS` | Units for OpenWeatherMap (`metric`, `imperial`). |
| `CALENDAR_ICS_URL` | Public ICS/ICAL feed URL for your calendar. |
| `BC_TRANSIT_API_KEY` | API key from BC Transit. |
| `BC_TRANSIT_REGION` | Region name used by BC Transit (e.g., `victoria`). |
| `BC_TRANSIT_STOP_ID` | Stop ID for predictions. |
| `VOICE_ASSISTANT_LANG` | Language code for speech recognition (default `en-CA`). |
| `VOICE_ASSISTANT_WAKE` | Wake phrase to listen for (default `"hey mirror"`). |
| `VOICE_TTS_BACKEND` | `pyttsx3` for offline TTS (default) or `openai` for ChatGPT voice. |
| `VOICE_TTS_MODEL` | OpenAI TTS model name (default `gpt-4o-mini-tts`). |
| `VOICE_TTS_VOICE` | OpenAI voice name (default `alloy`). |
| `OPENAI_API_KEY` | Required when `VOICE_TTS_BACKEND=openai`. |
| `MOTION_ENABLED` | Toggle motion sensor logic (default `true`). |
| `MOTION_GPIO_PIN` | GPIO pin for the PIR sensor (default `17`). |
| `MOTION_ABSENCE_COOLDOWN` | Seconds after last motion before the slideshow appears (default `45`). |
| `SLIDESHOW_DIR` | Directory containing slideshow images (default `slides`). |
| `SLIDESHOW_INTERVAL` | Seconds between slideshow images (default `30`). |
| `MEDIA_VIDEO_PLAYER` | Player command for video (default `mpv`). |
| `MEDIA_AUDIO_PLAYER` | Player command for audio-only playback (default `mpv`). |
| `MEDIA_DEFAULT_MUSIC` | Default search when you say "play music". |
| `MEDIA_DEFAULT_VIDEO` | Default search when you say "play video". |
| `ASTRONOMY_LOCATION` | Optional location label for the Earth/Moon widget. |
| `AURORA_LAT` / `AURORA_LON` | Optional coordinates to bias aurora updates (fallbacks to NOAA latest map). |

When data is unavailable (no API key or network), the services return static fallback content so the mirror keeps working.

## Voice assistant
`VoiceAssistant` listens for the wake phrase and responds to simple intents:
- "weather" → current conditions
- "next bus" → BC Transit predictions
- "agenda" → upcoming calendar items
- "moon" / "moon phase" → current lunar phase
- "aurora" / "northern lights" → current Kp/forecast summary
- "play music" / "play <artist or genre>" → launches an audio-only YouTube stream through your configured player
- "play video" / "play YouTube <topic>" → opens a fullscreen YouTube stream via your player

The default microphone and speaker are used; adjust `mirror/services/assistant.py` to integrate custom hardware like USB microphones or speakers on the Pi. Speech recognition uses the `SpeechRecognition` library (defaults to Google Web Speech).

### Using ChatGPT voice
- Set `VOICE_TTS_BACKEND=openai` in `.env`.
- Provide `OPENAI_API_KEY` (model defaults to `gpt-4o-mini-tts`, voice `alloy`).
- The assistant will synthesize replies with OpenAI text-to-speech instead of local pyttsx3. Leave `VOICE_TTS_BACKEND=pyttsx3` to stay fully offline.

## Extending
- Add new widgets under `mirror/services/`.
- Enrich the dashboard layout in `mirror/app.py` and `mirror/ui/display.py`.
- Replace the renderer with a GUI (e.g., PyQt, Kivy, Electron/HTML) targeting your mirror display.

## Development
Use `python -m mirror --once` to run a single refresh without the voice assistant loop. This helps while iterating on the UI without microphone hardware.

