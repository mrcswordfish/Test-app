from __future__ import annotations

import time


class MotionController:
    """Simple motion helper that works with Raspberry Pi PIR sensors.

    Falls back to an always-present state when gpiozero isn't available so
    development on non-Pi hardware still works.
    """

    def __init__(
        self,
        gpio_pin: int = 17,
        absence_cooldown: int = 45,
        enabled: bool = True,
    ) -> None:
        self.enabled = enabled
        self.gpio_pin = gpio_pin
        self.absence_cooldown = absence_cooldown
        self._sensor = self._init_sensor(gpio_pin) if enabled else None
        self._last_motion = time.time()
        self._presence = True

    def _init_sensor(self, gpio_pin: int):  # type: ignore[no-untyped-def]
        try:
            from gpiozero import MotionSensor

            return MotionSensor(gpio_pin)
        except Exception:
            # On non-Pi hardware or when gpiozero isn't installed, degrade gracefully.
            return None

    def detect_presence(self) -> bool:
        if not self.enabled or self._sensor is None:
            self._presence = True
            return self._presence

        now = time.time()
        if getattr(self._sensor, "motion_detected", False):
            self._presence = True
            self._last_motion = now
        elif now - self._last_motion > self.absence_cooldown:
            self._presence = False

        return self._presence

    @property
    def is_present(self) -> bool:
        return self._presence


__all__ = ["MotionController"]
