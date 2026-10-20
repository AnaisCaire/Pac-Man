# Acceptance test plan

Snapshot: 2026-10-20.

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
traceback. PR #32 recorded 130 passing tests and 56 mypy-checked source files on
both Windows and Linux. Rerun rather than reusing that historical count after
later changes.

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

## 7. Packaged-build acceptance

Verified from a clean clone on Windows and Linux x86_64:

- uv installs the locked dependencies and `make package` builds each native app;
- both archives contain executable, config, instructions, images and sounds;
- both extracted apps remain running outside the checkout with dummy SDL;
- both remain running with an intentionally unavailable audio driver;
- archive scans contain no `.venv`, `docs/`, `.hermes/`, cache, secret or backup;
- sizes, SHA-256 hashes and 26 s/30 s build times are recorded in
  `package-evidence.md`.

The team accepted the packaged gameplay and persistence flow for the published
release. The automated and external-startup evidence above was independently
recorded; the manual acceptance is a team confirmation rather than an agent-run
interactive transcript.

## 8. Public-platform and regeneration acceptance

- Clean-clone regeneration with the documented root script/spec: passed.
- Build timing and source-generated archive hashes: recorded in
  `package-evidence.md`.
- Free Itch.io page with visible Windows and Linux downloads: verified from the
  team-supplied screenshot at https://as3di0.itch.io/pac-man.
- Published game availability and final acceptance: confirmed by the team.
- Independent download/smoke by the agent: not performed because the release is
  not accessible to the agent; this limitation is recorded rather than inferred.

## Exit criteria

Epic #1 closes only when every mandatory row is evidenced, #10–#12 are closed,
the public artifact is downloadable, and README/project evidence match the
released build rather than an earlier source-only snapshot.
