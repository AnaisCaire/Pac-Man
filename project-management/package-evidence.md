# Package and regeneration evidence

Snapshot: 2026-10-20, packaging merged through PR #32 and published by the team.

## Packaging contract

- Tool: PyInstaller 6.22.3, installed by uv as a development dependency.
- Entry point: root `pac-man.spec`, invoked by `make package`.
- Shape: native `onedir` bundle plus one archive per operating system.
- Public files beside the executable: `config.json` and
  `PACKAGE-INSTRUCTIONS.txt`.
- Relative highscores use writable user data, never the install directory.
- PyInstaller builds natively; no cross-compilation claim is made.

## Clean-clone native builds

| Target | Python | Artifact | Size (bytes) | SHA-256 | Build time | Outside-checkout startup |
|---|---:|---|---:|---|---:|---|
| Windows x86_64 | 3.10.20 | `pac-man-windows-x86_64.zip` | 36,125,991 | `35abf98de01e8a8087a65df8c7001f8798d97dad3d52c52342cc84dc6ee48276` | 26 s | Running after 5 s with dummy SDL |
| Linux x86_64 (WSL2) | 3.10.21 | `pac-man-linux-x86_64.tar.gz` | 42,318,998 | `97f3c75c4ef8267908e71eec60c176b82cfbf422d0aaf1afb1dc5341fa3bb138` | 30 s | Running after 5 s with dummy SDL |

Both archives contain the executable, editable config, in-package instructions,
15 PNG images and two music files. Archive scans found no `.hermes`, `.venv`,
subject PDF, `__pycache__`, `OLD` backup, cache or secret path. Repeating startup
with an intentionally invalid SDL audio driver kept both packages running and
emitted the expected one-line silent-fallback warning.

The builds are regenerable from the locked source and commands; the compressed
archive bytes are not claimed to be bit-reproducible because ZIP/tar and
PyInstaller embed build timestamps.

## Verified source gates

- Windows: 130 tests pass; flake8 and mandatory mypy pass (56 files).
- Linux: 130 tests pass; flake8 and mandatory mypy pass (56 files).
- `uv lock --check` passes on both systems.
- Unit contracts verify frozen no-argument launch and writable Windows/Linux
  highscore path resolution.

## Itch.io release evidence

- URL: https://as3di0.itch.io/pac-man
- Visible title: `Pac-Man`.
- Visible creator: `As3di0`.
- Classification shown: `Games > Simulation > Free`.
- Windows download shown as `Pac-Man-Windows-x86_64.exe` (3.2 MB) with a
  Windows platform icon.
- Linux download shown as `Pac-Man-Linux-x86_64` (3 MB) with a Linux platform
  icon.
- The page exposes install sections for Launch, Controls, Evaluator mode and
  Highscores.
- No upload error, quarantine notice or compatibility warning is visible.

This page evidence was supplied by the team in a temporary repository-root
screenshot, inspected on 2026-10-20 and deleted immediately afterward. The
screenshot does not expose an explicit public/private label, per-file checksum,
channel name or build version, so none is claimed here. The team confirmed the
uploaded game is available and accepted packaging/deployment as complete.

The source-generated archive hashes above remain regeneration evidence; they
must not be presented as checksums for the differently named files displayed by
Itch.io because the screenshot does not prove byte identity.
