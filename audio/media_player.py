from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer


class AlertPlayer:

    def __init__(self, sound_path: Path, volume: float = 0.5):
        self._player = QMediaPlayer()
        self._output = QAudioOutput()
        self._player.setAudioOutput(self._output)
        self._output.setVolume(volume)
        self._player.setSource(QUrl.fromLocalFile(str(sound_path)))

    def play(self):
        self._player.play()
        
    
