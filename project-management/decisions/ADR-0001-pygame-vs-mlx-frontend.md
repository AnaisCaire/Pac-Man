# ADR-0001: Frontend graphics library — keep Pygame, constrained to MLX-equivalent calls

- Status: RED graphics/frontend items implemented; audio-as-separate-subsystem carve-out
  implemented with optional audio and graceful silent fallback in #15.
- Date: 2026-09-21 (matrix/ADR drafted); RED items replaced in `src/` same day
- Issue: #16 — [P0] Audit Pygame API against MLX-equivalence constraint
- Related: #10 (Harden UI and asset loading), #12 (Package, publish, and rehearse regeneration)

## Context

Pac-Man subject v1.5, Chapter IV, allows "MLX or a similar graphical library" only when every
relied-upon function has an MLX equivalent. The full call-by-call audit is in
[`../audits/pygame-mlx-api-matrix.md`](../audits/pygame-mlx-api-matrix.md). It found:

- 6 categories with a direct MLX equivalent (GREEN).
- 6 categories reachable in MLX only by hand-writing helpers on top of MLX primitives (AMBER):
  caption timing, backbuffer blit, event-loop architecture (poll vs. hook-driven), keycode
  mapping, PNG-vs-XPM asset format, and drawing primitives (rect/line/circle/polygon, since MLX
  only exposes `mlx_pixel_put`).
- 6 categories with **no** MLX equivalent at all (RED): alpha-blended blitting, runtime image
  scaling, TrueType/freetype text rendering, `pygame.font` rendering, `pygame.time.Clock`
  frame limiting, and `pygame.time.get_ticks()`.
- 1 category ruled out of scope for graphics equivalence: the audio mixer. Classic MLX has no
  audio API at all because it is a graphics library, so the subject's graphics-library
  equivalence clause does not apply to `pygame.mixer`. Audio remains a desired feature, tracked
  as optional audio with graceful silent fallback in #15.

## Decision

**Keep Pygame as the frontend, but stop relying on any Pygame convenience call that has no MLX
equivalent.** Concretely:

