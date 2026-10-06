"""Reusable final-score name-entry screen."""

from __future__ import annotations

import pathlib

import pygame

from ...scores.model import ScoreEntry
from ..gfx import bitmap_font, raster

_BG_COLOR = (106, 159, 181)
_TEXT_COLOR = (255, 255, 255)
_ERROR_COLOR = (255, 80, 80)
_FONT_SCALE = 4
_IMAGES_DIR = pathlib.Path(__file__).parent.parent / "images"
# Returned instead of "submit" when an evaluator run must not be saved.
MENU_ACTION = "menu"


def _draw_center(surface: pygame.Surface, text: str, y: int,
                 color: tuple[int, int, int]) -> None:
    image = bitmap_font.render_text(text, _FONT_SCALE, color)
    raster.blit_to_surface(
        surface,
        image,
        (surface.get_width() // 2 - image.shape[0] // 2, y),
    )


class ScoreEntryScreen:
    """Collect one validated player name before returning to the main menu."""

    def __init__(self, screen_width: int, screen_height: int, image_name: str) -> None:
        self.score = 0
        self.name = ""
        self.error: str | None = None
        center_x = screen_width // 2
        raw_image = raster.load_rgba(str(_IMAGES_DIR / image_name))
        max_height = screen_height - 320
        scale = min(screen_width / raw_image.shape[0], max_height / raw_image.shape[1])
        image_width = int(raw_image.shape[0] * scale)
        image_height = int(raw_image.shape[1] * scale)
        self.image = raster.nearest_neighbor_scale(raw_image, image_width, image_height)
        self.image_rect = pygame.Rect((0, 0), (image_width, image_height))
        self.image_rect.center = (center_x, image_height // 2 + 10)
        self.evaluator_run = False

    def set_score(self, score: int, evaluator_run: bool = False) -> None:
        """Prepare a fresh end screen; evaluator runs skip name entry."""
        self.score = score
        self.name = ""
        self.error = None
        self.evaluator_run = evaluator_run

    def score_entry(self) -> ScoreEntry:
        """Return the current input or raise a precise validation error."""
        return ScoreEntry(self.name, self.score)

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if self.evaluator_run:
            is_enter = event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN
            return MENU_ACTION if is_enter else None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
                self.error = None
            elif event.key == pygame.K_RETURN:
                return self._submit()
            elif (
                event.unicode.isascii()
                and (event.unicode.isalnum() or event.unicode == " ")
                and len(self.name) < 10
            ):
                self.name += event.unicode
                self.error = None
        return None

    def _submit(self) -> str | None:
        try:
            self.score_entry()
        except ValueError as error:
            self.error = str(error)
            return None
        return "submit"

    def update(self, mouse_pos: tuple[int, int]) -> None:
        """Keep the screen adapter contract; keyboard input needs no hover state."""

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(_BG_COLOR)
        raster.blit_to_surface(surface, self.image, self.image_rect.topleft)
        text_y = max(self.image_rect.bottom + 20, surface.get_height() - 260)
        _draw_center(
            surface, f"SCORE: {self.score}", text_y, _TEXT_COLOR
        )
        if self.evaluator_run:
            _draw_center(surface, "EVALUATOR RUN", text_y + 45, _ERROR_COLOR)
            _draw_center(surface, "SCORE NOT SAVED", text_y + 85, _ERROR_COLOR)
            _draw_center(
                surface, "PRESS ENTER FOR MENU", text_y + 135, _TEXT_COLOR
            )
            return
        _draw_center(
            surface, "INSERT NAME", text_y + 45, _TEXT_COLOR
        )
        visible_name = f"{self.name} I" if self.name else "I"
        _draw_center(
            surface, f"NAME: {visible_name}", text_y + 85, _TEXT_COLOR
        )
        _draw_center(
            surface, "PRESS ENTER TO SUBMIT", text_y + 135, _TEXT_COLOR
        )
        if self.error is not None:
            _draw_center(
                surface, self.error, text_y + 175, _ERROR_COLOR
            )
