import pygame
import sys
from enum import Enum

from .config import Config
from .maze import Maze
from ..ui.screens.main_menu import MainMenu
from ..ui.gameplay import draw_maze, draw_player, draw_pacgums, draw_legend, draw_super_pacgums, draw_ghosts
from .entities.player import Player, handle_input, check_collision, check_ghost_collision
from .entities.ghost_types import Blinky, Pinky, Inky, Clyde


WINDOW_SIZE = 800
HUB_HEIGHT = 100

class GameState(Enum):
    " all the different states of the engine "
    MAIN_MENU = 1
    HIGHSCORES = 2
    IN_GAME = 3
    PAUSE = 4
    GAME_OVER = 5
    VICTORY = 6


def _run_gameplay(screen: pygame.Surface, clock: pygame.time.Clock,
                  config: Config, font: pygame.font.Font,
                  tile_size: int, offset_x: int, offset_y: int) -> GameState:
    """
    Run the in-game loop. 
    Returns the next GameState when the game ends.
    """
    maze = Maze(config.level[0], seed=config.seed)
    spawn = sx, sy = maze.find_spawn()
    player = Player(sx, sy, tile_size, config)
    pacgums = maze.place_pacgums(spawn, config.pacgum)
    super_pacgums = maze.place_super_pacgums()

    level_start_time = pygame.time.get_ticks()

    ghost_positions = maze.place_ghosts()
    ghost_classes = [Blinky, Pinky, Inky, Clyde]
    ghost_list = []
    for cls, pos in zip(ghost_classes, ghost_positions):
        x, y = pos
        ghost_list.append(cls(x, y, tile_size, player, start_time=level_start_time))
    ghost_list[2].blinky = ghost_list[0]  # Inky needs Blinky

    while True:
        current_time = pygame.time.get_ticks()
        events = pygame.event.get()
        handle_input(player, events)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        passed_secs = (current_time - level_start_time) // 1000
        time_left = max(0, config.level_max_time - passed_secs)
        if time_left == 0:
            return GameState.GAME_OVER

        if not player.is_dying:
            player.update(maze)
        was_powered_up = player.is_powered_up
        check_collision(player, pacgums, super_pacgums,
                        config.points_per_pacgum,
                        config.points_per_super_pacgum)
        if player.is_powered_up and not was_powered_up:
            for ghost in ghost_list:
                ghost.frighten(current_time)
        check_ghost_collision(player, ghost_list)
        player.update_timers()

        if player.lives <= 0 and not player.is_alive and not player.is_dying:
            return GameState.GAME_OVER
        if not pacgums and not super_pacgums:
            return GameState.VICTORY

        for ghost in ghost_list:
            ghost.update(current_time, maze)

        screen.fill((0, 0, 0))
        draw_maze(screen, maze, tile_size, offset_x, offset_y)
        draw_player(screen, player, tile_size, offset_x, offset_y)
        draw_pacgums(screen, pacgums, tile_size, offset_x, offset_y)
        draw_super_pacgums(screen, super_pacgums, tile_size, offset_x, offset_y)
        draw_ghosts(screen, ghost_list, tile_size, offset_x, offset_y)
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


def game_loop(config: Config) -> None:
    pygame.init()

    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + HUB_HEIGHT))
    pygame.display.set_caption("Pac-Man")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    level_size = config.level[0]
    tile_size = WINDOW_SIZE // max(level_size.width, level_size.height)
    offset_x = (WINDOW_SIZE - tile_size * level_size.width) // 2
    offset_y = (WINDOW_SIZE - tile_size * level_size.height) // 2

    state = GameState.MAIN_MENU
    menu = MainMenu(WINDOW_SIZE, WINDOW_SIZE + HUB_HEIGHT)

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if state == GameState.MAIN_MENU:
            for event in events:
                action = menu.handle_event(event)
                if action == "play":
                    state = GameState.IN_GAME
                elif action == "highscores":
                    state = GameState.HIGHSCORES
                elif action == "instructions":
                    pass  # TODO
                elif action == "quit":
                    pygame.quit()
                    sys.exit()
            menu.update(pygame.mouse.get_pos())
            menu.draw(screen)

        elif state == GameState.HIGHSCORES:
            pass  # TODO: draw highscores screen
        elif state == GameState.IN_GAME:
            state = _run_gameplay(screen, clock, config, font, tile_size, offset_x, offset_y)
        elif state == GameState.GAME_OVER:
            pass  # TODO: draw game over screen
        elif state == GameState.VICTORY:
            pass  # TODO: draw victory screen

        pygame.display.flip()
        clock.tick(60)
