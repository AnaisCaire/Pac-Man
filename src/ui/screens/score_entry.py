"""Reusable final-score name-entry screen."""

from __future__ import annotations

import pathlib

import pygame

from ...scores.model import ScoreEntry
from ..gfx import bitmap_font, raster
from .bottons import UIElement

_BG_COLOR = (106, 159, 181)
_TEXT_COLOR = (255, 255, 255)
_ERROR_COLOR = (255, 80, 80)
_FONT_SCALE = 4
_BUTTON_FONT_SIZE = 40
_IMAGES_DIR = pathlib.Path(__file__).parent.parent / "images"


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
        button_y = screen_height - 50
        self.submit_button = UIElement(
            center_position=(center_x, button_y - 70),
            text="Save Score",
            font_size=_BUTTON_FONT_SIZE,
            action="submit",
        )
        raw_image = raster.load_rgba(str(_IMAGES_DIR / image_name))
        max_height = button_y - 190
        scale = min(screen_width / raw_image.shape[0], max_height / raw_image.shape[1])
        image_width = int(raw_image.shape[0] * scale)
        image_height = int(raw_image.shape[1] * scale)
        self.image = raster.nearest_neighbor_scale(raw_image, image_width, image_height)
        self.image_rect = pygame.Rect((0, 0), (image_width, image_height))
        self.image_rect.center = (center_x, image_height // 2 + 10)

    def set_score(self, score: int) -> None:
        """Prepare a fresh name entry for the completed game score."""
        self.score = score
        self.name = ""
        self.error = None

    def score_entry(self) -> ScoreEntry:
        """Return the current input or raise a precise validation error."""
        return ScoreEntry(self.name, self.score)

    def handle_event(self, event: pygame.event.Event) -> str | None:
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
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.submit_button.rect.collidepoint(event.pos):
                return self._submit()
        return None

    def _submit(self) -> str | None:
        try:
            self.score_entry()
        except ValueError as error:
            self.error = str(error)
            return None
        return "submit"

    def update(self, mouse_pos: tuple[int, int]) -> None:
        self.submit_button.update(mouse_pos)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(_BG_COLOR)
        raster.blit_to_surface(surface, self.image, self.image_rect.topleft)
        _draw_center(
            surface, f"SCORE: {self.score}", surface.get_height() - 170, _TEXT_COLOR
        )
        _draw_center(
            surface, f"NAME: {self.name}", surface.get_height() - 130, _TEXT_COLOR
        )
        if self.error is not None:
            _draw_center(
                surface, self.error, surface.get_height() - 100, _ERROR_COLOR
            )
        self.submit_button.draw(surface)
