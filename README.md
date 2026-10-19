*This project has been created as part of the 42 curriculum by masenjo, acaire-d.*

# Pac-Man

## Description

Pac-Man is a configurable recreation of the arcade game written in Python 3.10+
and rendered with Pygame. Each level uses the assigned A-Maze-ing package to
build a new maze containing Pac-Man, four ghosts, pacgums and four
super-pacgums. The game includes ten levels, persistent highscores, Pause,
evaluator controls, complete win/loss flows and graceful audio/image fallbacks.

The implementation keeps game rules separate from rendering and external I/O.
Small adapter boundaries cover maze generation, clocks, scores, audio and pixel
rendering without introducing a general framework.

## Requirements

- Python 3.10 or later.
- [uv](https://docs.astral.sh/uv/).
- A graphical environment supported by Pygame.

## Instructions

Install the locked dependencies:

```console
make install
```

Run the game with the delivered configuration:

```console
make run
```

The canonical direct invocation accepts exactly one JSON configuration path:

```console
python3 pac-man.py config.json
```

A different configuration can be supplied through Make:

```console
make run CONFIG=path/to/custom-name.json
```

The configuration filename itself is arbitrary, but both the configuration
file and `highscore_filename` must end in `.json`. Argument and configuration
errors produce clear messages without a Python traceback.

### Controls

| Key/input | Action |
|---|---|
| Arrow keys or `W` `A` `S` `D` | Move Pac-Man. |
| `Escape` | Open the Pause menu. |
| Mouse | Select menu and Pause actions. |
| Text, Backspace, Enter | Enter and submit a highscore name after Victory or Game Over. |

### Game flow

1. Main Menu → Start Game.
2. Eat every pacgum and super-pacgum before the level timer expires.
3. Keep the current score and remaining lives between levels.
4. Finish level 10 to win, or lose every life to reach Game Over.
5. Enter a name and submit the score.
6. Return to the Main Menu and use View Highscores to display the Top 10.

The HUD always shows score, lives, level and remaining time. Pause freezes the
complete simulation. Returning to the menu requires confirmation because the
current score is discarded.

### Evaluator mode

Evaluator mode helps peer reviewers reach difficult states quickly. It is off
in the delivered configuration and cannot be enabled from inside the game.
Create or edit a configuration with:

```json
"evaluator_mode": true
```

Evaluator runs are visibly marked and never saved to the highscore board.

| Key | Action |
|---|---|
| `F` | Toggle Evaluator Freeze. Pac-Man and collisions remain active; ghosts and simulation timers stop. |
| `G` | While frozen, cycle Blinky → Pinky → Inky → Clyde → no selected ghost. |
| `I` `J` `K` `L` | Move the selected ghost one valid tile up, left, down or right. |
| `I` with no selected ghost while frozen | Toggle invincibility; frightened ghosts remain edible. |
| `C` | Remove remaining collectibles and trigger the normal level-complete flow without awarding points. |

A lethal collision during Evaluator Freeze consumes one life and immediately
respawns Pac-Man without leaving Freeze, so the review session cannot become
stuck. The last life still ends the game normally.

## Configuration

The parser accepts standard JSON plus blank lines and full-line comments whose
first non-space character is `#`. A `#` inside a JSON string is preserved.
Unknown keys are ignored.

| Key | Default | Rules |
|---|---:|---|
| `highscore_filename` | `scores/high_scores.json` | Non-empty path ending in `.json`; any valid JSON filename is accepted. |
| `level` | ten `15x15` levels | Non-empty list; extended to at least 10 levels; width/height clamped to `15..18`. |
| `lives` | `3` | Integer at least 1. |
| `pacgum` | `42` | Non-negative integer. |
| `points_per_pacgum` | `10` | Non-negative integer. |
| `points_per_super_pacgum` | `50` | Non-negative integer. |
| `points_per_ghost` | `200` | Non-negative integer. |
| `seed` | `42` | Integer used only for the reproducible first level. |
| `level_max_time` | `90` | Integer of at least 15 seconds. |
| `evaluator_mode` | `false` | JSON boolean. |

Missing, unreadable or malformed configuration files recover to safe defaults.
Each missing or invalid field is recovered independently, and a clear warning
identifies the field and applied default or clamp. Python's standard `logging`
module is used; no logging dependency is required.

The delivered `config.json` contains ten 15x15–18x18 levels. The 18x18 cap
avoids a measured hang in the assigned generator at larger sizes.

## Highscore

The Main Menu provides a **View Highscores** action which opens the centered
`HALL OF FAME` view and displays up to ten player names and scores. This
satisfies the subject's Main Menu requirement without crowding the menu itself.

After Victory or Game Over, the player enters a name containing 1–10 ASCII
letters, numbers or spaces. Scores must be non-negative integers. The board is
sorted by descending score and deterministic name order; submitting the same
name replaces its previous entry.

JSON was chosen because it matches the project configuration format, is
human-readable and needs only the Python standard library. Writes are atomic:
the new board is written to a temporary file and then replaces the old file.
A failed save preserves the previous data. A missing file starts an empty
board; malformed JSON or an invalid top-level highscore structure logs a clear
warning and also recovers to an empty board without crashing.

Packaged builds store relative highscore paths in writable user data instead
of the installation directory: `%APPDATA%/Pac-Man/` on Windows and
`$XDG_DATA_HOME/pacman/` (or `~/.local/share/pacman/`) on Linux.

## Maze Generation

The assigned external artifact is tracked unchanged as
`mazegenerator-2.0.1-py3-none-any.whl`. Its SHA-256 checksum is:

```text
f4b6828cd367570973bf901d90bbd6e5ae5cd4eb6d9cff18b1daa7b5c03599c3
```

`src/game_logic/maze.py` is the only adapter to the package. It invokes
`MazeGenerator` with `perfect=False`, validates dimensions and cell values,
and converts import/generation/placement failures into a clear
`MazeGenerationError`.

Level 1 uses the configured fixed seed. Later levels receive random seeds from
an isolated RNG. Pacgum placement and frightened-ghost tie breaking also use
injected RNG instances, avoiding coupling to the generator's global random
state. Spawn, ghosts and both collectible types are placed only in reachable,
walkable cells.

## Implementation

- Pac-Man moves with queued four-direction input and tile interpolation.
- Pacgums, super-pacgums and edible ghosts award configurable points.
- Blinky targets Pac-Man; Pinky targets four tiles ahead; Inky uses Blinky and
  a two-tile pivot; Clyde chases while distant and targets home when close.
- Scatter and Chase use the existing greedy target rule. Frightened chooses a
  legal move maximizing squared distance from Pac-Man; RNG only breaks ties.
- Dead ghosts remain visible as eyes, travel at twice normal speed and use BFS
  to reach home. If home is unsafe, the eyes continue visibly to a safe corner
  and the ghost respawns exactly where they arrive.
- Scatter lasts 7 seconds and Chase 20 seconds. Frightened follows Pac-Man's
  power-up window. Pause and Evaluator Freeze use simulation time and resume
  without jumps.
- Missing or corrupt images render a visible placeholder. Audio initialization,
  loading or playback failures warn once and degrade to silence.

## General Software Architecture

- `pac-man.py`: command-line adapter and application entry point.
- `src/game_logic/config.py`: commented JSON parsing, validation and recovery.
- `src/game_logic/maze.py`: A-Maze-ing adapter, validation and placement.
- `src/game_logic/entities/`: player, ghost, item and collision rules.
- `src/game_logic/game_engine.py`: application state machine and level loop.
- `src/game_logic/evaluator.py`: reviewer-only state and commands.
- `src/game_logic/clock.py`: monotonic simulation clock independent of Pygame.
- `src/scores/`: validated score model and atomic JSON persistence.
- `src/ui/screens/`: menus, Pause and score-entry screens.
- `src/ui/gameplay/`: maze, entity and HUD rendering.
- `src/ui/gfx/`: bitmap text, nearest-neighbor scaling and alpha compositing.
- `src/ui/music_manager.py`: optional Pygame mixer adapter with silent fallback.

The project keeps rules and persistence testable without opening a display.
Pygame remains at input/render/audio boundaries. The frontend decision and
function-by-function MLX-equivalence audit are recorded in project management.

## Development

| Command | Purpose |
|---|---|
| `make install` | Synchronize the uv environment. |
| `make run` | Launch with `CONFIG`, defaulting to `config.json`. |
| `make debug` | Start under Python's built-in `pdb`. |
| `make clean` | Remove Python and analysis caches. |
| `make lint` | Run flake8 and mypy with the subject's mandatory flags. |
| `make test` | Run the unittest suite. |
| `make package` | Build and archive the native PyInstaller package for the current OS. |

Every production class and function has a purpose docstring, and public
boundaries use type hints. Behavior changes are protected with focused tests
before the full quality gates.

## Packaging

Packaging uses the checked-in `pac-man.spec` through `scripts/package.py` and
the uv development environment. `make package` creates one native `onedir`
bundle and archive under `dist/`:

- `pac-man-windows-x86_64.zip` when run on Windows;
- `pac-man-linux-x86_64.tar.gz` when run on Linux x86_64.

PyInstaller does not cross-compile, so each artifact must be generated on its
target operating system. The executable launches with the editable
`config.json` beside it; command-line users may still supply another JSON path.
`PACKAGE-INSTRUCTIONS.txt` is included at the package root. Build directories
and archives remain ignored; release evidence records their hashes and smoke
results in `project-management/package-evidence.md`.

## Project Management

The recovery roadmap is tracked through GitHub issues, reviewed pull requests,
a milestone and Project 11. Versioned evidence is indexed in the
[project-management directory](project-management/README.md), including:

- [retrospective timeline and Gantt](project-management/timeline.md);
- [planned work versus actual delivery](project-management/progress.md);
- [risk register](project-management/risks.md);
- [acceptance test plan](project-management/acceptance-test-plan.md);
- [package and regeneration evidence](project-management/package-evidence.md);
- [ADR-0001: Pygame vs. MLX frontend](project-management/decisions/ADR-0001-pygame-vs-mlx-frontend.md);
- [Pygame/MLX API matrix](project-management/audits/pygame-mlx-api-matrix.md).

Completed dates and status are reconstructed from GitHub records. Team roles
and decision-process evidence remain pending confirmation from both
contributors; packaging and deployment rows remain pending until #12 produces
real Windows/Linux artifacts and a verified Itch.io URL.

## Resources

### Technical references

- [Python documentation](https://docs.python.org/3/)
- [Pygame documentation](https://www.pygame.org/docs/)
- [uv documentation](https://docs.astral.sh/uv/)
- [MiniLibX prototypes](https://harm-smits.github.io/42docs/libs/minilibx/prototypes.html)
- [Handling a title screen, game flow and buttons](https://programmingpixels.com/handling-a-title-screen-game-flow-and-buttons-in-pygame.html)
- [Python Pac-Man tutorial](https://thepythoncode.com/code/creating-pacman-game-with-python)
- [Pac-Man tutorial source](https://github.com/x4nth055/pythoncode-tutorials/tree/master/gui-programming/pacman-game)

### Assets

- Pac-Man sound references: [KHInsider Pac-Man sound effects](https://downloads.khinsider.com/game-soundtracks/album/pac-man-game-sound-effects).
- The assigned A-Maze-ing wheel was provided by another student group and is
  used byte-for-byte without modification.

Final asset source/license attribution will be verified alongside packaging
before publication; unverified provenance will not be invented.

### Use of AI

AI tools were used to support repository auditing, requirement extraction,
implementation planning, test design, code review, documentation structure and
small code changes. Generated suggestions were not accepted as evidence on
their own: behavior was checked against Pac-Man subject v1.5, reviewed through
Git diffs and pull requests, and exercised with targeted tests, the complete
suite, flake8, mypy, configuration smokes and manual graphical checks.

The students remain responsible for understanding, explaining and modifying
all submitted code during peer review.
