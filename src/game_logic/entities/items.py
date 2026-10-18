class Item:
    """Base class for collectible items in the maze."""

    def __init__(self, x: int, y: int, points: int, is_super: bool) -> None:
        """Store an item's grid position, score value, and power-pellet flag."""
        self.x = x
        self.y = y
        self.points = points
        self.is_super = is_super


class Pacgum(Item):
    """A normal collectible that awards points without a power-up."""

    def __init__(self, x: int, y: int, points: int) -> None:
        """Create a normal pacgum at one grid position."""
        super().__init__(x, y, points, is_super=False)


class SuperPacgum(Item):
    """A power pellet that awards points and makes ghosts edible."""

    def __init__(self, x: int, y: int, points: int) -> None:
        """Create a super-pacgum at one grid position."""
        super().__init__(x, y, points, is_super=True)
