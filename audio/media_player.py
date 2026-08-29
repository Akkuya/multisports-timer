"""Sound playback for the timer.

``SoundManager`` owns a single ``QMediaPlayer`` and plays any *named* sound
registered with ``add()``. Keeping one shared player is lighter than one
player per effect, and only one sound needs to play at a time (a chime for
the final seconds, then a bell at the end).

Missing files are allowed at registration: an effect simply no-ops at play
time (and logs a warning) until the asset is dropped in. That keeps the app
runnable while new SFX are still being produced.
"""

import logging
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer

log = logging.getLogger(__name__)


class SoundManager:
    """Plays registered sound effects by name on a single shared player."""

    def __init__(self, default_volume: float = 0.5):
        self._player = QMediaPlayer()
        self._output = QAudioOutput()
        self._player.setAudioOutput(self._output)
        self._default_volume = default_volume
        self._output.setVolume(default_volume)
        self._sounds: dict[str, Path] = {}
        self._volumes: dict[str, float] = {}

    def add(self, name: str, path: Path, volume: float | None = None) -> None:
        """Register a sound so it can be played later by ``name``.

        ``volume`` overrides the shared default for this effect. A missing
        file is tolerated — it will simply not play until the asset exists.
        """
        self._sounds[name] = path
        self._volumes[name] = volume if volume is not None else self._default_volume

    def play(self, name: str) -> None:
        """Play the named effect, restarting it if it is already playing."""
        path = self._sounds.get(name)
        if path is None:
            log.warning("No sound registered under %r", name)
            return
        if not path.exists():
            log.warning("Sound asset missing for %r: %s", name, path)
            return
        self._output.setVolume(self._volumes[name])
        self._player.setSource(QUrl.fromLocalFile(str(path)))
        self._player.play()

    def set_default_volume(self, volume: float) -> None:
        self._default_volume = volume
        self._output.setVolume(volume)
