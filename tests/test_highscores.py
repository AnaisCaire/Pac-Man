"""Highscore persistence contracts independent of Pygame."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.scores.model import ScoreEntry
from src.scores.scores_utils import (
    load_highscores,
    rank_scores,
    resolve_highscore_path,
    save_highscores,
)


class HighscoreTests(unittest.TestCase):
    """Persist only valid deterministic Top 10 entries."""

    def test_entries_validate_name_and_non_negative_score(self) -> None:
        self.assertEqual(ScoreEntry(" Ana 42 ", 42).name, "Ana 42")
        with self.assertRaises(ValueError):
            ScoreEntry("", 1)
        with self.assertRaises(ValueError):
            ScoreEntry("too-long-name", 1)
        with self.assertRaises(ValueError):
            ScoreEntry("Ana!", 1)
        with self.assertRaises(ValueError):
            ScoreEntry("Ana", -1)
        with self.assertRaises(ValueError):
            ScoreEntry("Ana", True)

    def test_rank_is_deterministic_and_keeps_only_top_ten(self) -> None:
        scores = [ScoreEntry(f"P{i}", 100 if i < 2 else i) for i in range(12)]

        ranked = rank_scores(scores)

        self.assertEqual(len(ranked), 10)
        self.assertEqual([(entry.name, entry.score) for entry in ranked[:2]], [
            ("P0", 100),
            ("P1", 100),
        ])
        self.assertEqual(ranked[0].score, 100)
        self.assertGreaterEqual(ranked[-1].score, 2)

    def test_missing_or_malformed_file_recovers_to_empty_scores(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scores.json"
            self.assertEqual(load_highscores(path), [])
            path.write_text("not json", encoding="utf-8")
            self.assertEqual(load_highscores(path), [])

    def test_save_round_trip_uses_configured_data_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            data_dir = Path(directory)
            path = resolve_highscore_path("scores/high_scores.json", data_dir)
            scores = [ScoreEntry("Ana", 100), ScoreEntry("Mario", 50)]

            self.assertTrue(save_highscores(path, scores))
            self.assertEqual(load_highscores(path), scores)
            self.assertTrue(path.is_file())

    def test_failed_write_preserves_existing_scores(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scores.json"
            original = [ScoreEntry("Ana", 100)]
            self.assertTrue(save_highscores(path, original))
            blocked_path = path / "child.json"

            self.assertFalse(save_highscores(blocked_path, [ScoreEntry("Mario", 50)]))
            self.assertEqual(load_highscores(path), original)


if __name__ == "__main__":
    unittest.main()
