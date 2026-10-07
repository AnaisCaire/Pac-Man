"""Evaluator (cheat) mode state for peer review.

Application-level state only: no pygame, no wall clock. The caller passes
`now` from `ProjectClock.get_ticks_ms()`; the input adapter decides which
key maps to which method.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .entities.ghosts import Ghost
    from .entities.items import Pacgum, SuperPacgum
    from .maze import Maze


GHOST_NAMES = ("BLINKY", "PINKY", "INKY", "CLYDE")


@dataclass
class EvaluatorMode:
    """Opt-in reviewer aids; every command is a no-op when disabled."""

    enabled: bool
    frozen_at: int | None = None
    frozen_ms: int = 0
    selected_ghost: int | None = None

    @property
    def frozen(self) -> bool:
        """True while Evaluator Freeze holds game time still."""
        return self.frozen_at is not None

    @property
    def hud_lines(self) -> tuple[str, ...]:
        """Return the HUD badge lines: none in a normal game."""
        if not self.enabled:
            return ()
        lines = ["EVALUATOR FREEZE" if self.frozen else "EVALUATOR"]
        if self.selected_ghost is not None:
            lines.append(f"SELECTED {GHOST_NAMES[self.selected_ghost]}")
        return tuple(lines)

    def toggle_freeze(self, now: int) -> None:
        """Freeze or unfreeze game time; ignored when evaluator mode is off."""
        if not self.enabled:
            return
        if self.frozen_at is None:
            self.frozen_at = now
        else:
            self.frozen_ms += now - self.frozen_at
            self.frozen_at = None

    def game_time(self, now: int) -> int:
        """Return the timestamp domain code should see at clock time `now`.

        Advances with `now` while unfrozen, stands still while frozen, and
        never jumps forward after an unfreeze.
        """
        end_time = self.frozen_at if self.frozen_at is not None else now
        return end_time - self.frozen_ms

    def select_next_ghost(self, ghost_count: int) -> None:
        """Cycle the selected ghost while evaluator freeze is active."""
        if not self.enabled or not self.frozen or ghost_count == 0:
            return
        self.selected_ghost = (
            0 if self.selected_ghost is None
            else (self.selected_ghost + 1) % ghost_count
        )

    def move_selected_ghost(
        self,
        ghosts: list[Ghost],
        maze: Maze,
        direction: tuple[int, int],
    ) -> None:
        """Move the selected frozen ghost one walkable tile."""
        if not self.enabled or not self.frozen or self.selected_ghost is None:
            return
        ghost = ghosts[self.selected_ghost]
        target_x = ghost.grid_x + direction[0]
        target_y = ghost.grid_y + direction[1]
        if not (0 <= target_x < maze.width and 0 <= target_y < maze.height):
            return
        if maze.is_wall(target_x, target_y):
            return
        ghost.grid_x, ghost.grid_y = target_x, target_y
        ghost.current_direction = (0, 0)
        ghost.progress = 0.0

    # ------- clear level with C -------
    def clear_level(
        self,
        pacgums: dict[tuple[int, int], Pacgum],
        super_pacgums: dict[tuple[int, int], SuperPacgum],
    ) -> None:
        """Remove every collectible so the normal victory check ends the level.

        Awards no points: evaluator runs are not comparable to real scores.
        """
        if not self.enabled:
            return
        pacgums.clear()
        super_pacgums.clear()
