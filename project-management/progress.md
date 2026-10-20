# Planned work versus actual delivery

Snapshot: 2026-10-20. Statuses come from GitHub Project 11 and issue state.

## Roadmap progress

| Order | Planned slice | Actual delivery evidence | Status |
|---:|---|---|---|
| 0 | Establish workflow and roadmap | [PR #13](https://github.com/AnaisCaire/Pac-Man/pull/13) | Done |
| 1 | Green project baseline | [Issue #2](https://github.com/AnaisCaire/Pac-Man/issues/2), [PR #14](https://github.com/AnaisCaire/Pac-Man/pull/14) | Done |
| P0 | Audit Pygame/MLX equivalence | [Issue #16](https://github.com/AnaisCaire/Pac-Man/issues/16), [PR #17](https://github.com/AnaisCaire/Pac-Man/pull/17) | Done |
| P0 | Survive unavailable audio | [Issue #15](https://github.com/AnaisCaire/Pac-Man/issues/15), [PR #18](https://github.com/AnaisCaire/Pac-Man/pull/18) | Done |
| 2 | Exact CLI and robust configuration | [Issue #3](https://github.com/AnaisCaire/Pac-Man/issues/3), [PR #19](https://github.com/AnaisCaire/Pac-Man/pull/19) | Done |
| 3 | Maze adapter, seeds and placements | [Issue #4](https://github.com/AnaisCaire/Pac-Man/issues/4), [PR #22](https://github.com/AnaisCaire/Pac-Man/pull/22) | Done |
| 4 | Scoring and collision rules | [Issue #5](https://github.com/AnaisCaire/Pac-Man/issues/5), [PR #23](https://github.com/AnaisCaire/Pac-Man/pull/23), [PR #27](https://github.com/AnaisCaire/Pac-Man/pull/27) | Done |
| 5 | Persistent Top 10 highscores | [Issue #6](https://github.com/AnaisCaire/Pac-Man/issues/6), [PR #25](https://github.com/AnaisCaire/Pac-Man/pull/25) | Done |
| 6 | Ten-level progression and Pause | [Issue #7](https://github.com/AnaisCaire/Pac-Man/issues/7), [PR #24](https://github.com/AnaisCaire/Pac-Man/pull/24) | Done |
| 7 | Ghost chase/flee/dead/respawn | [Issue #8](https://github.com/AnaisCaire/Pac-Man/issues/8), [PR #28](https://github.com/AnaisCaire/Pac-Man/pull/28), [PR #29](https://github.com/AnaisCaire/Pac-Man/pull/29) | Done |
| 8 | Reviewer evaluator mode | [Issue #9](https://github.com/AnaisCaire/Pac-Man/issues/9), [PR #26](https://github.com/AnaisCaire/Pac-Man/pull/26), [PR #30](https://github.com/AnaisCaire/Pac-Man/pull/30) | Done |
| 9 | UI and resource hardening | [Issue #10](https://github.com/AnaisCaire/Pac-Man/issues/10), [PR #30](https://github.com/AnaisCaire/Pac-Man/pull/30), [PR #32](https://github.com/AnaisCaire/Pac-Man/pull/32) | Done |
| 10 | README and management evidence | [Issue #11](https://github.com/AnaisCaire/Pac-Man/issues/11), [PR #30](https://github.com/AnaisCaire/Pac-Man/pull/30), this directory | In progress: team evidence pending |
| 11 | Package, publish and rehearse | [Issue #12](https://github.com/AnaisCaire/Pac-Man/issues/12), [PR #32](https://github.com/AnaisCaire/Pac-Man/pull/32), [Itch.io release](https://as3di0.itch.io/pac-man) | Done (team accepted) |

## Material differences from the initial plan

- Two P0 slices were inserted after the baseline: MLX-equivalence evidence and
  no-audio startup. Both were resolved before later UI/package work.
- Scoring was implemented in PR #23; PR #27 later added the collision-frame
  Pause/Freeze regressions needed to close the owning issue safely.
- Ghost behavior needed two follow-ups after the main implementation: PR #29
  accelerated/retargeted returning eyes and centered the Hall of Fame.
- PR #30 intentionally combined adjacent review concerns: evaluator usability,
  asset fallback, highscore/config recovery, README and docstring compliance.
- Project-management evidence was not backfilled before the team could review
  the actual history. This retrospective is generated from immutable GitHub
  records and keeps remaining team-process claims pending confirmation.

## Observable collaboration record

GitHub records the following PR-opening accounts for this delivery history:

- `AnaisCaire`: PRs #17, #26 and #27.
- `mario-asenjo`: PRs #13, #14, #18, #19, #21–#25 and #28–#32.

This is traceability, not a workload or responsibility claim. Branch commits,
pair work, review, testing and decisions may involve both contributors. The
final team-organization document will be written only after `masenjo` and
`acaire-d` confirm responsibilities and decision process.

## Current delivery state

Functional gameplay, source gates, native Windows/Linux builds, regeneration,
external startup/no-audio smokes and team-confirmed Itch.io publication are
complete. Remaining work is the manually authored team-management evidence in
#11 followed by final epic acceptance/recode review.
