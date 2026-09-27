import pathlib
import sys

import pygame

_SOUNDS_DIR = pathlib.Path(__file__).parent / "sounds"

# Original review note: check for more original-game audio so we can use it in
# matching situations.
# Post-fix: keep only menu/game tracks until matching assets and call sites are
# added deliberately.
_TRACKS = {
    "menu": ["menu.ogg", "menu.mp3", "menu.wav"],
    "game": ["game.ogg", "game.mp3", "game.wav"],
}


def _find_track(name: str) -> pathlib.Path | None:
    for filename in _TRACKS[name]:
        path = _SOUNDS_DIR / filename
        if path.exists():
            return path
    return None


class MusicManager:
    """Optional background-music adapter with silent fallback.

    `pygame.mixer` is an audio subsystem, not part of the MLX-equivalence
    graphics decision. When the host has no usable audio device, or a track
    cannot be loaded/played, this adapter warns once and becomes a no-op so
    menus and gameplay keep running.
    """

    def __init__(self, enabled: bool = True) -> None:
        self._enabled = enabled
        self._warned = False
        self._current: str | None = None

    @classmethod
    def initialize(cls) -> "MusicManager":
        """Initialize the mixer when possible, otherwise return silent audio."""
        manager = cls()
        try:
            pygame.mixer.init()
        except pygame.error as error:
            manager._disable(str(error))
        return manager

    def _disable(self, reason: str) -> None:
        """Switch to silent mode and emit the single allowed audio warning."""
        self._enabled = False
        self._current = None
        if not self._warned:
            print(f"WARNING: audio unavailable: {reason}", file=sys.stderr)
            self._warned = True

    def play(self, name: str) -> None:
        """Switch tracks, doing nothing if active or unavailable."""
        if not self._enabled:
            return
        if name == self._current:
            return
        path = _find_track(name)
        if path is None:
            return
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.play(-1)
            self._current = name
        except pygame.error as error:
            self._disable(str(error))

    def stop(self) -> None:
        """Stop current music when audio is active; ignore mixer failures."""
        if not self._enabled:
            return
        try:
            pygame.mixer.music.stop()
        except pygame.error as error:
            self._disable(str(error))
        self._current = None
