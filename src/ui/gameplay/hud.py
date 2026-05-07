import pygame


def draw_legend(surface: pygame.Surface, font: pygame.font.Font,
                time_left: int, score: int, lives: int,
                is_powered_up: bool, hud_y_start: int) -> None:
    """Draws the game's HUD including timer, score, and lives."""
    TEXT_COLOR = (255, 255, 255)
    POWER_COLOR = (255, 255, 0)
    URGENT_COLOR = (255, 0, 0)
    LINE_COLOR = (50, 50, 255)

    screen_width = surface.get_width()

    pygame.draw.line(surface, LINE_COLOR, (0, hud_y_start), (screen_width, hud_y_start), 3)

    top_row_y = hud_y_start + 40
    bottom_row_y = hud_y_start + 90

    score_text = font.render(f"SCORE: {score}", True, TEXT_COLOR)
    surface.blit(score_text, score_text.get_rect(midleft=(30, top_row_y)))

    timer_color = URGENT_COLOR if time_left <= 10 else TEXT_COLOR
    timer_text = font.render(f"TIME: {time_left}", True, timer_color)
    surface.blit(timer_text, timer_text.get_rect(center=(screen_width // 2, top_row_y)))

    lives_text = font.render(f"LIVES: {lives}", True, TEXT_COLOR)
    surface.blit(lives_text, lives_text.get_rect(midright=(screen_width - 30, top_row_y)))

    if is_powered_up:
        power_text = font.render("POWER PELLET ACTIVE!", True, POWER_COLOR)
        surface.blit(power_text, power_text.get_rect(center=(screen_width // 2, bottom_row_y)))
