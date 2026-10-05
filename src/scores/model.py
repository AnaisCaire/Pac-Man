"""Pygame-independent highscore value objects."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreEntry:
    """One validated score submitted by a player."""

    name: str
    score: int

    def __post_init__(self) -> None:
        normalized = self.name.strip()
        if not normalized or len(normalized) > 10:
            raise ValueError("name must contain 1 to 10 characters")
        if not normalized.isascii() or not all(
            character.isalnum() or character == " " for character in normalized
        ):
            raise ValueError("name must contain only letters, numbers, and spaces")
        if type(self.score) is not int or self.score < 0:
            raise ValueError("score must be a non-negative integer")
        object.__setattr__(self, "name", normalized)