1. Every RED item is replaced by a small, tested, Pygame-agnostic helper that only performs what
   an MLX-based implementation would also have to hand-roll, in `src/ui/gfx/` and
   `src/game_logic/clock.py`:
   - `pygame.transform.scale` -> `ui/gfx/raster.nearest_neighbor_scale`, a hand-written resize
     over the raw pixel array. Pre-scaled static assets were considered instead, but `tile_size`
     is computed at runtime from `config.json`'s level dimensions (`WINDOW_SIZE //
     max(width, height)`), so there is no fixed set of sizes to bake ahead of time — the resize
     has to happen in code either way. The result is cached per `(sprite, tile_size)` so it only
     recomputes on a level change, not every frame.
   - `.convert_alpha()` + Pygame's implicit blit blending -> `ui/gfx/raster.blit_to_surface` /
     `composite_array`, which read/write RGBA pixel arrays directly (via `numpy` +
     `pygame.surfarray`) and do the alpha math by hand — real per-pixel alpha blending, not a
     color-key approximation, since the source PNGs already carry a genuine alpha channel and
     numpy makes the honest version cheap enough to keep.
   - `pygame.freetype` / `pygame.font.render` -> `ui/gfx/bitmap_font`, a hand-baked 5x7 glyph
     table (A-Z, 0-9, space, `:`, `!`) rendered to a pixel array per string, mirroring the fixed,
     size-less nature of `mlx_string_put`. Text is upper-cased; there is no lowercase glyph set.
   - `pygame.time.Clock` / `pygame.time.get_ticks()` -> `game_logic.clock.ProjectClock`
     (`time.monotonic()`-based), owned outside the rendering layer. `player.py`'s
     `update_timers`, `respawn`, `activate_power_up`, and `check_item_collision` now take
     `current_time: int` as an explicit parameter instead of reading a clock themselves — the
     same convention `Ghost.update(current_time, maze)` already followed, and required
     independent of this ADR by the project's own "no direct wall-clock/Pygame ticks in domain
     rules" guardrail.
   - Drawing primitives (`pygame.draw.*` — rect/line/circle/polygon) are **not** touched here:
     the matrix classifies them AMBER, not RED (a substitute is reachable via `mlx_pixel_put`
     loops, just not built yet), and replacing them isn't required by the Definition of Done.
     Left for a future issue if ever needed.
   - `numpy` is added as a dependency to make this pixel-buffer math vectorized rather than
     Python-level per-pixel loops, since the maze/ghost render path runs every frame.
2. Other AMBER items (window caption timing, backbuffer flip ordering, event-loop architecture,
   keycode mapping, PNG vs. XPM asset format) are left as Pygame calls as-is, since a real MLX
   port would need the exact same shape of code (hooks instead of polling, a keycode table, a
   fixed-format image loader) — the point is that our Pygame usage must already be written *as
   if* it were sitting on top of MLX, so the mapping is mechanical, not hand-wavy, if a port is
   ever required.
3. Audio stays behind `src/ui/music_manager.py` as an isolated non-graphics adapter. Music and
   sound effects use `pygame.mixer` when an audio device is available; mixer init/load/play
   failures degrade to a single clear warning and silent no-op behavior, without removing audio or
   forcing a dummy backend.

## Why not a real MLX port

- No MLX equivalent exists for TrueType text, alpha compositing, or image scaling at all — a
  real port would require us to hand-roll all three from scratch, which is a materially larger
  scope than what this issue asks for and is explicitly a non-goal ("does not authorize a
  big-bang frontend rewrite").
- MLX's event model (hook + `mlx_loop`) versus Pygame's poll loop is an architectural inversion,
  not a call substitution — attempting it now would touch every screen class for no additional
  subject compliance, since the subject only requires *function-level equivalence*, not literal
  MLX usage.
- The subject rule is satisfied for graphics/frontend calls once every retained Pygame graphics
  API is GREEN/AMBER-defensible, and every previously RED graphics behavior no longer depends on
  a non-equivalent Pygame API because it moved into project-owned code. That is achievable without
  a rewrite.

## Consequences

- New modules: `src/ui/gfx/raster.py` (scale + alpha composite), `src/ui/gfx/bitmap_font.py`
  (text), `src/game_logic/clock.py` (project clock) — each independently testable, and `numpy`
  added as a dependency.
- Menu/HUD text visually changes from antialiased Courier to a blocky retro pixel font. This is
  a real, visible product change, not just an internal refactor — flag it in review.
- `player.py` no longer reads a wall clock itself; `game_engine.py` passes `current_time` down
  explicitly, same as it already did for ghosts.
- Asset rework (issue #10) is unblocked for the PNG/XPM question specifically (still AMBER,
  unresolved — see the matrix); alpha/font/scaling policy is now settled and implemented, so
  issue #10 does not need to redo this work, only decide the loader format.
- Packaging (issue #12) does not need to bundle MLX or any MLX bindings.

## Audio carve-out behavior

**Audio.** Classic MLX has no mixer equivalent because it is not an audio library. This ADR treats
audio as a separate non-graphics subsystem rather than part of the Pygame -> MLX graphics
equivalence matrix. That does **not** mean removing audio: keep `pygame.mixer` for music/SFX when
available, isolated behind `src/ui/music_manager.py`. If mixer init, music loading, or playback
fails, emit one clear warning, switch to no-op/silent behavior, and let menu/gameplay continue
without a traceback.

## Verification

- [ ] Matrix in `../audits/pygame-mlx-api-matrix.md` peer-reviewed against cited MLX prototypes.
- [x] No RED item remains unresolved in `src/`: scaling, alpha compositing, fonts, and
      Clock/`get_ticks` are replaced by `src/ui/gfx/raster.py`, `src/ui/gfx/bitmap_font.py`, and
      `src/game_logic/clock.py`. (Drawing primitives (`pygame.draw.*`) were classified AMBER, not
      RED — a substitute is reachable but not required by the Definition of Done — and are left
      as Pygame calls; revisit only if a real MLX port is ever undertaken.)
- [x] `player.py` / `game_engine.py` no longer call `pygame.time.get_ticks()` directly; time is
      passed as an explicit `current_time` parameter, matching `Ghost.update()`'s convention.
- [x] `make lint` (flake8 + mypy strict) and `make test` pass with the replacements in place;
      the full menu/HUD/gameplay render path was additionally smoke-tested headlessly
      (SDL dummy driver) and visually inspected via screenshot.
- [x] README summarizes this decision with a link to this ADR.
- [x] Audio carve-out confirmed by #15 as optional audio with graceful silent fallback, not an
      audio-removal policy.
- [ ] Matrix/ADR peer review by teammate — PR should stay in draft until this happens.
