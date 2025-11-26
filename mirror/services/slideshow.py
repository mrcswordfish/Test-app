from __future__ import annotations

import itertools
import time
from pathlib import Path


class SlideshowService:
    def __init__(self, directory: str, interval_seconds: int = 30) -> None:
        self.directory = Path(directory)
        self.interval_seconds = interval_seconds
        self._images = self._discover_images()
        self._cycle = itertools.cycle(self._images) if self._images else itertools.cycle([None])
        self._current: str | None = None
        self._last_change = 0.0

    def _discover_images(self) -> list[str]:
        if not self.directory.exists():
            return []
        supported = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
        return [str(path) for path in sorted(self.directory.iterdir()) if path.suffix.lower() in supported]

    def next_image(self) -> str | None:
        now = time.time()
        if self._current is None or now - self._last_change >= self.interval_seconds:
            self._current = next(self._cycle)
            self._last_change = now
        return self._current

    def has_images(self) -> bool:
        return bool(self._images)


__all__ = ["SlideshowService"]
