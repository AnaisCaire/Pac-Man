# Package and regeneration evidence

Snapshot: 2026-10-19, implementation branch before clean-clone rehearsal.

## Packaging contract

- Tool: PyInstaller 6.22.3, installed by uv as a development dependency.
- Entry point: root `pac-man.spec`, invoked by `make package`.
- Shape: native `onedir` bundle plus one archive per operating system.
- Public files beside the executable: `config.json` and
  `PACKAGE-INSTRUCTIONS.txt`.
- Relative highscores use writable user data, never the install directory.
- PyInstaller builds natively; no cross-compilation claim is made.

## Initial native builds

| Target | Python | Artifact | Size (bytes) | SHA-256 | Outside-checkout startup |
|---|---:|---|---:|---|---|
| Windows x86_64 | 3.10.20 | `pac-man-windows-x86_64.zip` | 36,125,838 | `72e9ee8f0a51ca6407bc6574c56779a7a66c9769716a1800ed97f15c65ab1936` | Running after 5 s with dummy SDL |
| Linux x86_64 (WSL2) | 3.10.21 | `pac-man-linux-x86_64.tar.gz` | 42,315,841 | `e55b5c73ce46e53065c7cd21f0e8dcca6c2eb5ef0d068b3b6e2dbb65d3f94c6e` | Running after 5 s with dummy SDL |

Both archives contain the executable, editable config, in-package instructions,
15 PNG images and two music files. Archive scans found no `.hermes`, `.venv`,
subject PDF, `__pycache__`, `OLD` backup, cache or secret path.

## Verified source gates

- Windows: 130 tests pass; flake8 and mandatory mypy pass (56 files).
- Linux: 130 tests pass; flake8 and mandatory mypy pass (56 files).
- `uv lock --check` passes on both systems.
- Unit contracts verify frozen no-argument launch and writable Windows/Linux
  highscore path resolution.

## Pending before release

- Repeat both builds from a fresh clone of the pushed commit and record elapsed
  regeneration time plus final artifact hashes.
- Manually exercise menu, gameplay, Pause, evaluator win/loss, name entry and
  highscore persistence/restart in each native bundle.
- Verify a real unavailable-audio path in the packaged application.
- Publish free and unlisted/private on Itch.io, download from the resulting URL
  and repeat the package smoke.

These pending rows remain open in issue #12 and must not be replaced with the
initial branch-build evidence above.
