"""Wall-clock source independent of any graphics library.

Replaces `pygame.time.Clock` / `pygame.time.get_ticks()`, which have no
MLX equivalent at all — frame pacing under MLX is entirely the caller's
own responsibility. Domain code (entities, game rules) must receive time
as an explicit parameter rather than reading this clock directly, the
same convention `Ghost.update(current_time, maze)` already follows.
"""

from __future__ import annotations

import time
from collections.abc import Callable


class ProjectClock:
    """Simulation timestamps and frame-rate limiting via `time.monotonic()`."""

    def __init__(
        self,
        monotonic: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._monotonic = monotonic
        self._sleep = sleep
        self._start = monotonic()
        self._last_tick = self._start
        self._pause_started: float | None = None
        self._paused_seconds = 0.0

    def get_ticks_ms(self) -> int:
        """Milliseconds elapsed in gameplay simulation time."""
        now = (
            self._pause_started
            if self._pause_started is not None
            else self._monotonic()
        )
        return int((now - self._start - self._paused_seconds) * 1000)

    def pause(self) -> None:
        """Freeze simulation time while UI events and rendering continue."""
        if self._pause_started is None:
            self._pause_started = self._monotonic()

    def resume(self) -> None:
        """Resume simulation time without charging the pause duration."""
        if self._pause_started is not None:
            self._paused_seconds += self._monotonic() - self._pause_started
            self._pause_started = None

    def tick(self, fps: int) -> int:
        """Sleep as needed to cap the frame rate at `fps`."""
        target_dt = 1.0 / fps if fps > 0 else 0.0
        now = self._monotonic()
        elapsed = now - self._last_tick
        if target_dt and elapsed < target_dt:
            self._sleep(target_dt - elapsed)
            now = self._monotonic()
            elapsed = now - self._last_tick
        self._last_tick = now
        return int(elapsed * 1000)
