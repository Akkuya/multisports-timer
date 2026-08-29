"""Filesystem path resolution that works both from source and when frozen.

PyInstaller one-file builds extract bundled assets to a temp directory
(exposed as ``sys._MEIPASS``), so paths must be resolved there at runtime
instead of relative to ``__file__`` or the current working directory.
"""
import sys
from pathlib import Path


def resource_path(*parts: str) -> Path:
    """Resolve a path to a bundled file, working in dev and frozen builds."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return base.joinpath(*parts)
