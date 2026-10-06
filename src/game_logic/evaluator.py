"""Evaluator (cheat) mode state for peer review.

Application-level state only: no pygame, no wall clock. The caller passes
`now` from `ProjectClock.get_ticks_ms()`; the input adapter decides which
key maps to which method.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .entities.items import Pacgum, SuperPacgum


@dataclass
class EvaluatorMode:
    """Opt-in reviewer aids; every command is a no-op when disabled."""

    enabled: bool
    frozen_at: int | None = None
    frozen_ms: int = 0

    @property
    def frozen(self) -> bool:
        """True while Evaluator Freeze holds game time still."""
        return self.frozen_at is not None

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

    # ------- clear level with L -------
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
