class Item:
    """Base class for collectible items in the maze."""

    def __init__(self, x: int, y: int, points: int, is_super: bool) -> None:
        self.x = x
        self.y = y
        self.points = points
        self.is_super = is_super


class Pacgum(Item):
    def __init__(self, x: int, y: int, points: int) -> None:
        super().__init__(x, y, points, is_super=False)


class SuperPacgum(Item):
    def __init__(self, x: int, y: int, points: int) -> None:
        super().__init__(x, y, points, is_super=True)
