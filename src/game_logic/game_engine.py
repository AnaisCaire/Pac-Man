import pygame
import sys
from enum import Enum

from .config import Config
from .maze import Maze
from ..ui.screens.main_menu import MainMenu
from ..ui.screens.gameover import GameOver
from ..ui.screens.victory import VictoryScreen
from ..ui.screens.sub_screens import HighscoreScreen, InstructionsScreen, PauseScreen
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
    GAME_OVER = 4
    VICTORY = 5
    INSTRUCT = 6


def _run_gameplay(screen: pygame.Surface, clock: pygame.time.Clock,
                  config: Config, font: pygame.font.Font,
                  pause_menu: PauseScreen,
                  level_index: int,
                  initial_score: int,
                  initial_lives: int) -> tuple[GameState, int, int]:
    """
    Run one level of gameplay.
    Returns (next_state, final_score, final_lives).
    """
    level_size = config.level[level_index]
    tile_size = WINDOW_SIZE // max(level_size.width, level_size.height)
    offset_x = (WINDOW_SIZE - tile_size * level_size.width) // 2
    offset_y = (WINDOW_SIZE - tile_size * level_size.height) // 2

    maze = Maze(level_size, seed=config.seed + level_index)
    spawn = sx, sy = maze.find_spawn()
    player = Player(sx, sy, tile_size, config)
    player.score = initial_score
    player.lives = initial_lives
    pacgums = maze.place_pacgums(spawn, config.pacgum)
    super_pacgums = maze.place_super_pacgums()

    level_start_time = pygame.time.get_ticks()
    total_pause_ms = 0

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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pause_start = pygame.time.get_ticks()
                paused = True
                while paused:
                    for pause_event in pygame.event.get():
                        if pause_event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if pause_event.type == pygame.KEYDOWN and pause_event.key == pygame.K_ESCAPE:
                            paused = False
                        action = pause_menu.handle_event(pause_event)
                        if action == "resume":
                            paused = False
                        elif action == "menu":
                            return (GameState.MAIN_MENU, player.score, player.lives)
                    pause_menu.update(pygame.mouse.get_pos())
                    pause_menu.draw(screen)
                    pygame.display.flip()
                    clock.tick(60)
                total_pause_ms += pygame.time.get_ticks() - pause_start

        passed_secs = (current_time - level_start_time - total_pause_ms) // 1000
        time_left = max(0, config.level_max_time - passed_secs)
        if time_left == 0:
            return (GameState.GAME_OVER, player.score, player.lives)

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
            return (GameState.GAME_OVER, player.score, player.lives)
        if not pacgums and not super_pacgums:
            return (GameState.VICTORY, player.score, player.lives)

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
            level_num=level_index + 1,
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

    # --- all the windows ------
    state = GameState.MAIN_MENU
    current_level = 0
    current_score = 0
    current_lives = config.lives
    menu = MainMenu(WINDOW_SIZE, WINDOW_SIZE + HUB_HEIGHT)
    high_menu = HighscoreScreen(WINDOW_SIZE, WINDOW_SIZE + HUB_HEIGHT)
    inst_menu = InstructionsScreen(WINDOW_SIZE, WINDOW_SIZE + HUB_HEIGHT)
    pause_menu = PauseScreen(WINDOW_SIZE, WINDOW_SIZE + HUB_HEIGHT)
    gameover_menu = GameOver(WINDOW_SIZE, WINDOW_SIZE + HUB_HEIGHT)
    victory_menu = VictoryScreen(WINDOW_SIZE, WINDOW_SIZE + HUB_HEIGHT)


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
                    current_level = 0
                    current_score = 0
                    current_lives = config.lives
                    state = GameState.IN_GAME
                elif action == "highscores":
                    state = GameState.HIGHSCORES
                elif action == "instructions":
                    state = GameState.INSTRUCT
                elif action == "quit":
                    pygame.quit()
                    sys.exit()
            menu.update(pygame.mouse.get_pos())
            menu.draw(screen)

        elif state == GameState.HIGHSCORES:
            for event in events:
                high_action = high_menu.handle_event(event)
                if high_action == "back":
                    state = GameState.MAIN_MENU
            high_menu.update(pygame.mouse.get_pos())
            high_menu.draw(screen)

        elif state == GameState.INSTRUCT:
            for event in events:
                inst_action = inst_menu.handle_event(event)
                if inst_action == "back":
                    state = GameState.MAIN_MENU
            inst_menu.update(pygame.mouse.get_pos())
            inst_menu.draw(screen)

        elif state == GameState.IN_GAME:
            next_state, current_score, current_lives = _run_gameplay(
                screen, clock, config, font, pause_menu,
                level_index=current_level,
                initial_score=current_score,
                initial_lives=current_lives
            )
            if next_state == GameState.VICTORY:
                current_level += 1
                if current_level >= len(config.level):
                    state = GameState.VICTORY
                else:
                    state = GameState.IN_GAME
            elif next_state == GameState.GAME_OVER:
                state = GameState.GAME_OVER
            elif next_state == GameState.MAIN_MENU:
                current_level = 0
                current_score = 0
                current_lives = config.lives
                state = GameState.MAIN_MENU


        elif state == GameState.GAME_OVER:
            for event in events:
                gameover_action = gameover_menu.handle_event(event)
                if gameover_action == "main menu":
                    state = GameState.MAIN_MENU
            gameover_menu.update(pygame.mouse.get_pos())
            gameover_menu.draw(screen)

        elif state == GameState.VICTORY:
            for event in events:
                victory_action = victory_menu.handle_event(event)
                if victory_action == "main menu":
                    state = GameState.MAIN_MENU
            victory_menu.update(pygame.mouse.get_pos())
            victory_menu.draw(screen)

        pygame.display.flip()
        clock.tick(60)
