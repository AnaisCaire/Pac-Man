"""Command-line contract tests for the Pac-Man entry point."""

from __future__ import annotations

import os
from pathlib import Path
import runpy
import subprocess
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
ENTRY_POINT = ROOT / "pac-man.py"


class CommandLineTests(unittest.TestCase):
    """Exercise the public CLI without opening a game window."""

    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        """Run the entry point with a headless SDL configuration."""
        environment = os.environ.copy()
        environment["SDL_AUDIODRIVER"] = "dummy"
        environment["SDL_VIDEODRIVER"] = "dummy"
        return subprocess.run(
            [sys.executable, str(ENTRY_POINT), *arguments],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

    def test_help_documents_the_configuration_argument(self) -> None:
        """The standard help flag explains the required positional file."""
        result = self.run_cli("--help")

        self.assertEqual(result.returncode, 0)
        self.assertIn("usage: pac-man.py", result.stdout)
        self.assertIn("configuration file", result.stdout.lower())
        self.assertNotIn("pygame-ce", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_missing_configuration_argument_is_a_clean_usage_error(self) -> None:
        """No argument must fail clearly without a Python traceback."""
        result = self.run_cli()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("usage: pac-man.py", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_extra_argument_is_a_clean_usage_error(self) -> None:
        """More than one path must fail clearly without a traceback."""
        result = self.run_cli("config.json", "extra.json")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("usage: pac-man.py", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_non_json_configuration_path_is_a_clean_usage_error(self) -> None:
        """The subject launch contract expects a JSON configuration file."""
        result = self.run_cli("config.txt")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("configuration file must end with .json", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_valid_argument_starts_the_game_with_parsed_configuration(self) -> None:
        """A valid positional path is passed through to the game loop."""
        namespace = runpy.run_path(str(ENTRY_POINT), run_name="pacman_cli")
        main = namespace["main"]
        configuration = object()

        with (
            patch.dict(os.environ, {"PYGAME_HIDE_SUPPORT_PROMPT": "1"}),
            patch("src.parse_config", return_value=configuration) as parse_config,
            patch("src.game_loop") as game_loop,
        ):
            main(["custom.json"])

        parse_config.assert_called_once_with("custom.json")
        game_loop.assert_called_once_with(configuration)


if __name__ == "__main__":
    unittest.main()
