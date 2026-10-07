import numpy as np
import pygame
from ..gfx import bitmap_font, raster

FONT_SCALE = 4
EVALUATOR_FONT_SCALE = 2
EVALUATOR_COLORS = ((255, 140, 0), (0, 255, 255))


def _blit_midleft(surface: pygame.Surface, rgba: np.ndarray,
                  point: tuple[int, int]) -> None:
    h = rgba.shape[1]
    x, y = point
    raster.blit_to_surface(surface, rgba, (x, y - h // 2))


def _blit_center(surface: pygame.Surface, rgba: np.ndarray,
                 point: tuple[int, int]) -> None:
    w, h = rgba.shape[0], rgba.shape[1]
    x, y = point
    raster.blit_to_surface(surface, rgba, (x - w // 2, y - h // 2))


def _blit_midright(surface: pygame.Surface, rgba: np.ndarray,
                   point: tuple[int, int]) -> None:
    w, h = rgba.shape[0], rgba.shape[1]
    x, y = point
    raster.blit_to_surface(surface, rgba, (x - w, y - h // 2))


def draw_legend(surface: pygame.Surface,
                time_left: int, score: int, lives: int,
                level_num: int, is_powered_up: bool, hud_y_start: int,
                evaluator_lines: tuple[str, ...] = ()) -> None:
    """Draws the game's HUD including timer, score, lives and evaluator badge."""
    TEXT_COLOR = (255, 255, 255)
    POWER_COLOR = (255, 255, 0)
    URGENT_COLOR = (255, 0, 0)
    LINE_COLOR = (50, 50, 255)

    screen_width = surface.get_width()

    pygame.draw.line(surface, LINE_COLOR, (0, hud_y_start),
                     (screen_width, hud_y_start), 3)

    top_row_y = hud_y_start + 40
    bottom_row_y = hud_y_start + 90

    score_text = bitmap_font.render_text(f"SCORE: {score}", FONT_SCALE, TEXT_COLOR)
    _blit_midleft(surface, score_text, (30, top_row_y))

    timer_color = URGENT_COLOR if time_left <= 10 else TEXT_COLOR
    timer_text = bitmap_font.render_text(f"TIME: {time_left}", FONT_SCALE, timer_color)
    _blit_center(surface, timer_text, (screen_width // 2, top_row_y))

    lives_text = bitmap_font.render_text(f"LIVES: {lives}", FONT_SCALE, TEXT_COLOR)
    _blit_midright(surface, lives_text, (screen_width - 30, top_row_y))

    level_text = bitmap_font.render_text(f"LEVEL: {level_num}", FONT_SCALE, TEXT_COLOR)
    _blit_center(surface, level_text, (screen_width // 2, hud_y_start + 70))

    if is_powered_up:
        power_text = bitmap_font.render_text(
            "POWER PELLET ACTIVE!", FONT_SCALE, POWER_COLOR)
        _blit_center(surface, power_text, (screen_width // 2, bottom_row_y))

    badges = []
    for index, line in enumerate(evaluator_lines):
        color = EVALUATOR_COLORS[min(index, len(EVALUATOR_COLORS) - 1)]
        badges.append(bitmap_font.render_text(line, EVALUATOR_FONT_SCALE, color))
    badge_x = 20
    badge_y = surface.get_height() - max(
        (badge.shape[1] for badge in badges),
        default=0,
    )
    for badge in badges:
        _blit_midleft(surface, badge, (badge_x, badge_y + badge.shape[1] // 2))
        badge_x += badge.shape[0] + 20
