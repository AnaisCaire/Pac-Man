# Pac-Man
Recreate the famous arcade game Pac-Man with a modern Python codebase, a clean
project structure, and a deployable build.

## Requirements

- Python 3.10 or later
- [uv](https://docs.astral.sh/uv/)

## Installation

```console
make install
```

## Usage

Pac-Man accepts exactly one positional argument: the path to its commented
JSON configuration file.

```console
python3 pac-man.py config.json
```

The Makefile launches the same command with the repository configuration:

```console
make run
```

To launch a different configuration through Make:

```console
make run CONFIG=path/to/config.json
```

Use the built-in help for the complete command-line explanation:

```console
python3 pac-man.py --help
```

Invalid argument counts print a concise usage error to standard error and exit
without starting the game.

Configuration files must use the `.json` extension. Blank lines and full-line
comments whose first non-space character is `#` are allowed; `#` characters
inside JSON strings are preserved. Unknown keys are ignored. Missing,
unreadable, malformed, or unsafe values are reported clearly and recovered with
safe defaults or clamps without discarding valid sibling settings.

## Development commands

| Command | Purpose |
|---|---|
| `make install` | Create or synchronize the uv environment. |
| `make lint` | Run flake8 and the mandatory mypy checks. |
| `make test` | Run the automated CLI contract tests. |
| `make debug` | Start Pac-Man under Python's built-in `pdb` debugger. |
| `make clean` | Remove Python caches and local analysis output. |


## Evaluator mode (cheat mode)

Evaluator mode exists so a peer reviewer can reach every game state quickly. It
is off in the delivered `config.json` and cannot be switched on from inside the
game, so a normal player can never trigger it by accident.

To enable it, copy the configuration, set the key to `true`, and launch with
the copy:

```jsonc
"evaluator_mode": true
```

```console
make run CONFIG=path/to/evaluator_config.json
```

While it is enabled, the HUD always shows `EVALUATOR` in the bottom-left
corner. With it disabled, all evaluator keys do nothing.

| Key | Action | Repeated presses |
|---|---|---|
| `F` | Evaluator Freeze: ghosts stop moving; the level timer, power-pellet, respawn, invincibility and ghost state timers stop. Pac-Man still moves, eats, and collides. The HUD adds `FREEZE`. | Toggles. Unfreezing continues every timer from where it stopped, without a jump. |
| `G` | Select the next ghost while frozen. The HUD shows `SELECTED` and its name. | Cycles Blinky, Pinky, Inky, Clyde. Does nothing outside Freeze. |
| `I` `J` `K` `L` | Move the selected ghost one walkable tile up, left, down, or right while frozen. | Each valid key press moves one tile; walls and map edges are ignored. |
| `C` | Clear level: removes every remaining pacgum and super-pacgum, so the normal level-complete transition runs. No points are awarded. | Idempotent. Waits for an ongoing death to resolve first. |

Pause and Evaluator Freeze are different:

| | `Escape` Pause | `F` Evaluator Freeze |
|---|---|---|
| Available | Always | Only in evaluator mode |
| Screen | Pause menu | Normal game view with `FREEZE` on the HUD |
| Pac-Man | Stopped | Moves, eats, and collides |
| Ghosts | Stopped | Stopped |
| Level, power-pellet, respawn and ghost timers | Stopped | Stopped |

The two combine safely: pausing while frozen and resuming leaves the game
frozen, with no time jump.

Evaluator runs are never saved: the Game Over and Victory screens show
`EVALUATOR RUN` / `SCORE NOT SAVED` and Enter returns to the main menu. Test
highscore saving with evaluator mode off.

### Reviewer walkthrough

With evaluator mode enabled:

1. **Freeze and Pause**: press `F` (ghosts and `TIME` stop, Pac-Man moves),
   `Escape` then Resume (still frozen), `F` again (time continues).
2. **Ghost selection and movement**: while frozen, press `G` to cycle through
   all four ghosts and use `I`/`J`/`K`/`L` to place the selected ghost.
3. **Power pellet, frightened and eaten ghosts**: freeze, eat a super-pacgum
   (ghosts stay frightened while frozen), place a ghost on Pac-Man to eat it,
   unfreeze and watch it return home.
4. **Death and Game Over**: freeze and place a non-frightened ghost on Pac-Man;
   the respawn waits until unfreeze. Repeat until no lives remain.
5. **Level and final victory**: press `C` on each level; `C` on level 10 shows
   the Victory screen.
6. **Timeout**: set `level_max_time` to its minimum of `15` in the evaluator
   configuration and wait.

With evaluator mode disabled:

7. **Highscore save**: lose all lives, enter a name, and check the Highscores
   menu.

## Gameplay progression and controls

- Use either the arrow keys or W/A/S/D to move Pac-Man in the four required
  directions. Both schemes set the same queued direction, so pressing their
  matching keys together never doubles movement.
- Press `Escape` during a level to pause. Resume continues the same session;
  Return to Menu asks for confirmation before discarding it. The next game
  starts with level 1, score 0, and the configured lives.
- The level timer, power-pellet, player respawn/invincibility, and ghost state
  timers all use simulation time and do not advance while paused.
- A lethal collision also pauses only the level countdown until the player
  respawns; death animation and respawn processing continue normally. During
  that transition Pac-Man cannot collect items, ghosts are frozen, and any
  ghost within five tiles of the respawn is moved to a free distant corner.
- Reaching the time limit ends the current game in Game Over. Timeout takes
  priority over same-frame gameplay actions.
- Completing a level keeps score and remaining lives. Completing the tenth
  configured level wins the game.

The delivered `config.json` contains ten 15x15–18x18 levels. The 18x18 cap
avoids a known hang in the assigned maze generator at larger sizes. Level 1
uses the configured seed; later levels use isolated random seeds.

## Highscores

After a win or loss, enter a name of 1–10 ASCII letters, numbers, or spaces
under `INSERT NAME`, then press Enter to submit. The game stores a deterministic
Top 10 sorted by descending score then name. Missing or corrupt score files
recover to an empty board.

`highscore_filename` is used exactly as configured. The delivered configuration
stores scores in `scores/high_scores.json`; each submitted name replaces that
name's prior entry before the board is sorted. Writes use a temporary file
followed by replacement, so a failed save preserves the prior board.

## A-Maze-ing package

The assigned external maze-generator artifact is tracked unchanged as
`mazegenerator-2.0.1-py3-none-any.whl` (version 2.0.1). Its SHA-256 checksum is
`f4b6828cd367570973bf901d90bbd6e5ae5cd4eb6d9cff18b1daa7b5c03599c3`.

Maze generation is wrapped by `src/game_logic/maze.py`, which calls the package
with `perfect=False`, validates generated grids before gameplay, and keeps the
first level on the configured fixed seed. Later levels receive random seeds from
an isolated level-seed RNG; pacgum placement and frightened ghost choices also
use injected RNG sources instead of sharing module-global randomness.

## Project management

- Frontend library decision (Pygame vs. MLX-equivalence audit):
  [`project-management/decisions/ADR-0001-pygame-vs-mlx-frontend.md`](project-management/decisions/ADR-0001-pygame-vs-mlx-frontend.md),
  backed by the full call-by-call matrix in
  [`project-management/audits/pygame-mlx-api-matrix.md`](project-management/audits/pygame-mlx-api-matrix.md).
  Decision: keep Pygame, but every call with no MLX equivalent is replaced by a small tested
  helper that assumes only MLX-shaped capabilities. Implemented in `src/ui/gfx/` (image scaling,
  alpha compositing, a hand-baked pixel font replacing TrueType text) and
  `src/game_logic/clock.py` (a `time.monotonic()` project clock replacing `pygame.time.Clock`
  and `pygame.time.get_ticks()`, including in `Player`, which previously read the wall clock
  directly from domain code). Audio is a separate non-graphics subsystem: `pygame.mixer` is kept
  behind `src/ui/music_manager.py` when available, and gracefully falls back to silent no-op
  behavior with one warning when mixer initialization or playback fails.

## Resources

- https://programmingpixels.com/handling-a-title-screen-game-flow-and-buttons-in-pygame.html
- https://thepythoncode.com/code/creating-pacman-game-with-python
- https://github.com/x4nth055/pythoncode-tutorials/tree/master/gui-programming/pacman-game
- https://www.pygame.org/docs/tut/newbieguide.html

### Sounds

- https://downloads.khinsider.com/game-soundtracks/album/pac-man-game-sound-effects

Note: the bundled gameplay music at `src/ui/sounds/game.mp3` was refreshed on
`main` before the scoring/collision PR branch was fast-forwarded.
