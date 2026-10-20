# Retrospective timeline

Snapshot: 2026-10-20.

This Gantt is reconstructed from real PR creation and merge dates. It is a
retrospective record, not a claim that these dates were estimated in advance.

```mermaid
gantt
    title Pac-Man v1.5 verified delivery history
    dateFormat YYYY-MM-DD
    axisFormat %d %b

    section Recovery
    Planning workflow and guardrails (PR 13) :done, p13, 2026-08-22, 2d
    Green Python/Make quality baseline (PR 14) :done, p14, 2026-08-25, 1d

    section Compliance foundations
    Pygame to MLX API audit (PR 17) :done, p17, 2026-09-21, 7d
    Audio silent fallback (PR 18) :done, p18, 2026-09-27, 1d
    CLI and config hardening (PR 19) :done, p19, 2026-09-27, 1d
    Inline review cleanup (PR 21) :done, p21, 2026-09-27, 1d

    section Game contracts
    Maze seeds and placements (PR 22) :done, p22, 2026-09-28, 1d
    Scoring and collision rules (PR 23) :done, p23, 2026-09-28, 2d
    Progression and Pause (PR 24) :done, p24, 2026-09-29, 1d
    Persistent Top 10 highscores (PR 25) :done, p25, 2026-09-30, 6d
    Reviewer evaluator mode (PR 26) :done, p26, 2026-10-06, 2d
    Pause/Freeze collision regressions (PR 27) :done, p27, 2026-10-13, 2d
    Ghost behavior completion (PR 28) :done, p28, 2026-10-15, 1d
    Ghost return and Hall of Fame polish (PR 29) :done, p29, 2026-10-17, 2d

    section UI and evidence
    Evaluator, asset fallback and README (PR 30) :done, p30, 2026-10-18, 2d
    Project delivery evidence (PR 31) :done, p31, 2026-10-19, 1d
    Native packaging and regeneration (PR 32) :done, p32, 2026-10-19, 2d
    Itch.io Windows/Linux release :milestone, itch, 2026-10-20, 0d
```

## Remaining sequence (dates intentionally TBD)

1. Confirm team organization and complete the remaining #11 evidence.
2. Run the final requirement-to-evidence audit and close epic #1.

PR #32 generated Windows and Linux packages from a clean clone in 26 s and 30 s,
verified their contents and started both outside the checkout with normal dummy
audio and forced audio failure. The team then published Windows and Linux
downloads at https://as3di0.itch.io/pac-man and accepted #12 as complete.

The remaining #11 date is deliberately omitted until the team confirms its
manual organization evidence. This avoids converting guesses into project
evidence.
