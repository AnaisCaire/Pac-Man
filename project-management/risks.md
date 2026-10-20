# Risk register

Snapshot: 2026-10-19. Probability and impact are qualitative and reassessed at
slice boundaries.

| Risk | Probability / impact | Mitigation and evidence | State |
|---|---|---|---|
| Unsupported Python/tooling baseline | Low / High | Python 3.10+, mandatory Make rules, flake8, mypy and tests in PR #14 | Closed |
| Pygame uses APIs with no MLX equivalent | Low / High | API matrix, ADR and replacement pixel/clock helpers in PR #17 | Closed |
| No audio device crashes startup | Low / High | Optional mixer and silent fallback covered by PR #18 | Closed |
| Invalid config discards valid sibling values | Low / High | Per-field recovery and warnings in PRs #19 and #30 | Closed |
| Assigned generator failure or invalid placements | Low / High | Single validated adapter, reachable placement contracts and `perfect=False` in PR #22 | Closed |
| Assigned generator hangs on large mazes | Medium / High | Delivered levels capped at verified 15x15–18x18; ten-level smoke | Mitigated; revisit only with bounded generation |
| Global RNG couples generator and gameplay | Low / Medium | Independent seed, placement and ghost RNGs in PR #22 | Closed |
| Same-frame collision/pause ordering loses lives or score | Low / High | Rule tests in PR #23 and Pause/Freeze regressions in PR #27 | Closed |
| Highscore/config JSON is malformed | Low / Medium | Defaults/empty board, warnings and atomic writes in PRs #25/#30 | Closed in source |
| Missing/corrupt images crash screens | Low / High | Shared visible RGBA fallback and screen renders in PR #30 | Closed in source |
| Resource paths fail in a packaged layout | Low / High | Windows/Linux archives contain all assets and start outside checkout | Closed before publication |
| Highscore path is not writable in a packaged install | Low / High | Platform user-data policy and Windows/Linux path contracts; manual persistence/restart still required | Mitigated; final smoke pending |
| Asset provenance is insufficient for public upload | Medium / High | Verify source/license before publishing; never invent attribution | Open |
| Windows/Linux packages diverge | Low / Medium | One spec/script built and started native artifacts on both targets | Closed before publication |
| Itch.io build cannot be regenerated during review | Low / High | Timed clean-clone builds completed; download/published-artifact smoke remains | Mitigated; Itch.io pending |
| Management evidence overstates inferred team roles | Low / High | Report PR authorship only; wait for both contributors to confirm responsibilities | Controlled; #11 pending |

## Escalation rule

A risk stays open until observable evidence closes it. Documentation statements,
a successful source checkout or a dummy SDL run do not substitute for a real
packaged-build and download smoke.
