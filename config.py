"""Loads runtime settings from config.yaml with safe defaults.

This file is meant to be edited next to the running program. In a frozen
build that is the folder holding the .exe; in dev it is the repo root (where
config.yaml lives). A missing or invalid key simply falls back to a sane
default rather than crashing.
"""

import functools
import sys
from pathlib import Path

import yaml

DEFAULT_CONFIG = {
    "duration_seconds": 900,
    "volume": 0.5,
    "sounds": {
        "alert": "alert.mp3",
        "ending_soon": "ending-soon.mp3",
        "start": "start.mp3",
    },
}

# Default global-hotkey bindings. Keys are the internal action names used
# throughout the code; values are the 'keyboard'-library key/chord strings,
# e.g. "enter", "r", or "ctrl+shift+q". Remappable via the 'keybinds' section
# of config.yaml.
DEFAULT_KEYBINDS = {
    "toggle_pause": "enter",
    "reset": "r",
    "start": "s",
    "quit": "ctrl+shift+q",
    "add_min": "shift+=",
}


def _prog_dir() -> Path:
    """Directory next to the running program (the exe's folder when frozen,
    otherwise the repo root)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def config_path() -> Path:
    """Path of the editable config file next to the running program."""
    return _prog_dir() / "config.yaml"


def log_path_for(key: str, default_name: str) -> Path:
    """Resolve a log file path from the config's ``logging`` section.

    The configured value may be a bare filename (placed in the program's
    ``logs`` subfolder) or a full path. Falls back to ``logs/default_name``
    when unset or invalid.
    """
    raw = _load_raw()
    logging_cfg = raw.get("logging")
    value = None
    if isinstance(logging_cfg, dict):
        value = logging_cfg.get(key)
    if not isinstance(value, str) or not value.strip():
        return _prog_dir() / "logs" / default_name
    p = Path(value)
    if p.is_absolute():
        return p
    return _prog_dir() / "logs" / p


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
    seconds = raw.get("duration_seconds", DEFAULT_CONFIG["duration_seconds"])
    try:
        seconds = int(seconds)
    except (TypeError, ValueError):
        seconds = DEFAULT_CONFIG["duration_minutes"]
    return max(1, seconds)


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


def sound_path(name: str) -> Path:
    """Resolve a named sound effect to a file *next to the running program*.

    Looks under ``<program dir>/assets/<filename>`` (same folder that holds
    ``config.yaml`` and ``logs/``), so venues can drop in or replace sound
    files without rebuilding the exe. Returns ``Path()`` (empty) when the
    effect is disabled via an empty configured name.
    """
    filename = sound_file(name)
    if not filename:
        return Path()
    return _prog_dir() / "assets" / filename


@functools.lru_cache(maxsize=1)
def keybinds() -> dict[str, str]:
    """Global-hotkey bindings, keyed by action name.

    Reads the ``keybinds`` section of config.yaml. A missing or non-string
    value falls back to the entry from ``DEFAULT_KEYBINDS``.
    """
    raw = _load_raw()
    cfg = raw.get("keybinds")
    if not isinstance(cfg, dict):
        return dict(DEFAULT_KEYBINDS)
    result = dict(DEFAULT_KEYBINDS)
    for action, default_key in DEFAULT_KEYBINDS.items():
        value = cfg.get(action)
        if isinstance(value, str) and value.strip():
            result[action] = value.strip()
    return result
