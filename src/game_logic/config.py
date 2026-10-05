import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_MIN_LEVEL_SIZE = 15
_MAX_LEVEL_SIZE = 18
_MIN_LEVELS = 10
_MIN_LEVEL_TIME = 15


@dataclass
class LevelMazeSize:
    """The maze size for one level."""

    width: int = 15
    height: int = 15


@dataclass
class Config:
    """All configuration values needed by the game."""

    highscore_filename: str = field(default="scores/high_scores.json")
    level: list[LevelMazeSize] = field(
        default_factory=lambda: [LevelMazeSize(width=15, height=15) for _ in range(10)]
    )
    lives: int = 3
    pacgum: int = 42
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    seed: int = 42
    level_max_time: int = 90
    evaluator_mode: bool = False


def _warning(field_name: str, message: str) -> None:
    """Log one precise configuration recovery warning."""
    logger.warning("%s: %s", field_name, message)


def _strip_full_line_comments(text: str) -> str:
    """Remove blank/comment lines without touching # inside JSON strings."""
    return "".join(
        line for line in text.splitlines(keepends=True)
        if line.strip() and not line.lstrip().startswith("#")
    )


def _int_value(
    raw: object,
    default: int,
    field_name: str,
    minimum: int | None = None,
) -> int:
    """Return a safe integer; bools and wrong types fall back to default."""
    if type(raw) is not int:
        _warning(
            field_name,
            f"expected integer, got {type(raw).__name__}; using {default}",
        )
        return default
    if minimum is not None and raw < minimum:
        _warning(field_name, f"must be >= {minimum}, got {raw}; using {default}")
        return default
    return raw


def _bool_value(raw: object, default: bool, field_name: str) -> bool:
    """Return a real JSON boolean, otherwise the default value."""
    if isinstance(raw, bool):
        return raw
    _warning(
        field_name,
        f"expected boolean, got {type(raw).__name__}; using {default}",
    )
    return default


def _string_value(raw: object, default: str, field_name: str) -> str:
    """Return a non-empty string, otherwise the default value."""
    if not isinstance(raw, str) or not raw:
        _warning(field_name, f"expected non-empty string; using {default}")
        return default
    return raw


def _level_size(raw: object, index: int) -> LevelMazeSize:
    """Normalize one level entry without invalidating its siblings."""
    default = LevelMazeSize()
    if not isinstance(raw, dict):
        _warning(f"level[{index}]", "expected object; using 15x15")
        return default

    width = _int_value(
        raw.get("width", default.width),
        default.width,
        f"level[{index}].width",
    )
    height = _int_value(
        raw.get("height", default.height),
        default.height,
        f"level[{index}].height",
    )
    if width < _MIN_LEVEL_SIZE:
        _warning(
            f"level[{index}].width",
            f"must be >= 15, got {width}; clamping to 15",
        )
        width = _MIN_LEVEL_SIZE
    if height < _MIN_LEVEL_SIZE:
        _warning(
            f"level[{index}].height",
            f"must be >= 15, got {height}; clamping to 15",
        )
        height = _MIN_LEVEL_SIZE
    if width > _MAX_LEVEL_SIZE:
        _warning(
            f"level[{index}].width",
            f"must be <= {_MAX_LEVEL_SIZE}, got {width}; clamping to {_MAX_LEVEL_SIZE}",
        )
        width = _MAX_LEVEL_SIZE
    if height > _MAX_LEVEL_SIZE:
        message = (
            f"must be <= {_MAX_LEVEL_SIZE}, got {height}; "
            f"clamping to {_MAX_LEVEL_SIZE}"
        )
        _warning(
            f"level[{index}].height",
            message,
        )
        height = _MAX_LEVEL_SIZE
    return LevelMazeSize(width=width, height=height)


def _levels_value(raw: object, default: list[LevelMazeSize]) -> list[LevelMazeSize]:
    """Normalize at least ten generator-safe levels."""
    if not isinstance(raw, list) or not raw:
        _warning("level", "expected non-empty list; using default levels")
        return default
    levels = [_level_size(item, index) for index, item in enumerate(raw)]
    if len(levels) < _MIN_LEVELS:
        _warning(
            "level",
            f"must contain {_MIN_LEVELS} levels; extending with 15x15",
        )
        levels.extend(LevelMazeSize() for _ in range(_MIN_LEVELS - len(levels)))
    return levels


def _config_from_dict(data: dict[str, Any]) -> Config:
    """Build a Config by validating each known key independently."""
    defaults = Config()
    return Config(
        highscore_filename=_string_value(
            data.get("highscore_filename", defaults.highscore_filename),
            defaults.highscore_filename,
            "highscore_filename",
        ),
        level=_levels_value(data.get("level", defaults.level), defaults.level),
        lives=_int_value(data.get("lives", defaults.lives), defaults.lives, "lives", 1),
        pacgum=_int_value(
            data.get("pacgum", defaults.pacgum),
            defaults.pacgum,
            "pacgum",
            0,
        ),
        points_per_pacgum=_int_value(
            data.get("points_per_pacgum", defaults.points_per_pacgum),
            defaults.points_per_pacgum,
            "points_per_pacgum",
            0,
        ),
        points_per_super_pacgum=_int_value(
            data.get("points_per_super_pacgum", defaults.points_per_super_pacgum),
            defaults.points_per_super_pacgum,
            "points_per_super_pacgum",
            0,
        ),
        points_per_ghost=_int_value(
            data.get("points_per_ghost", defaults.points_per_ghost),
            defaults.points_per_ghost,
            "points_per_ghost",
            0,
        ),
        seed=_int_value(data.get("seed", defaults.seed), defaults.seed, "seed"),
        level_max_time=_int_value(
            data.get("level_max_time", defaults.level_max_time),
            defaults.level_max_time,
            "level_max_time",
            _MIN_LEVEL_TIME,
        ),
        evaluator_mode=_bool_value(
            data.get("evaluator_mode", defaults.evaluator_mode),
            defaults.evaluator_mode,
            "evaluator_mode",
        ),
    )


def parse_config(path: str) -> Config:
    """Parse a commented JSON config file, recovering bad fields independently."""
    config_path = Path(path)
    if config_path.suffix != ".json":
        logger.warning("config path must end with .json: %s; using defaults", path)
        return Config()
    try:
        with config_path.open("r", encoding="utf-8") as config_file:
            content = _strip_full_line_comments(config_file.read())
        data = json.loads(content)
    except FileNotFoundError:
        logger.warning("config file not found: %s; using defaults", path)
        return Config()
    except OSError as error:
        logger.warning("cannot read config file %s: %s; using defaults", path, error)
        return Config()
    except json.JSONDecodeError as error:
        logger.warning("invalid JSON in %s: %s; using defaults", path, error)
        return Config()

    if not isinstance(data, dict):
        logger.warning("config root must be an object; using defaults")
        return Config()
    return _config_from_dict(data)
