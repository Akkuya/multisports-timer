"""Loads runtime settings from config.yaml with safe defaults.

Unlike ``paths.resource_path`` (which resolves assets bundled *inside* a
PyInstaller exe), this file is meant to be edited next to the running
program. In a frozen build that is the folder holding the .exe; in dev it is
the repo root (where config.yaml lives). A missing or invalid key simply
falls back to a sane default rather than crashing.
"""

import functools
import sys
from pathlib import Path

import yaml

DEFAULT_CONFIG = {
    "duration_minutes": 15,
    "volume": 0.5,
    "sounds": {
        "alert": "alert.mp3",
        "ending_soon": "ending-soon.mp3",
        "start": "start.mp3",
    },
}


def config_path() -> Path:
    """Path of the editable config file next to the running program."""
    base = Path(getattr(sys, "frozen", False) and sys.executable or Path(__file__).resolve().parent)
    return base / "config.yaml"


def _load_raw() -> dict:
    path = config_path()
    if not path.is_file():
        return {}
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        return loaded if isinstance(loaded, dict) else {}
    except (yaml.YAMLError, OSError):
        return {}


def _clamp_volume(value) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return DEFAULT_CONFIG["volume"]
    return max(0.0, min(1.0, v))


@functools.lru_cache(maxsize=1)
def seconds() -> int:
    """Countdown duration in whole seconds (duration_minutes -> seconds)."""
    raw = _load_raw()
    minutes = raw.get("duration_minutes", DEFAULT_CONFIG["duration_minutes"])
    try:
        minutes = int(minutes)
    except (TypeError, ValueError):
        minutes = DEFAULT_CONFIG["duration_minutes"]
    return max(1, minutes * 60)


@functools.lru_cache(maxsize=1)
def volume() -> float:
    return _clamp_volume(_load_raw().get("volume"))


@functools.lru_cache(maxsize=None)
def sound_file(name: str) -> str:
    """Filename under assets/ for a named effect, or '' to disable the effect.

    Falls back to the built-in default unless config.yaml explicitly overrides
    (or disables, via an empty string) the named sound.
    """
    raw = _load_raw()
    sounds = raw.get("sounds")
    if isinstance(sounds, dict) and name in sounds and isinstance(sounds[name], str):
        return sounds[name]
    return DEFAULT_CONFIG["sounds"].get(name, "")
