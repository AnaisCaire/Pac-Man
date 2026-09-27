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

## A-Maze-ing package

The assigned external maze-generator artifact is tracked unchanged as
`mazegenerator-2.0.1-py3-none-any.whl` (version 2.0.1). Its SHA-256 checksum is
`f4b6828cd367570973bf901d90bbd6e5ae5cd4eb6d9cff18b1daa7b5c03599c3`.

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