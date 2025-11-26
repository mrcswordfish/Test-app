from __future__ import annotations

import re
import subprocess
from typing import List


class MediaController:
    """Minimal media launcher for YouTube videos or music via mpv (or any player).

    The controller keeps things simple by shelling out to an external player that
    already supports YouTube playback (mpv does through yt-dlp). On the Pi, make
    sure `mpv` and `yt-dlp` are installed via apt.
    """

    def __init__(
        self,
        video_player: str = "mpv",
        audio_player: str = "mpv",
        default_music_query: str = "lofi hip hop radio",
        default_video_query: str = "news livestream",
    ) -> None:
        self.video_player = video_player
        self.audio_player = audio_player
        self.default_music_query = default_music_query
        self.default_video_query = default_video_query

    def play_youtube(self, query_or_url: str, video: bool = True) -> None:
        target = self._normalize_target(query_or_url)
        cmd: List[str] = [self.video_player, "--fs", "--no-terminal", target] if video else [
            self.audio_player,
            "--no-video",
            "--no-terminal",
            target,
        ]
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def play_music(self, query_or_url: str | None = None) -> None:
        self.play_youtube(query_or_url or self.default_music_query, video=False)

    def play_video(self, query_or_url: str | None = None) -> None:
        self.play_youtube(query_or_url or self.default_video_query, video=True)

    def _normalize_target(self, value: str) -> str:
        value = value.strip()
        if self._looks_like_url(value):
            return value
        # mpv can resolve ytdl search with this scheme
        return f"ytdl://ytsearch:{value}"

    def _looks_like_url(self, text: str) -> bool:
        return bool(re.match(r"https?://", text))


__all__ = ["MediaController"]
