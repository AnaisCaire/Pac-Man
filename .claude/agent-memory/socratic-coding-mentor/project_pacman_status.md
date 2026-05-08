---
name: Pacman project current status (May 2026)
description: What is actually implemented vs what the 42 subject requires, as of the MARIO review on 2026-05-08
type: project
---

Full code review completed on 2026-05-08. MARIO file written at repo root.

**Why:** Student asked for a complete itemized TODO list against the subject (v1.2).

**How to apply:** Use this to quickly orient to what is missing before diving into any specific task with the student.

## What IS implemented (working)
- Maze generation via mazegenerator package (perfect=False, seeded)
- Player movement: smooth sub-tile, turn buffering, respawn, death animation, invincibility window
- Ghost AI: 4 ghost types (Blinky/Pinky/Inky/Clyde), SCATTER/CHASE/FRIGHTENED/DEAD states, state timers, correct targeting algorithms
- Ghost collision: FRIGHTENED ghosts can be eaten; player dies to non-frightened ghosts
- Pacgum/super-pacgum collision: score added for both
- Power-up state: ghosts turn FRIGHTENED on super-pacgum, 5s duration
- 3 lives, respawn at center
- Time limit (90s default, configurable)
- Pause/resume via ESC (PauseScreen)
- Main menu: Start, Highscores, Instructions, Exit (all buttons functional)
- GameOver and Victory screens (but no name entry or score saving)
- HUD: score, time, lives, level displayed
- Music manager (menu.mp3 / game.mp3)
- Config: JSON with # comment support, defaults, clamping validation

## BLOCKING gaps (will fail peer review)
1. Only 3 levels in config.json (need 10+)
2. Levels 2+ seeded as config.seed + index, not random
3. Makefile missing: debug, clean, lint, lint-strict targets
4. pyproject.toml requires-python = ">=3.14" (should be 3.10+)
5. No MovingEntity base class (Player and Ghost are unrelated)
6. No Items class (pacgums are bare sets of tuples)
7. Eating a ghost does NOT add points_per_ghost to score (bug in check_ghost_collision)
8. WASD keys not implemented (only arrow keys)
9. GameOver screen: no name entry, no score saving
10. Victory screen: no name entry, no score saving
11. No highscore load/save module exists
12. HighscoreScreen shows nothing (just a Back button)
13. No cheat mode (invincibility, level skip, ghost freeze, extra lives, speed boost)
14. README missing italicized first line and all required sections
15. No packaging script at repo root
16. No Itch.io/Steam deployment
