# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


ROOT = Path.cwd()
DATA_FILES = [
    (str(ROOT / "config.json"), "."),
    (str(ROOT / "PACKAGE-INSTRUCTIONS.txt"), "."),
    (str(ROOT / "src" / "ui" / "images"), "src/ui/images"),
    (str(ROOT / "src" / "ui" / "sounds"), "src/ui/sounds"),
]

analysis = Analysis(
    [str(ROOT / "pac-man.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=DATA_FILES,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(analysis.pure)

executable = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="Pac-Man",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)

bundle = COLLECT(
    executable,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    name="Pac-Man",
)
