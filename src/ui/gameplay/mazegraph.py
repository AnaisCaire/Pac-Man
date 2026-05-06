import pygame
from ...game_logic.maze import Maze
from ...game_logic.player import Player
import math

# for flake 8 in mouth animation
DIRECTION_ANGLES = {
    (1, 0): 0.0,                # Right
    (0, -1): -math.pi / 2.0,    # Up
    (-1, 0): math.pi,           # Left
    (0, 1): math.pi / 2.0       # Down
}
MAX_MOUTH_ANGLE = math.pi / 4.0  # 45 degrees
ARC_POINTS = 20  # N points for the curved part of the body
WALL_COLOR = (0, 0, 255)
PLAYER_COLOR = (255, 255, 0)
PACGUM_COLOR = (255, 182, 193)
SUPERPACGUM_COLOR = (255, 102, 102)


def draw_maze(surface: pygame.Surface, maze: Maze, tile_size: int,
              offset_x: int = 0, offset_y: int = 0) -> None:
    for y in range(len(maze.grid)):
        for x in range(len(maze.grid[y])):
            px = offset_x + x * tile_size
            py = offset_y + y * tile_size

            if maze.is_wall(x, y):
                pygame.draw.rect(surface, WALL_COLOR, (px, py, tile_size, tile_size))
                continue

            if maze.has_wall(x, y, 'N'):
                pygame.draw.line(surface, WALL_COLOR, (px, py), (px + tile_size, py))
            if maze.has_wall(x, y, 'E'):
                pygame.draw.line(surface, WALL_COLOR, (px + tile_size, py), (px + tile_size, py + tile_size))
            if maze.has_wall(x, y, 'S'):
                pygame.draw.line(surface, WALL_COLOR, (px, py + tile_size), (px + tile_size, py + tile_size))
            if maze.has_wall(x, y, 'W'):
                pygame.draw.line(surface, WALL_COLOR, (px, py), (px, py + tile_size))


def draw_player(surface: pygame.Surface, player: Player, tile_size: int,
                offset_x: int = 0, offset_y: int = 0) -> None:
    """
    Create a yellow circle
    Make a mouth (progress is mapped by a sinus wave)
    """
    # 1. make circle in the middle
    px = offset_x + (player.grid_x + player.progress * player.current_direction[0]) * tile_size
    py = offset_y + (player.grid_y + player.progress * player.current_direction[1]) * tile_size
    radius = tile_size // 3
    center_x, center_y = int(px + tile_size // 2), int(py + tile_size // 2)

    # 2. where the mouth is facing (default is rightn at start)
    facing_mouth = DIRECTION_ANGLES.get(player.current_direction, 0.0)

    # 3. current mouth aperture depending on progress
    aperture = MAX_MOUTH_ANGLE * math.sin(player.progress * math.pi) if player.moving else 0.0

    # 4. define start/end of arc + center
    start_angle = facing_mouth + aperture
    end_angle = facing_mouth + (2 * math.pi) - aperture
    points = [(center_x, center_y)]

    # generate the points of the arc
    for i in range(ARC_POINTS + 1):
        # Linearly interpolate the angle between start_angle and end_angle
        theta = start_angle + i * (end_angle - start_angle) / ARC_POINTS
        
        # Calculate X and Y using trig
        x = center_x + radius * math.cos(theta)
        y = center_y + radius * math.sin(theta)
        points.append((x, y))

    # 6. Draw the filled polygon
    # Pygame 2.x handles float coordinates in polygons perfectly
    pygame.draw.polygon(surface, PLAYER_COLOR, points)

def draw_pacgums(surface: pygame.Surface, pacgums: set[tuple[int, int]], tile_size: int,
                offset_x: int = 0, offset_y: int = 0) -> None:
    """ small little light pink boxes """
    pacgum_size = max(2, tile_size // 5)
    half_tile = tile_size // 2
    half_pacgum = pacgum_size // 2

    for grid_x, grid_y in pacgums:
        px = offset_x + grid_x * tile_size
        py = offset_y + grid_y * tile_size
        
        # Find the exact center pixel of the grid cell
        center_x = px + half_tile
        center_y = py + half_tile
        
        # Calculate the top-left coordinate for the pacgum
        box_x = center_x - half_pacgum
        box_y = center_y - half_pacgum
        
        # 4. Draw the square
        pygame.draw.rect(surface, PACGUM_COLOR, (box_x, box_y, pacgum_size, pacgum_size))

def draw_super_pacgums(surface: pygame.Surface, pacgums: set[tuple[int, int]], tile_size: int,
                offset_x: int = 0, offset_y: int = 0) -> None:
    """ bigger little light red boxes """
    pacgum_size = max(2, tile_size // 3)
    half_tile = tile_size // 2
    half_pacgum = pacgum_size // 2

    for grid_x, grid_y in pacgums:
        px = offset_x + grid_x * tile_size
        py = offset_y + grid_y * tile_size
        
        # Find the exact center pixel of the grid cell
        center_x = px + half_tile
        center_y = py + half_tile
        
        # Calculate the top-left coordinate for the pacgum
        box_x = center_x - half_pacgum
        box_y = center_y - half_pacgum
        
        # 4. Draw the square
        pygame.draw.rect(surface, SUPERPACGUM_COLOR, (box_x, box_y, pacgum_size, pacgum_size))

def draw_legend(surface: pygame.Surface, font: pygame.font.Font, 
                time_left: int, score: int, lives: int, is_powered_up: bool, hud_y_start: int) -> None:
    """
    Draws the game's HUD (Heads Up Display) including timer, score, and lives.
    """
    TEXT_COLOR = (255, 255, 255)  # White
    POWER_COLOR = (255, 255, 0)   # Yellow
    URGENT_COLOR = (255, 0, 0)    # Red
    LINE_COLOR = (50, 50, 255)    # Dark Blue

    screen_width = surface.get_width()

    pygame.draw.line(surface, LINE_COLOR, (0, hud_y_start), (screen_width, hud_y_start), 3)
    
    top_row_y = hud_y_start + 40
    bottom_row_y = hud_y_start + 90

    # 1. Draw Score (Anchored to the Left)
    score_text = font.render(f"SCORE: {score}", True, TEXT_COLOR)
    # midleft=(X, Y) aligns the left edge of the text to X=30
    score_rect = score_text.get_rect(midleft=(30, top_row_y))
    surface.blit(score_text, score_rect)

    # 2. Draw Timer (Anchored in the Center)
    timer_color = URGENT_COLOR if time_left <= 10 else TEXT_COLOR
    timer_text = font.render(f"TIME: {time_left}", True, timer_color)
    timer_rect = timer_text.get_rect(center=(screen_width // 2, top_row_y))
    surface.blit(timer_text, timer_rect)

    # 3. Draw Lives (Anchored to the Right)
    lives_text = font.render(f"LIVES: {lives}", True, TEXT_COLOR)
    # midright=(X, Y) aligns the right edge of the text to 30 pixels from the right wall
    lives_rect = lives_text.get_rect(midright=(screen_width - 30, top_row_y))
    surface.blit(lives_text, lives_rect)

    # 4. Draw Power-Up Status (Centered below the top row)
    if is_powered_up:
        power_text = font.render("POWER PELLET ACTIVE!", True, POWER_COLOR)
        power_rect = power_text.get_rect(center=(screen_width // 2, bottom_row_y))
        surface.blit(power_text, power_rect)