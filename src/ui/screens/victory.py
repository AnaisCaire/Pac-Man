from .score_entry import ScoreEntryScreen


class VictoryScreen(ScoreEntryScreen):
    """Collect the final score after winning every configured level."""

    def __init__(self, screen_width: int, screen_height: int) -> None:
        """Create the score-entry screen with the Victory image."""
        super().__init__(screen_width, screen_height, "victory_screen.png")
