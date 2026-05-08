import pygame
import pathlib

_SOUNDS_DIR = pathlib.Path(__file__).parent / "sounds"

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
    """Handles background music switching between menu and gameplay."""

    def __init__(self) -> None:
        self._current = None

    def play(self, name: str) -> None:
        """Switch to the named track ('menu' or 'game'). No-op if already playing or file missing."""
        if name == self._current:
            return
        path = _find_track(name)
        if path is None:
            return
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.play(-1)
            self._current = name
        except pygame.error:
            pass

    def stop(self) -> None:
        pygame.mixer.music.stop()
        self._current = None
