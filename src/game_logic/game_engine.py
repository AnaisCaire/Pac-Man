from __future__ import annotations

from collections.abc import Collection

import pygame
import random
import sys
from dataclasses import dataclass
from enum import Enum
from typing import cast

from .clock import ProjectClock
from .config import Config
from .maze import Maze
from ..ui.screens.main_menu import MainMenu
from ..ui.screens.gameover import GameOver
from ..ui.screens.victory import VictoryScreen
from ..ui.screens.sub_screens import (
    HighscoreScreen,
    InstructionsScreen,
    PauseScreen,
)
from ..ui.gameplay import (
    draw_ghosts,
    draw_legend,
    draw_maze,
    draw_pacgums,
    draw_player,
    draw_super_pacgums,
)
from ..ui.music_manager import MusicManager
from .entities.player import Player, handle_input, resolve_collisions
from .entities.ghost_types import Blinky, Pinky, Inky, Clyde
from .entities.ghosts import Ghost


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


@dataclass
class GameSession:
    """Application state retained across level transitions."""

    level_index: int
    score: int
    lives: int

    @classmethod
    def new(cls, config: Config) -> GameSession:
        """Create a fresh game session from the configured starting lives."""
        return cls(level_index=0, score=0, lives=config.lives)

    def reset(self, config: Config) -> None:
        """Discard the current session before starting a new game."""
        self.level_index = 0
        self.score = 0
        self.lives = config.lives


@dataclass
class LevelTimer:
    """Level elapsed time, excluding a player's death-to-respawn transition."""

    start_time: int
    paused_at: int | None = None
    paused_ms: int = 0

    def pause(self, current_time: int) -> None:
        """Stop the level countdown once without stopping respawn processing."""
        if self.paused_at is None:
            self.paused_at = current_time

    def resume(self, current_time: int) -> None:
        """Resume the level countdown after the player has respawned."""
        if self.paused_at is not None:
            self.paused_ms += current_time - self.paused_at
            self.paused_at = None

    def elapsed_ms(self, current_time: int) -> int:
        """Return elapsed level time excluding a current or completed pause."""
        end_time = self.paused_at if self.paused_at is not None else current_time
        return end_time - self.start_time - self.paused_ms


def transition_session(
    session: GameSession,
    outcome: GameState,
    level_count: int,
) -> GameState:
    """Advance one cleared level or return the terminal application state."""
    if outcome is not GameState.VICTORY:
        return outcome
    if session.level_index + 1 >= level_count:
        return GameState.VICTORY
    session.level_index += 1
    return GameState.IN_GAME


def select_level_seed(configured_seed: int,
                      level_index: int,
                      level_seed_rng: random.Random) -> int:
    """Return the fixed first-level seed or an isolated random later seed."""
    if level_index == 0:
        return configured_seed
    return level_seed_rng.randrange(0, 2 ** 31)


def terminal_state(
    player: Player,
    pacgums: Collection[object],
    super_pacgums: Collection[object],
    timed_out: bool = False,
) -> GameState | None:
    """Return the explicit timeout, defeat, or cleared-level outcome."""
    if timed_out or (player.lives <= 0 and not player.is_alive and not player.is_dying):
        return GameState.GAME_OVER
    if player.is_alive and not player.is_dying and not pacgums and not super_pacgums:
        return GameState.VICTORY
    return None


