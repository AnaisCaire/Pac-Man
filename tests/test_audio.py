"""Audio adapter tests for optional music playback."""

from __future__ import annotations

from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from typing import cast
import unittest
from unittest.mock import patch

import pygame

from src.game_logic.config import Config
from src.game_logic.game_engine import game_loop
from src.ui.music_manager import MusicManager


class MusicManagerTests(unittest.TestCase):
    """Protect graceful silent fallback around pygame.mixer."""

    def test_mixer_init_failure_warns_once_and_plays_silently(self) -> None:
        """A missing audio device must not crash startup or later play calls."""
        stderr = StringIO()

        with (
            patch("pygame.mixer.init", side_effect=pygame.error("no device")),
            patch("pygame.mixer.music.load") as load,
            redirect_stderr(stderr),
        ):
            music = MusicManager.initialize()
            music.play("menu")
            music.play("game")

        self.assertIn("WARNING: audio unavailable: no device", stderr.getvalue())
        self.assertEqual(stderr.getvalue().count("WARNING: audio unavailable"), 1)
        self.assertNotIn("Traceback", stderr.getvalue())
        load.assert_not_called()

    def test_game_loop_continues_past_audio_init_failure(self) -> None:
        """Game startup delegates mixer failure to the silent audio adapter."""
        stderr = StringIO()

        with (
            patch("pygame.init"),
            patch("pygame.mixer.init", side_effect=pygame.error("no device")),
            patch("pygame.display.set_mode"),
            patch("pygame.display.set_caption"),
            patch(
                "src.game_logic.game_engine.MainMenu",
                side_effect=RuntimeError("started"),
            ),
            redirect_stderr(stderr),
        ):
            with self.assertRaisesRegex(RuntimeError, "started"):
                game_loop(cast(Config, SimpleNamespace(lives=3)))

        self.assertIn("WARNING: audio unavailable: no device", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_available_audio_loads_and_loops_track(self) -> None:
        """When mixer setup works, the selected track is loaded and looped."""
        with (
            patch("pygame.mixer.init") as init,
            patch("src.ui.music_manager._find_track", return_value=Path("menu.ogg")),
            patch("pygame.mixer.music.load") as load,
            patch("pygame.mixer.music.play") as play,
        ):
            music = MusicManager.initialize()
            music.play("menu")

        init.assert_called_once_with()
        load.assert_called_once_with("menu.ogg")
        play.assert_called_once_with(-1)

    def test_load_failure_warns_once_and_disables_audio(self) -> None:
        """Bad or corrupt audio assets degrade to later silent no-op playback."""
        stderr = StringIO()

        with (
            patch("pygame.mixer.init"),
            patch("src.ui.music_manager._find_track", return_value=Path("bad.ogg")),
            patch(
                "pygame.mixer.music.load",
                side_effect=pygame.error("bad file"),
            ) as load,
            redirect_stderr(stderr),
        ):
            music = MusicManager.initialize()
            music.play("menu")
            music.play("game")

        self.assertIn("WARNING: audio unavailable: bad file", stderr.getvalue())
        self.assertEqual(stderr.getvalue().count("WARNING: audio unavailable"), 1)
        self.assertNotIn("Traceback", stderr.getvalue())
        load.assert_called_once_with("bad.ogg")


if __name__ == "__main__":
    unittest.main()
