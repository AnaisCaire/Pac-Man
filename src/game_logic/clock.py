"""Wall-clock source independent of any graphics library.

Replaces `pygame.time.Clock` / `pygame.time.get_ticks()`, which have no
MLX equivalent at all — frame pacing under MLX is entirely the caller's
own responsibility. Domain code (entities, game rules) must receive time
as an explicit parameter rather than reading this clock directly, the
same convention `Ghost.update(current_time, maze)` already follows.
"""

from __future__ import annotations

import time


class ProjectClock:
    """Millisecond timestamps and frame-rate limiting via `time.monotonic()`."""

    def __init__(self) -> None:
        self._start = time.monotonic()
        self._last_tick = self._start

    def get_ticks_ms(self) -> int:
        """Milliseconds elapsed since this clock was created."""
        return int((time.monotonic() - self._start) * 1000)

    def tick(self, fps: int) -> int:
        """Sleep as needed to cap the frame rate at `fps`.

        Returns the elapsed time in milliseconds since the previous call,
        mirroring `pygame.time.Clock.tick()`.
        """
        target_dt = 1.0 / fps if fps > 0 else 0.0
        now = time.monotonic()
        elapsed = now - self._last_tick
        if target_dt and elapsed < target_dt:
            time.sleep(target_dt - elapsed)
            now = time.monotonic()
            elapsed = now - self._last_tick
        self._last_tick = now
        return int(elapsed * 1000)
