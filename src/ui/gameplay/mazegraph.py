import pygame
from ...game_logic.maze import Maze

WALL_COLOR = (0, 0, 255)


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
