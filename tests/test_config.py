"""Configuration parsing contract tests."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.game_logic.config import Config, parse_config


class ConfigParsingTests(unittest.TestCase):
    """Exercise commented JSON parsing and per-field recovery."""

    def parse_text(self, text: str, filename: str = "config.json") -> Config:
        """Write a temporary config file and parse it through the public seam."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / filename
            path.write_text(text, encoding="utf-8")
            return parse_config(str(path))

    def test_valid_commented_config_preserves_hash_inside_strings(self) -> None:
        """Only full-line comments are stripped before JSON parsing."""
        config = self.parse_text(
            """
            # full-line comment
            {
              "highscore_filename": "scores/#hash.json",
              "level": [{"width": 16, "height": 17}],
              "lives": 5,
              "pacgum": 24,
              "points_per_pacgum": 11,
              "points_per_super_pacgum": 55,
              "points_per_ghost": 250,
              "seed": 99,
              "level_max_time": 120
            }
            """
        )

        self.assertEqual(config.highscore_filename, "scores/#hash.json")
        self.assertEqual(config.level[0].width, 16)
        self.assertEqual(config.level[0].height, 17)
        self.assertEqual(config.lives, 5)
        self.assertEqual(config.pacgum, 24)
        self.assertEqual(config.points_per_pacgum, 11)
        self.assertEqual(config.points_per_super_pacgum, 55)
        self.assertEqual(config.points_per_ghost, 250)
        self.assertEqual(config.seed, 99)
        self.assertEqual(config.level_max_time, 120)

    def test_unknown_keys_do_not_discard_valid_known_values(self) -> None:
        """Unknown top-level and level keys are ignored independently."""
        config = self.parse_text(
            json.dumps({
                "lives": 7,
                "unknown": "ignored",
                "level": [{"width": 19, "height": 20, "theme": "ignored"}],
            })
        )

        self.assertEqual(config.lives, 7)
        self.assertEqual(config.level[0].width, 19)
        self.assertEqual(config.level[0].height, 20)

    def test_invalid_fields_fall_back_independently(self) -> None:
        """Bad fields use safe defaults without losing valid sibling values."""
        with self.assertLogs("src.game_logic.config", level="WARNING") as logs:
            config = self.parse_text(
                json.dumps({
                    "highscore_filename": None,
                    "lives": True,
                    "pacgum": -1,
                    "points_per_pacgum": -5,
                    "points_per_super_pacgum": False,
                    "points_per_ghost": -9,
                    "seed": False,
                    "level_max_time": 3,
                    "level": [
                        {"width": 3, "height": "bad"},
                        "not an object",
                        {"width": 21, "height": 22},
                    ],
                })
            )

        defaults = Config()
        self.assertEqual(config.highscore_filename, defaults.highscore_filename)
        self.assertEqual(config.lives, defaults.lives)
        self.assertEqual(config.pacgum, defaults.pacgum)
        self.assertEqual(config.points_per_pacgum, defaults.points_per_pacgum)
        self.assertEqual(
            config.points_per_super_pacgum,
            defaults.points_per_super_pacgum,
        )
        self.assertEqual(config.points_per_ghost, defaults.points_per_ghost)
        self.assertEqual(config.seed, defaults.seed)
        self.assertEqual(config.level_max_time, defaults.level_max_time)
        self.assertEqual([(level.width, level.height) for level in config.level], [
            (15, 15),
            (15, 15),
            (21, 22),
        ])
        self.assertGreaterEqual(len(logs.output), 8)

    def test_malformed_json_root_and_missing_file_use_defaults(self) -> None:
        """Unreadable or structurally invalid config files recover cleanly."""
        defaults = Config()

        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing.json"
            with self.assertLogs("src.game_logic.config", level="WARNING"):
                missing_config = parse_config(str(missing))

        with self.assertLogs("src.game_logic.config", level="WARNING"):
            malformed_config = self.parse_text("{bad json")
        with self.assertLogs("src.game_logic.config", level="WARNING"):
            list_root_config = self.parse_text("[]")

        self.assertEqual(missing_config, defaults)
        self.assertEqual(malformed_config, defaults)
        self.assertEqual(list_root_config, defaults)

    def test_unreadable_file_and_non_json_extension_use_defaults(self) -> None:
        """I/O failures and wrong extensions are reported without tracebacks."""
        defaults = Config()

        with self.assertLogs("src.game_logic.config", level="WARNING"):
            extension_config = self.parse_text("{}", filename="config.txt")

        with patch("pathlib.Path.open", side_effect=OSError("permission denied")):
            with self.assertLogs("src.game_logic.config", level="WARNING"):
                unreadable_config = parse_config("config.json")

        self.assertEqual(extension_config, defaults)
        self.assertEqual(unreadable_config, defaults)


if __name__ == "__main__":
    unittest.main()
