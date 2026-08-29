# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the multisport timer.

Build (from repo root):
    uv run pyinstaller --noconfirm multisports-timer.spec

Output: dist/multisports-timer.exe
"""
from pathlib import Path

# Datas: none bundled. Sound effects are deliberately NOT packed into the exe
# — they are loaded at runtime from the portable "<program dir>/assets" folder
# next to the .exe (see config.sound_path), so venues can drop in or replace
# audio files without rebuilding. Ship the exe together with an assets folder
# containing any sound files you want the timer to play.

# Disable PyInstaller's attempt to bulk-copy every dynamic lib in PySide6
# (that drags in Qt6WebEngineCore.dll ~194 MB and dozens of unused Qt
# modules). Rely on Analysis' natural dependency resolution instead, which
# follows the .pyd imports actually used (QtWidgets/QtMultimedia).
a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        "PySide6.QtMultimedia",
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
        "PySide6.QtCharts",
        "PySide6.QtDataVisualization",
        "PySide6.QtGraphs",
        "PySide6.QtDesigner",
        "PySide6.QtPdf",
        "PySide6.QtPdfWidgets",
        "PySide6.QtLocation",
        "PySide6.QtMultimediaWidgets",
    ],
    noarchive=False,
)

# Drop Qt modules pulled in transitively that this app doesn't use but that
# PySide6's hooks still grab: the QML/Quick DLLs (Qt6Quick.dll ~6.5 MB +
# Qt6Qml*.dll ~13 MB, linked by QtMultimedia's QML backend) and all the
# per-language .qm translation files (this app is English-only).
_UNUSED_BINS = (
    "Qt6Quick.dll",
    "Qt6Qml.dll",
    "Qt6QmlMeta.dll",
    "Qt6QmlModels.dll",
    "Qt6QmlWorkerScript.dll",
)
a.binaries = [b for b in a.binaries if not b[0].endswith(_UNUSED_BINS)]
a.datas = [d for d in a.datas if "translations" not in d[0]]

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
    icon="app_icon.ico",
)
