"""Command-line entry point for Pac-Man."""

import argparse
from collections.abc import Sequence
import os


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for the public command-line interface."""
    parser = argparse.ArgumentParser(
        description="Start Pac-Man using a commented JSON configuration file.",
        epilog="Example: python3 pac-man.py config.json",
    )
    parser.add_argument(
        "config_file",
        metavar="CONFIG_FILE",
        help="path to the commented JSON configuration file",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """Parse command-line arguments and start the game."""
    parser = build_parser()
    arguments = parser.parse_args(argv)

    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    from src import game_loop, parse_config

    game_loop(parse_config(arguments.config_file))


if __name__ == "__main__":
    main()
