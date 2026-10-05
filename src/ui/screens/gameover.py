from .score_entry import ScoreEntryScreen


class GameOver(ScoreEntryScreen):
    """Collect the final score after a losing game."""

    def __init__(self, screen_width: int, screen_height: int):
        super().__init__(screen_width, screen_height, "game_over.png")
