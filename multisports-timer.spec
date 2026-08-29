# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the multisport timer.

Build (from repo root):
    uv run pyinstaller --noconfirm multisports-timer.spec

Output: dist/multisports-timer.exe
"""
from PyInstaller.utils.hooks import collect_dynamic_libs
from pathlib import Path

def resource(*parts):
    return str(Path(SPECPATH) / "assets" / Path(*parts))

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=collect_dynamic_libs("PySide6"),
    datas=[
        (resource("alert.mp3"), "assets"),
    ],
    hiddenimports=[
        "PySide6.QtMultimedia",
        "PySide6.QtMultimediaWidgets",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "PySide6.QtWebEngineCore",
        "PySide6.QtWebEngineWidgets",
        "PySide6.QtQml",
        "PySide6.QtQuick",
        "PySide6.Qt3DCore",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="multisports-timer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
