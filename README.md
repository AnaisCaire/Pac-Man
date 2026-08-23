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

## Resources

- https://programmingpixels.com/handling-a-title-screen-game-flow-and-buttons-in-pygame.html
- https://thepythoncode.com/code/creating-pacman-game-with-python
- https://github.com/x4nth055/pythoncode-tutorials/tree/master/gui-programming/pacman-game
- https://www.pygame.org/docs/tut/newbieguide.html

### Sounds

- https://downloads.khinsider.com/game-soundtracks/album/pac-man-game-sound-effects 