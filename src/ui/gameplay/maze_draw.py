import pygame
from ...game_logic.maze import Maze

WALL_COLOR = (0, 0, 255)
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


def draw_pacgums(surface: pygame.Surface, pacgums: set[tuple[int, int]], tile_size: int,
                 offset_x: int = 0, offset_y: int = 0) -> None:
    """ small little light pink boxes """
    pacgum_size = max(2, tile_size // 5)
    half_tile = tile_size // 2
    half_pacgum = pacgum_size // 2

    for grid_x, grid_y in pacgums:
        px = offset_x + grid_x * tile_size
        py = offset_y + grid_y * tile_size
        center_x = px + half_tile
        center_y = py + half_tile
        box_x = center_x - half_pacgum
        box_y = center_y - half_pacgum
        pygame.draw.rect(surface, PACGUM_COLOR, (box_x, box_y, pacgum_size, pacgum_size))


def draw_super_pacgums(surface: pygame.Surface, pacgums: set[tuple[int, int]], tile_size: int,
                       offset_x: int = 0, offset_y: int = 0) -> None:
    """ bigger light red boxes """
    pacgum_size = max(2, tile_size // 3)
    half_tile = tile_size // 2
    half_pacgum = pacgum_size // 2

    for grid_x, grid_y in pacgums:
        px = offset_x + grid_x * tile_size
        py = offset_y + grid_y * tile_size
        center_x = px + half_tile
        center_y = py + half_tile
        box_x = center_x - half_pacgum
        box_y = center_y - half_pacgum
        pygame.draw.rect(surface, SUPERPACGUM_COLOR, (box_x, box_y, pacgum_size, pacgum_size))
