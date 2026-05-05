import os, json, logging
from dataclasses import dataclass, field
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LevelMazeSize:
    """ The maze size for one level"""
    width: int = 15
    height: int = 15

@dataclass
class Config:
    """
    all needed configuration values from config file
    """
    highscore_filename: str = field(default="scores/high_scores.json")
    level: List[LevelMazeSize] = field(
        default_factory=lambda: [LevelMazeSize(width=15, height=15) for _ in range(10)]
    )
    lives: int = 3
    pacgum: int = 42
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    seed: int = 42
    level_max_time: int = 90

def validate_config(config: Config) -> Config:
    """ verify values """
    defaults = Config()
    if config.lives < 1:
        logger.error(f"lives must be >= 1 (got {config.lives}). \
Clamping to {defaults.lives}.")
        config.lives = defaults.lives

    if config.level_max_time < 15:
        logger.error(f"level_max_time must be >= 15 (got {config.level_max_time}). \
Clamping to {defaults.level_max_time}.")
        config.level_max_time = defaults.level_max_time

    if config.points_per_pacgum < 0:
        logger.error(f"points_per_pacgum cannot be negative. \
Clamping to {defaults.points_per_pacgum}.")
        config.points_per_pacgum = defaults.points_per_pacgum

    if config.points_per_super_pacgum < 0:
        logger.error(f"points_per_super_pacgum cannot be negative. \
Clamping to {defaults.points_per_super_pacgum}.")
        config.points_per_super_pacgum = defaults.points_per_super_pacgum

    if config.points_per_ghost < 0:
        logger.error(f"points_per_ghost cannot be negative. \
Clamping to {defaults.points_per_ghost}.")
        config.points_per_ghost = defaults.points_per_ghost

    if not config.level or len(config.level) < 1:
        logger.error("Game requires at least 1 level. Clamping to default level set.")
        config.level = defaults.level

    for i, lvl in enumerate(config.level):
        if lvl.width < 15 or lvl.height < 15:
            logger.error(f"Level {i} size ({lvl.width}x{lvl.height}) is too small \
for the '42' logo. Clamping to 15x15.")
            lvl.width = max(15, lvl.width)
            lvl.height = max(15, lvl.height)
    return config

def parse_config(path: str) -> Config:
    """
    Parse the config
    """
    if not os.path.exists(path):
        logger.error(f"Config file not found at {path}. Using default configuration.")
        return Config()
    try:
        with open(path, 'r') as f:
            content = "".join(line for line in f if not
                            line.strip().startswith('#'))
            res_dict = json.loads(content)
            if 'level' in res_dict:
                res_dict['level'] = [LevelMazeSize(**lvl) for lvl in res_dict['level']]
            return validate_config(config=Config(**res_dict))
    except(json.JSONDecodeError, TypeError, KeyError) as e:
        logger.error(f"Invalid config data in {path}: {e}. Clamping to defaults.")
        return Config()