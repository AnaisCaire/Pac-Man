import pygame
import math
from ....game_logic.entities.player import Player

DIRECTION_ANGLES = {
    (1, 0): 0.0,
    (0, -1): -math.pi / 2.0,
    (-1, 0): math.pi,
    (0, 1): math.pi / 2.0,
}
MAX_MOUTH_ANGLE = math.pi / 4.0
ARC_POINTS = 20
PLAYER_COLOR = (255, 255, 0)


def draw_player(surface: pygame.Surface, player: Player, tile_size: int,
                offset_x: int = 0, offset_y: int = 0) -> None:
    """Draw Pac-Man as an animated yellow wedge."""
    px = offset_x + (player.grid_x + player.progress * player.current_direction[0]) * tile_size
    py = offset_y + (player.grid_y + player.progress * player.current_direction[1]) * tile_size
    # shrink radius to 0 as death_progress goes from 0.0 → 1.0
    full_radius = tile_size // 3
    radius = int(full_radius * (1.0 - player.death_progress))
    if radius <= 0:
        return  # fully shrunk — nothing to draw
    center_x, center_y = int(px + tile_size // 2), int(py + tile_size // 2)

    facing_mouth = DIRECTION_ANGLES.get(player.current_direction, 0.0)
    aperture = MAX_MOUTH_ANGLE * math.sin(player.progress * math.pi) if player.moving else 0.0

    start_angle = facing_mouth + aperture
    end_angle = facing_mouth + (2 * math.pi) - aperture
    points = [(center_x, center_y)]

    for i in range(ARC_POINTS + 1):
        theta = start_angle + i * (end_angle - start_angle) / ARC_POINTS
        points.append((int(center_x + radius * math.cos(theta)),
                       int(center_y + radius * math.sin(theta))))

    pygame.draw.polygon(surface, PLAYER_COLOR, points)
