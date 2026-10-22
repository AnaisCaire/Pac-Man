import numpy as np
import pygame
from ..gfx import bitmap_font, raster


FONT_SCALE = 3
EVALUATOR_FONT_SCALE = 2
EVALUATOR_COLORS = ((255, 140, 0), (0, 255, 255))
HUD_PADDING = 10  # space between the separator line and row 1
ROW_GAP = 8  # space between row 1 and row 2
SIDE_MARGIN = 30  # distance from the left/right window edges


def _blit_midleft(surface: pygame.Surface, rgba: np.ndarray,
                  point: tuple[int, int]) -> None:
    """Draw an RGBA array anchored at its left-side midpoint."""
    h = rgba.shape[1]
    x, y = point
    raster.blit_to_surface(surface, rgba, (x, y - h // 2))


def _blit_center(surface: pygame.Surface, rgba: np.ndarray,
                 point: tuple[int, int]) -> None:
    """Draw an RGBA array centered on a destination point."""
    w, h = rgba.shape[0], rgba.shape[1]
    x, y = point
    raster.blit_to_surface(surface, rgba, (x - w // 2, y - h // 2))


def _blit_midright(surface: pygame.Surface, rgba: np.ndarray,
                   point: tuple[int, int]) -> None:
    """Draw an RGBA array anchored at its right-side midpoint."""
    w, h = rgba.shape[0], rgba.shape[1]
    x, y = point
    raster.blit_to_surface(surface, rgba, (x - w, y - h // 2))


def draw_legend(surface: pygame.Surface,
                time_left: int, score: int, lives: int,
                level_num: int, is_powered_up: bool, hud_y_start: int,
                evaluator_lines: tuple[str, ...] = ()) -> None:
    """Draws the game's HUD including timer, score, lives and evaluator
    badge.
    """
    TEXT_COLOR = (255, 255, 255)
    POWER_COLOR = (255, 255, 0)
    URGENT_COLOR = (255, 0, 0)
    LINE_COLOR = (50, 50, 255)

    screen_width = surface.get_width()

    pygame.draw.line(surface, LINE_COLOR, (0, hud_y_start),
                     (screen_width, hud_y_start), 3)

    score_text = bitmap_font.render_text(
        f"SCORE: {score}", FONT_SCALE, TEXT_COLOR
    )

    # rows are computed from the real text height
    # so they can never overlap (shape[1] is the height)
    text_h = score_text.shape[1]
    top_row_y = hud_y_start + HUD_PADDING + text_h // 2
    bottom_row_y = top_row_y + text_h + ROW_GAP

    # row 1: SCORE (left) | TIME (center) | LIVES (right)
    _blit_midleft(surface, score_text, (SIDE_MARGIN, top_row_y))

    timer_color = URGENT_COLOR if time_left <= 10 else TEXT_COLOR
    timer_text = bitmap_font.render_text(
        f"TIME: {time_left}", FONT_SCALE, timer_color
    )
    _blit_center(surface, timer_text, (screen_width // 2, top_row_y))

    lives_text = bitmap_font.render_text(
        f"LIVES: {lives}", FONT_SCALE, TEXT_COLOR
    )
    _blit_midright(
        surface, lives_text, (screen_width - SIDE_MARGIN, top_row_y)
    )

    # row 2: LEVEL (left) | POWER PELLET (center, only when active);
    # LEVEL moved to the left so it no longer shares the center with POWER
    level_text = bitmap_font.render_text(
        f"LEVEL: {level_num}", FONT_SCALE, TEXT_COLOR
    )
    _blit_midleft(surface, level_text, (SIDE_MARGIN, bottom_row_y))

    if is_powered_up:
        power_text = bitmap_font.render_text(
            "POWER PELLET ACTIVE!", FONT_SCALE, POWER_COLOR)
        _blit_center(surface, power_text, (screen_width // 2, bottom_row_y))

    # row 3: evaluator badges in smaller text
    badges = []
    for index, line in enumerate(evaluator_lines):
        color = EVALUATOR_COLORS[min(index, len(EVALUATOR_COLORS) - 1)]
        badges.append(
            bitmap_font.render_text(line, EVALUATOR_FONT_SCALE, color)
        )
    badge_x = SIDE_MARGIN
    for badge in badges:
        badge_row_y = (
            bottom_row_y + text_h // 2 + ROW_GAP + badge.shape[1] // 2
        )
        _blit_midleft(surface, badge, (badge_x, badge_row_y))
        badge_x += badge.shape[0] + 20
