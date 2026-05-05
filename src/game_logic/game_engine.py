import pygame
import sys

from .config import Config
from .maze import Maze
from ..ui.gameplay import draw_maze

WINDOW_SIZE = 800

def game_loop(config: Config) -> None:
    pygame.init()

    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Pac-Man")
    clock = pygame.time.Clock()

    level_size = config.level[0]
    tile_size = WINDOW_SIZE // max(level_size.width, level_size.height)
    offset_x = (WINDOW_SIZE - tile_size * level_size.width) // 2
    offset_y = (WINDOW_SIZE - tile_size * level_size.height) // 2
    maze = Maze(level_size, seed=config.seed)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        draw_maze(screen, maze, tile_size, offset_x, offset_y)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()
