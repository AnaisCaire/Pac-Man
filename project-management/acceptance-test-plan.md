# Acceptance test plan

Snapshot: 2026-10-19.

The subject is accepted in layers. Automated source checks run first; graphical,
packaged and public-download checks remain manual because a passing unit test
cannot prove an installed game is usable.

## 1. Source quality gate

Run from a clean clone with Python 3.10+:

```console
make install
make clean
make lint
make test
uv lock --check
uv run python -m compileall -q pac-man.py src tests
```

Expected: zero flake8/mypy errors, all tests green, lock unchanged and no
traceback. PR #30 recorded 125 passing tests and 54 mypy-checked source files.
Rerun rather than reusing that historical count after later changes.

## 2. Configuration and dependency gate

- Launch exactly as `python3 pac-man.py config.json`.
- Probe missing file, malformed JSON, non-object root, unknown keys, wrong types,
  missing values, out-of-range dimensions and non-JSON extensions.
- Confirm clear warnings/defaults with no traceback.
- Reinstall and use the assigned unmodified A-Maze-ing 2.0.1 wheel.
- Confirm `perfect=False`, fixed first seed and random later seeds.
- Generate every delivered level and verify reachable spawn/items/ghosts.

## 3. Gameplay acceptance

- Start a normal game from Main Menu.
- Verify arrows and WASD, walls, pacgums, super-pacgums and configured scoring.
- Exercise lethal, frightened and same-frame super-pacgum collisions.
- Observe four ghost personalities, fleeing, visible dead eyes and exact respawn.
- Pause/resume without timer jumps; abandon only after confirmation.
- Complete levels while preserving score/lives; verify timeout, Game Over and
  final Victory after level 10.

## 4. Evaluator acceptance

With evaluator enabled:

- HUD visibly identifies the run and excludes it from highscores.
- `F` freezes/resumes simulation time.
- `G` cycles Blinky, Pinky, Inky, Clyde and NONE.
- `IJKL` moves only a selected ghost through walkable tiles.
- `I` with NONE toggles visible invincibility while frightened ghosts stay edible.
- A non-invincible death during Freeze consumes one life and respawns without
  leaving Freeze; the last life still reaches Game Over.
- `C` clears each level without awarding points.

## 5. UI and resource acceptance

At 800x900, inspect Main Menu, Highscores, Instructions, gameplay HUD, Pause,
Game Over, Victory and name entry for clipping/overlap. Remove or corrupt one
image and one audio track separately; confirm visible/silent fallbacks and one
clear warning without traceback.

## 6. Highscore acceptance

- Submit valid and invalid names after both win and loss.
- Keep a deterministic Top 10 and replace a repeated name.
- Recover missing/corrupt JSON without crash.
- Simulate a failed write and preserve prior data.
- Restart and confirm the board persists.

## 7. Packaged-build acceptance (pending #12)

For both Windows and Linux artifacts, outside the source checkout:

- install/launch from the packaged layout;
- verify bundled config, images, sounds, bitmap font and game flow;
- verify behavior with and without audio hardware;
- verify a writable highscore location and persistence across restart;
- execute Pause and evaluator-assisted win/loss;
- confirm no development-only path, `.venv`, `docs/`, `.hermes/`, cache, secret
  or local backup is included;
- record OS, artifact filename, size, SHA-256 and exact result.

## 8. Public-platform and regeneration acceptance (pending #12)

- Publish the verified build free and unlisted/private on Itch.io or equivalent.
- Download it from the public-platform URL on a clean environment.
- Repeat the packaged smoke against the downloaded artifact.
- Regenerate from a clean clone with the documented root script/spec while
  timing the operation.
- Record URL, artifact hash, elapsed build time, failures/fixes and final result.

## Exit criteria

Epic #1 closes only when every mandatory row is evidenced, #10–#12 are closed,
the public artifact is downloadable, and README/project evidence match the
released build rather than an earlier source-only snapshot.
