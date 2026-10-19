"""Build and archive the native Pac-Man package for the current OS."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import platform
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def _platform_tag() -> tuple[str, str]:
    """Return the supported archive label and format for this native host."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    architecture = {
        "amd64": "x86_64",
        "x86_64": "x86_64",
        "aarch64": "arm64",
        "arm64": "arm64",
    }.get(machine, machine)
    if system == "windows":
        return (f"windows-{architecture}", "zip")
    if system == "linux":
        return (f"linux-{architecture}", "gztar")
    raise SystemExit(f"unsupported packaging host: {platform.system()}")


def _sha256(path: Path) -> str:
    """Return the SHA-256 digest of one artifact without loading it all."""
    digest = hashlib.sha256()
    with path.open("rb") as artifact:
        for chunk in iter(lambda: artifact.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_package() -> tuple[Path, str]:
    """Run PyInstaller, add public files, archive the bundle, and hash it."""
    platform_tag, archive_format = _platform_tag()
    platform_dist = ROOT / "dist" / platform_tag
    work_path = ROOT / "build" / platform_tag
    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            "--noconfirm",
            "--distpath",
            str(platform_dist),
            "--workpath",
            str(work_path),
            str(ROOT / "pac-man.spec"),
        ],
        cwd=ROOT,
        check=True,
    )

    bundle = platform_dist / "Pac-Man"
    shutil.copy2(ROOT / "config.json", bundle / "config.json")
    shutil.copy2(
        ROOT / "PACKAGE-INSTRUCTIONS.txt",
        bundle / "PACKAGE-INSTRUCTIONS.txt",
    )

    archive_base = ROOT / "dist" / f"pac-man-{platform_tag}"
    archive_suffix = ".zip" if archive_format == "zip" else ".tar.gz"
    archive = archive_base.with_suffix(archive_suffix)
    archive.unlink(missing_ok=True)
    archive = Path(shutil.make_archive(
        str(archive_base),
        archive_format,
        root_dir=platform_dist,
        base_dir="Pac-Man",
    ))
    checksum = _sha256(archive)
    archive.with_name(f"{archive.name}.sha256").write_text(
        f"{checksum}  {archive.name}\n",
        encoding="utf-8",
    )
    return archive, checksum


def main() -> None:
    """Parse the help flag and build one native PyInstaller artifact."""
    parser = argparse.ArgumentParser(
        description="Build and archive Pac-Man with PyInstaller for this OS."
    )
    parser.parse_args()
    archive, checksum = build_package()
    print(f"artifact={archive}")
    print(f"sha256={checksum}")


if __name__ == "__main__":
    main()
