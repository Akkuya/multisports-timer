"""Filesystem path resolution that works both from source and when frozen.

PyInstaller one-file builds extract bundled assets to a temp directory
(exposed as ``sys._MEIPASS``), so paths must be resolved there at runtime
instead of relative to ``__file__`` or the current working directory.
"""
import sys
from pathlib import Path


def resource_path(*parts: str) -> Path:
    """Resolve a path to a bundled file, working in dev and frozen builds.

    When frozen, PyInstaller extracts assets under ``sys._MEIPASS``.
    When running from source, assets live next to this module (the repo
    root, since ``paths.py`` sits at the top level), so ``__file__``'s
    parent is the base.
    """
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base.joinpath(*parts)