def _run_gameplay(screen: pygame.Surface, clock: ProjectClock,
                  config: Config,
                  pause_menu: PauseScreen,
                  level_index: int,
                  level_seed: int,
                  placement_rng: random.Random,
                  ghost_rng: random.Random,
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

    maze = Maze(level_size, seed=level_seed)
    spawn = sx, sy = maze.find_spawn()
    player = Player(sx, sy, tile_size, config)
    player.score = initial_score
    player.lives = initial_lives
    super_pacgums = maze.place_super_pacgums(
        config.points_per_super_pacgum,
        spawn,
    )
    pacgums = maze.place_pacgums(
        spawn,
        config.pacgum,
        config.points_per_pacgum,
        placement_rng,
        blocked=set(super_pacgums),
    )

    simulation_start = clock.get_ticks_ms()
    level_timer = LevelTimer(simulation_start)

    ghost_positions = maze.place_ghosts(spawn)
    ghost_classes = [Blinky, Pinky, Inky, Clyde]
    ghost_list: list[Ghost] = []
    for cls, pos in zip(ghost_classes, ghost_positions):
        x, y = pos
        ghost_list.append(cls(x, y, tile_size, player, simulation_start, ghost_rng))
    for ghost in ghost_list:
        ghost.home_positions = ghost_positions
    inky = cast(Inky, ghost_list[2])
    inky.blinky = ghost_list[0]

    while True:
        current_time = clock.get_ticks_ms()
        events = pygame.event.get()
        handle_input(player, events)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Original review note: Maybe change track in "escape menu" too?
            # Post-fix: deferred; pause-specific music is audio polish, not #7.
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                clock.pause()
                paused = True
                while paused:
                    for pause_event in pygame.event.get():
                        if pause_event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        escape_pressed = (
                            pause_event.type == pygame.KEYDOWN
                            and pause_event.key == pygame.K_ESCAPE
                        )
                        if escape_pressed:
                            pause_menu.cancel_confirmation()
                            paused = False
                        action = pause_menu.handle_event(pause_event)
                        if action == "resume":
                            pause_menu.cancel_confirmation()
                            paused = False
                        # Original review note: menu track may be okay here;
                        # check later.
                        # Post-fix: kept current menu track.
                        elif action == "menu":
                            pause_menu.cancel_confirmation()
                            clock.resume()
                            return (GameState.MAIN_MENU, player.score, player.lives)
                    pause_menu.update(pygame.mouse.get_pos())
                    pause_menu.draw(screen)
                    pygame.display.flip()
                    clock.tick(60)
                clock.resume()

        current_time = clock.get_ticks_ms()
        if player.is_dying or (not player.is_alive and player.lives > 0):
            level_timer.pause(current_time)
        else:
            level_timer.resume(current_time)
        passed_secs = level_timer.elapsed_ms(current_time) // 1000
        time_left = max(0, config.level_max_time - passed_secs)
        if terminal_state(
            player,
            pacgums,
            super_pacgums,
            timed_out=time_left == 0,
        ) is GameState.GAME_OVER:
            return (GameState.GAME_OVER, player.score, player.lives)

        if not player.is_dying:
            player.update(maze)
        resolve_collisions(
            player,
            pacgums,
            super_pacgums,
            ghost_list,
            current_time,
        )
        if player.is_dying:
            level_timer.pause(current_time)
        player.update_timers(current_time)
        if player.is_alive:
            level_timer.resume(current_time)

        outcome = terminal_state(player, pacgums, super_pacgums)
        if outcome is not None:
            return (outcome, player.score, player.lives)

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
    # Original review note: set pygame.display.set_icon to change the window
    # icon; Pac-Man with mouth open could work.
    # Post-fix: deferred to #10 asset policy; no new icon asset in this cleanup.
    clock = ProjectClock()
    music = MusicManager.initialize()

    # --- all the windows ------
    state = GameState.MAIN_MENU
    session = GameSession.new(config)
    level_seed_rng = random.Random()
    music.play("menu")
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
                    session.reset(config)
                    music.play("game")
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
            next_state, session.score, session.lives = _run_gameplay(
                screen, clock, config, pause_menu,
                level_index=session.level_index,
                level_seed=select_level_seed(
                    config.seed,
                    session.level_index,
                    level_seed_rng,
                ),
                placement_rng=random.Random(),
                ghost_rng=random.Random(),
                initial_score=session.score,
                initial_lives=session.lives
            )
            # Original review note: winning a level should advance to the next
            # level with the same lives and points.
            # Post-fix: already true in this branch; no behavior change needed.
            # Original review note: maybe add a "Next level: X" transition and
            # its own music track.
            # Post-fix: deferred; transition timing/music is UX scope, not this
            # cleanup.
            if next_state == GameState.VICTORY:
                state = transition_session(session, next_state, len(config.level))
                # Original review note: this case is actually winning the
                # whole game; change track before setting the state.
                # Post-fix: deferred; winning-track work belongs to audio polish.
                if state is GameState.VICTORY:
                    # Original review note: Maybe winning track?
                    # Post-fix: deferred; no new track assets in #4.
                    music.play("menu")
                # Original review note: This is going to the next level not
                # state = GameState.IN_GAME, should load next level instead
                # Post-fix: kept state transition; next loop loads next level
                # with a fresh random seed via select_level_seed().
                else:
                    state = GameState.IN_GAME
            # Original review note: game over needs an end track and username
            # registration for highscores.
            # Post-fix: deferred to highscore/audio content work; this cleanup
            # keeps existing menu music behavior.
            elif next_state == GameState.GAME_OVER:
                music.play("menu")
                state = GameState.GAME_OVER

            elif next_state == GameState.MAIN_MENU:
                session.reset(config)
                music.play("menu")
                state = GameState.MAIN_MENU

        # Original review note: Game Over should register username for the
        # highscore screen and change music.
        # Post-fix: documented as follow-up; no highscore/audio content change
        # in this cleanup.
        elif state == GameState.GAME_OVER:
            for event in events:
                gameover_action = gameover_menu.handle_event(event)
                if gameover_action == "main menu":
                    state = GameState.MAIN_MENU
            gameover_menu.update(pygame.mouse.get_pos())
            gameover_menu.draw(screen)

        # Original review note: Victory needs the same transition/highscore
        # cleanup mentioned from IN_GAME.
        # Post-fix: documented as follow-up; no transition behavior added here.
        elif state == GameState.VICTORY:
            for event in events:
                victory_action = victory_menu.handle_event(event)
                if victory_action == "main menu":
                    state = GameState.MAIN_MENU
            victory_menu.update(pygame.mouse.get_pos())
            victory_menu.draw(screen)

        pygame.display.flip()
        clock.tick(60)
