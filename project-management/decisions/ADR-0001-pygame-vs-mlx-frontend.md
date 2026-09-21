# ADR-0001: Frontend graphics library — keep Pygame, constrained to MLX-equivalent calls

- Status: PROPOSED (needs team sign-off before issue #16 closes; audio carve-out needs
  explicit agreement, see "Open question" below)
- Date: 2026-09-21
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
- 1 category ruled out of scope: the audio mixer. Classic MLX has no audio API at all, so the
  subject's graphics-library equivalence clause does not apply to it; it's tracked against the
  parallel no-audio P0 issue instead of resolved here.

## Decision

**Keep Pygame as the frontend, but stop relying on any Pygame convenience call that has no MLX
equivalent.** Concretely:

1. Every RED item is replaced by a small, tested, Pygame-agnostic helper that only performs what
   an MLX-based implementation would also have to hand-roll:
   - Drawing primitives (`pygame.draw.*`) -> our own rect/line/circle/polygon helpers built from
     per-pixel writes, mirroring what a `mlx_pixel_put` loop would do. (Currently AMBER because a
     substitute is straightforward; still gets its own helper module either way.)
   - `pygame.transform.scale` -> no runtime scaling. Ship pre-scaled asset variants at the exact
     tile sizes the game uses (asset policy decision, see below), matching the fact that MLX has
     no resize call either.
   - `pygame.freetype` / `pygame.font.render` -> decide and implement one bitmap-font/text
     strategy that would also work against `mlx_string_put`'s constraints (fixed glyphs, single
     color per draw), rather than depending on arbitrary TrueType rendering.
   - `.convert_alpha()` -> replace real alpha-blend compositing with an explicit transparent
     color-key convention on load, since neither MLX nor our own pixel-loop blit gets free alpha
     blending.
   - `pygame.time.Clock` / `pygame.time.get_ticks()` -> a project clock (`time.monotonic()`
     based) owned outside the rendering layer and injected into anything that needs elapsed time,
     including `game_logic/entities/player.py` and `game_engine.py`, which currently call
     `pygame.time.get_ticks()` directly from domain code. This is required independent of this
     ADR, per the project's own "no direct wall-clock/Pygame ticks in domain rules" guardrail.
2. AMBER items (window caption timing, backbuffer flip ordering, event architecture, keycode
   table, PNG vs. XPM) are left as Pygame calls as-is, since a real MLX port would need the exact
   same shape of code (hooks instead of polling, a keycode table, a fixed-format image loader) —
   the point is that our Pygame usage must already be written *as if* it were sitting on top of
   MLX, so the mapping is mechanical, not hand-wavy, if a port is ever required.
3. Audio stays behind `src/ui/music_manager.py` as an isolated adapter, explicitly justified as
   outside the graphics-library equivalence clause, pending the no-audio P0 issue's own decision.

## Why not a real MLX port

- No MLX equivalent exists for TrueType text, alpha compositing, or image scaling at all — a
  real port would require us to hand-roll all three from scratch, which is a materially larger
  scope than what this issue asks for and is explicitly a non-goal ("does not authorize a
  big-bang frontend rewrite").
- MLX's event model (hook + `mlx_loop`) versus Pygame's poll loop is an architectural inversion,
  not a call substitution — attempting it now would touch every screen class for no additional
  subject compliance, since the subject only requires *function-level equivalence*, not literal
  MLX usage.
- The subject rule is satisfied once every retained call is either GREEN, or AMBER/RED-resolved
  by a helper that only assumes MLX-shaped capabilities. That is achievable without a rewrite.

## Consequences

- New work: rect/line/circle/polygon pixel-loop helpers, a bitmap-font/text helper, a project
  clock module, and a pre-scaled asset pipeline — each independently testable.
- `player.py` and `game_engine.py` must stop importing time from Pygame directly; they take a
  clock dependency instead.
- Asset rework (issue #10) is blocked on the PNG/XPM + alpha + font + scaling policy decided
  here — do not touch assets before this ADR is accepted.
- Packaging (issue #12) does not need to bundle MLX or any MLX bindings.

## Open question requiring explicit team sign-off

**Audio.** Classic MLX has no mixer equivalent. This ADR proposes treating audio as out of scope
for the graphics-equivalence clause rather than dropping it — but that argument needs to be one
the team can make to an evaluator, not just asserted here. Confirm this against whatever the
no-audio P0 issue concludes before closing #16.

## Verification

- [ ] Matrix in `../audits/pygame-mlx-api-matrix.md` peer-reviewed against cited MLX prototypes.
- [ ] No RED item remains unresolved in `src/` (rect/line/circle/polygon, scaling, fonts, alpha,
      clock/ticks all replaced by the helpers described above).
- [ ] `player.py` / `game_engine.py` no longer call `pygame.time.get_ticks()` directly.
- [ ] README summarizes this decision with a link to this ADR.
- [ ] Audio carve-out confirmed against the no-audio P0 issue's outcome.
