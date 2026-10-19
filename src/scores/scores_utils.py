"""Atomic, Pygame-independent persistence for the Top 10 highscores."""

from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path
import sys

from .model import ScoreEntry

_MAX_SCORES = 10
logger = logging.getLogger(__name__)


def resolve_highscore_path(filename: str) -> Path:
    """Resolve relative packaged scores beneath a writable user-data directory."""
    path = Path(filename)
    if not getattr(sys, "frozen", False) or path.is_absolute():
        return path
    if sys.platform == "win32":
        data_root = Path(
            os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")
        ) / "Pac-Man"
    else:
        data_root = Path(
            os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
        ) / "pacman"
    return data_root / path


def rank_scores(scores: list[ScoreEntry]) -> list[ScoreEntry]:
    """Return a deterministic Top 10 sorted by score then player name."""
    return sorted(
        scores,
        key=lambda entry: (-entry.score, entry.name.casefold(), entry.name),
    )[:_MAX_SCORES]


def load_highscores(path: Path) -> list[ScoreEntry]:
    """Load valid entries, recovering safely from absent or corrupt storage."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        raw_scores = data["highscores"]
        if not isinstance(raw_scores, list):
            logger.warning(
                "invalid highscore list in %s; using an empty board",
                path,
            )
            return []
    except FileNotFoundError:
        return []
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
        logger.warning(
            "cannot load highscores from %s: %s; using an empty board",
            path,
            error,
        )
        return []

    scores: list[ScoreEntry] = []
    for raw_score in raw_scores:
        if not isinstance(raw_score, dict):
            continue
        try:
            scores.append(ScoreEntry(raw_score["name"], raw_score["score"]))
        except (KeyError, TypeError, ValueError):
            continue
    return scores


def save_highscores(path: Path, scores: list[ScoreEntry]) -> bool:
    """Atomically save the validated Top 10 without destroying prior data."""
    payload = {
        "highscores": [
            {"name": entry.name, "score": entry.score}
            for entry in rank_scores(scores)
        ]
    }
    temporary_path: Path | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            text=True,
        )
        temporary_path = Path(temporary_name)
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            json.dump(payload, output, separators=(",", ":"))
        temporary_path.replace(path)
        return True
    except OSError:
        return False
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass


def record_score(path: Path, entry: ScoreEntry) -> list[ScoreEntry] | None:
    """Persist one submitted score and return the resulting board on success."""
    scores = {score.name: score for score in load_highscores(path)}
    scores[entry.name] = entry
    ranked = rank_scores(list(scores.values()))
    return ranked if save_highscores(path, ranked) else None
