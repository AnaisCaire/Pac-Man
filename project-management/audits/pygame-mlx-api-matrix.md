# Pygame -> MLX equivalence matrix

Issue: [P0] Audit Pygame API against MLX-equivalence constraint (#16)
Subject reference: Pac-Man subject v1.5, Chapter IV ("MLX or similar" clause).

MLX ground truth used below is the canonical header, not blog posts:
https://github.com/42Paris/minilibx-linux/blob/master/mlx.h
(cross-checked against https://harm-smits.github.io/42docs/libs/minilibx/prototypes.html)

Legend:
- GREEN: a direct MLX function/capability exists, call-for-call or via a trivial reshape.
- AMBER: the capability is reachable in MLX, but only by writing our own helper on top of
  MLX primitives (no ready-made MLX call). Bridgeable, must be built and tested.
- RED: no MLX capability exists at all (classic MLX has nothing comparable). Requires an
  explicit product decision, not a code substitution.
- RESOLVED: a previously RED graphics/frontend dependency that no longer relies on a
  non-equivalent Pygame API because the behavior moved into project-owned code,
  per [`../decisions/ADR-0001-pygame-vs-mlx-frontend.md`](../decisions/ADR-0001-pygame-vs-mlx-frontend.md).
- OUT OF SCOPE: not part of the graphics-library equivalence question. Audio is a separate
  subsystem; it may keep using `pygame.mixer` behind an adapter when available.

## A. Window & display lifecycle

| Pygame call | File:line | MLX equivalent | Verdict |
|---|---|---|---|
| `pygame.init()` / `pygame.quit()` | `game_engine.py:156,85,93,182,199` | `mlx_init()` (no bulk teardown call; window/image destroys are explicit) | GREEN |
| `pygame.display.set_mode((w, h))` | `game_engine.py:159` | `mlx_new_window(mlx, size_x, size_y, title)` | GREEN (MLX windows are fixed-size at creation, matches our fixed `WINDOW_SIZE`) |
| `pygame.display.set_caption(str)` | `game_engine.py:160` | title argument of `mlx_new_window` (title is set once, at creation, no later rename call in MLX) | AMBER (needs reordering: pass title at construction instead of after) |
| `pygame.display.flip()` | `game_engine.py:108,151,260` | `mlx_put_image_to_window(mlx, win, img, x, y)` per frame | AMBER (MLX has no implicit backbuffer swap; you render into an off-screen `mlx_new_image` buffer via `mlx_get_data_addr` and blit it yourself) |

## B. Event loop

| Pygame call | File:line | MLX equivalent | Verdict |
|---|---|---|---|
| `pygame.event.get()` (poll queue, per frame) | `game_engine.py:81,91,179` | No poll queue in MLX. Input is callback-driven: `mlx_key_hook`, `mlx_mouse_hook`, `mlx_hook` (generic X event, e.g. close button), all pumped by `mlx_loop(mlx)` | AMBER (capability exists but the *architecture* is inverted: register hooks once, don't poll each frame) |
| `event.type == pygame.QUIT` | `game_engine.py:85,93,182` | `mlx_hook` on a window-close/DestroyNotify event | GREEN |
| `event.type == pygame.KEYDOWN`, `event.key == pygame.K_*` | `game_engine.py:87,97`; `player.py:167-174` | `mlx_key_hook(win, f, param)` delivers raw X11 keycodes, not named constants | AMBER (capability exists, but keycodes are platform-specific ints; needs our own keycode-name mapping table) |
| `pygame.mouse.get_pos()` | `game_engine.py:106,201,209,217,249,257` | `mlx_mouse_get_pos(mlx, win, &x, &y)` | GREEN |

## C. Asset loading (PNG + alpha)

| Pygame call | File:line | MLX equivalent | Verdict |
|---|---|---|---|
| `pygame.image.load(path)` | `main_menu.py:26`, `sub_screens.py:56,92`, `gameover.py:24`, `victory.py:21`, `ghost_draw.py:17-30` | `mlx_xpm_file_to_image` (guaranteed, declared in canonical `mlx.h`) *or* `mlx_png_file_to_image` (advertised on the 42docs prototypes page but **absent from the official 42Paris `mlx.h`** — a fork/platform extension, not guaranteed) | AMBER/RED — needs an explicit format policy before touching assets. See decision below. |
| `.convert_alpha()` (per-pixel alpha compositing on blit) | same files as above, plus `bottons.py:18` | **No equivalent anywhere in `mlx.h`.** `mlx_put_image_to_window` has no blending/alpha parameter. | RESOLVED — `.convert_alpha()` removed; images are loaded as raw RGBA arrays (`ui/gfx/raster.load_rgba`) and composited by hand (`ui/gfx/raster.blit_to_surface` / `composite_array`), the same per-pixel work an MLX renderer would do via `mlx_get_data_addr`. |

## D. Runtime scaling

| Pygame call | File:line | MLX equivalent | Verdict |
|---|---|---|---|
| `pygame.transform.scale(img, (w, h))` | `main_menu.py:31`, `sub_screens.py:63,97`, `gameover.py:31`, `victory.py:28`, `ghost_draw.py:55` | **None.** No resize/scale function exists in `mlx.h`. | RESOLVED — replaced with a hand-written nearest-neighbor resize on the raw pixel array (`ui/gfx/raster.nearest_neighbor_scale`). Ghost sprites (the only per-frame case, since `tile_size` varies with level size) are additionally cached per `(sprite, tile_size)` so the resize only recomputes on a level change, not every frame. |

## E. Fonts / text rendering

| Pygame call | File:line | MLX equivalent | Verdict |
|---|---|---|---|
| `pygame.freetype.SysFont(...).render(...)` | `bottons.py:16-17` | `mlx_string_put(mlx, win, x, y, color, str)` — single fixed bitmap font, no size/bold/antialiasing control. `mlx_set_font` exists but is Linux-only and still just an X11 core font name, not a size/weight API. | RESOLVED — replaced with a hand-baked 5x7 pixel font (`ui/gfx/bitmap_font`), covering only the characters the UI actually uses (A-Z, 0-9, space, `:`, `!`; text is upper-cased). Visual trade-off: menu/HUD text is now a blocky pixel font instead of antialiased Courier. |
| `pygame.font.SysFont(None, 36).render(...)` | `game_engine.py:162`, `hud.py:21-38` | same as above | RESOLVED — same `ui/gfx/bitmap_font` helper; `hud.draw_legend` no longer takes a `pygame.font.Font` argument at all. |

## F. Drawing primitives

| Pygame call | File:line | MLX equivalent | Verdict |
|---|---|---|---|
| `pygame.draw.rect/line/polygon/circle` | `maze_draw.py:18-75`, `hud.py:15`, `player_draw.py:43,51` | Only `mlx_pixel_put(mlx, win, x, y, color)` exists — a single-pixel primitive. No rect/line/circle/polygon calls anywhere in `mlx.h`. | AMBER (every primitive is reachable as a loop of `mlx_pixel_put` calls — nested loop for rect, Bresenham for line, midpoint algorithm for circle — but we would be writing and testing our own helpers, not calling a library function) |

## G. Rect / hit-testing objects

| Pygame call | File:line | MLX equivalent | Verdict |
|---|---|---|---|
| `pygame.Rect`, `surface.get_rect(...)`, `rect.collidepoint(...)` | `bottons.py:56,60`, `main_menu.py:32,52`, `sub_screens.py:64,98,28,68,116`, `gameover.py:32,36`, `victory.py:29,33` | N/A — this is plain point-in-rectangle arithmetic, not a rendering capability. MLX has no `Rect` type because it was never in scope for a graphics library. | GREEN, but flagged: this should be reimplemented as a small pygame-independent geometry helper regardless of the MLX decision, per the "keep geometry outside the graphics dependency" guardrail — hit-testing should not depend on `pygame.Rect`. |

## H. Timing / frame limiting

| Pygame call | File:line | MLX equivalent | Verdict |
|---|---|---|---|
| `pygame.time.Clock()` + `clock.tick(fps)` | `game_engine.py:161` (used for FPS cap) | **None.** No delay/clock/FPS-limiter symbol anywhere in `mlx.h`; frame pacing under MLX is entirely the caller's own responsibility (typically `mlx_loop_hook` + your own OS-clock timer). | RESOLVED — replaced by `game_logic.clock.ProjectClock`, a `time.monotonic()`-based clock with the same `tick(fps)` contract. |
| `pygame.time.get_ticks()` | `game_engine.py:67,80,88,110`; `player.py:83,96,100,106,131,136` | Same gap — no MLX ticks function. | RESOLVED — replaced by `ProjectClock.get_ticks_ms()`. |

**Separate compliance flag, now fixed as part of this resolution:** `pygame.time.get_ticks()`
was called directly inside `src/game_logic/entities/player.py` (domain/entity code), violating
this project's own architecture guardrail ("no direct wall-clock/Pygame ticks in domain rules").
`Player.update_timers`, `.respawn`, `.activate_power_up` and `.check_item_collision` now take
`current_time: int` as an explicit parameter instead of reading a clock themselves — the same
convention `Ghost.update(current_time, maze)` already followed.

## I. Mixer / audio

| Pygame call | File:line | MLX equivalent | Verdict |
|---|---|---|---|
| `pygame.mixer.init()`, `pygame.mixer.music.load/play/stop` | `music_manager.py:35-42`, `game_engine.py:157` | **None.** Classic MLX has zero audio-related symbols because it is a graphics library, not an audio API. | OUT OF SCOPE — audio is a separate non-graphics subsystem. Keep music/SFX via `pygame.mixer` when an audio device is available, isolated behind `music_manager.py` or an equivalent adapter, and track optional audio with graceful silent fallback in #15. |

## Summary counts

| Verdict | Count | Categories |
|---|---|---|
| GREEN | 6 | window init, `set_mode`, QUIT event, mouse position, Rect/hit-testing (geometry, not a lib call) |
| AMBER | 6 | caption timing, `flip`/backbuffer, event-loop architecture, keycodes, image format policy, drawing primitives |
| RESOLVED (was RED) | 6 | alpha compositing, runtime scaling, freetype text, `font.render`, Clock/tick, `get_ticks` |
| OUT OF SCOPE | 1 | audio mixer (no graphics-library equivalence applies) |

No unresolved RED graphics/frontend dependency remains in `src/` — all six no longer depend on
non-equivalent Pygame APIs because the behavior moved into helpers in `src/ui/gfx/` and
`src/game_logic/clock.py`. See `../decisions/ADR-0001-pygame-vs-mlx-frontend.md` for the
reasoning behind each replacement.

Audio is not a RED graphics item to resolve by deletion or an MLX port. It is a separate
non-graphics subsystem: keep music/SFX via `pygame.mixer` when available, and make #15 provide
optional audio with graceful silent fallback when mixer init or asset playback fails.
