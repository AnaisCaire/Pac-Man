import pygame
import sys

from .config import Config
from .maze import Maze
from ..ui.gameplay import draw_maze, draw_player, draw_pacgums, draw_legend, draw_super_pacgums
from .player import Player, handle_input, check_collision
from .ghosts import Ghost

WINDOW_SIZE = 800
HUB_HEIGHT = 100

def game_loop(config: Config) -> None:
    pygame.init()

    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + HUB_HEIGHT))
    pygame.display.set_caption("Pac-Man")
    clock = pygame.time.Clock()
    # Initialize Font for drawing the timer on screen
    font = pygame.font.SysFont(None, 36)

    level_size = config.level[0]
    tile_size = WINDOW_SIZE // max(level_size.width, level_size.height)
    offset_x = (WINDOW_SIZE - tile_size * level_size.width) // 2
    offset_y = (WINDOW_SIZE - tile_size * level_size.height) // 2

    maze = Maze(level_size, seed=config.seed)
    spawn = sx, sy = maze.find_spawn()
    player = Player(sx, sy, tile_size, config)
    pacgums = maze.place_pacgums(spawn)
    super_pacgums = maze.place_super_pacgums()

    level_start_time = pygame.time.get_ticks()

    hihi = Ghost(x, y, color, tile_size, player, start_time=level_start_time)
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        events = pygame.event.get()
        handle_input(player, events)
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        
        # timer logic
        passed_secs = (current_time - level_start_time) // 1000
        time_left = max(0, config.level_max_time - passed_secs)
        if time_left == 0:
            print("Time's up! Level Over.")
            running = False

        player.update(maze)
        check_collision(player, pacgums, super_pacgums, 
                        config.points_per_pacgum, 
                        config.points_per_super_pacgum)
        
        # -- super pac gums ---
        player.update_timers()

        # Drawing
        screen.fill((0, 0, 0))
        draw_maze(screen, maze, tile_size, offset_x, offset_y)
        draw_player(screen, player, tile_size, offset_x, offset_y)
        draw_pacgums(screen, pacgums, tile_size, offset_x, offset_y)
        draw_super_pacgums(screen, super_pacgums, tile_size, offset_x, offset_y)
        draw_legend(
            surface=screen,
            font=font,
            time_left=time_left,
            score=player.score,
            lives=player.lives,
            is_powered_up=player.is_powered_up,
            hud_y_start=WINDOW_SIZE
        )
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()
