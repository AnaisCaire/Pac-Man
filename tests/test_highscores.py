"""Highscore persistence contracts independent of Pygame."""

from __future__ import annotations

import tempfile
import unittest
import json
from pathlib import Path

from src.scores.model import ScoreEntry
from src.scores.scores_utils import (
    load_highscores,
    rank_scores,
    record_score,
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

    def test_equal_scores_use_a_case_sensitive_final_tiebreaker(self) -> None:
        first = rank_scores([ScoreEntry("a", 10), ScoreEntry("A", 10)])
        second = rank_scores([ScoreEntry("A", 10), ScoreEntry("a", 10)])

        self.assertEqual(first, second)
        self.assertEqual([entry.name for entry in first], ["A", "a"])

    def test_missing_or_malformed_file_recovers_to_empty_scores(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scores.json"
            self.assertEqual(load_highscores(path), [])
            path.write_text("not json", encoding="utf-8")
            self.assertEqual(load_highscores(path), [])

    def test_save_round_trip_uses_configured_data_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            data_dir = Path(directory)
            path = data_dir / "scores" / "high_scores.json"
            scores = [ScoreEntry("Ana", 100), ScoreEntry("Mario", 50)]

            self.assertTrue(save_highscores(path, scores))
            self.assertEqual(load_highscores(path), scores)
            self.assertTrue(path.is_file())

    def test_configured_path_is_used_exactly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            data_dir = Path(directory)

            self.assertEqual(
                resolve_highscore_path("scores/high_scores.json", data_dir),
                Path("scores/high_scores.json"),
            )
            self.assertEqual(
                resolve_highscore_path("../escaped.json", data_dir),
                Path("../escaped.json"),
            )

    def test_load_preserves_file_order_and_update_replaces_same_name(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scores.json"
            path.write_text(json.dumps({"highscores": [
                {"name": "Mario", "score": 10},
                {"name": "Ana", "score": 100},
            ]}), encoding="utf-8")

            self.assertEqual(
                [entry.name for entry in load_highscores(path)],
                ["Mario", "Ana"],
            )
            scores = record_score(path, ScoreEntry("Mario", 200))

            self.assertIsNotNone(scores)
            assert scores is not None
            self.assertEqual([(entry.name, entry.score) for entry in scores], [
                ("Mario", 200),
                ("Ana", 100),
            ])

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
