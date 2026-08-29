import sys

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication, QLabel, QWidget

from audio.media_player import AlertPlayer
from paths import resource_path
from timer.state import SessionState
from input.hotkeys import GlobalHotkeyManager
from timer.session import SessionTimer


class Overlay(QWidget):

    def __init__(self):
        super().__init__()
        self.HkManager = GlobalHotkeyManager()
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            
        )
        self.setFixedSize(300, 80)
        self.label = QLabel("15:00", self)
        self.label.setStyleSheet("color: white; font-size: 60px;")
        # Position in top-right corner of primary screen
        self.screen = QApplication.primaryScreen().geometry()
        self._normal_pos = (self.screen.width() - self.width() - 20, 20)
        self.move(*self._normal_pos)
        self.session = SessionTimer()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_tick)
        self.timer.start(1000)
        self._register_keybinds()
        self.alert_player = AlertPlayer(resource_path("assets", "alert.mp3"))
        self.alert_played = False
        
    
    def on_tick(self):
        self.session.tick()
        self.label.setText(self.session.formatted())
        
        if self.session.state == SessionState.FINISHED:
            self.show_finished_state()
            
    def show_finished_state(self):
        if not self.alert_played:
            self.play_alert()
            self.alert_played = True
        self.setFixedSize(self.screen.width(), self.screen.height())
        self.move(0,0)
        self.label.setText("Done")

    def restore_normal_state(self):
        self.setFixedSize(300, 80)
        self.move(*self._normal_pos)
        self.label.setText(self.session.formatted())

    def reset_session(self):
        self.session.reset()
        self.alert_played = False
        self.restore_normal_state()

    def _register_keybinds(self):
        self.HkManager.register("enter", "toggle pause", self.session.toggle_pause)
        self.HkManager.register("r", "reset timer", self.reset_session)
        self.HkManager.register("s", "start game", self.session.start)
        self.HkManager.register("ctrl+shift+q", "quit app", self.exit)

    def play_alert(self):
        self.alert_player.play()
    
    def exit(self):
        # self.close() alone is NOT enough to quit here. The overlay is
        # deliberately shown without activating (WA_ShowWithoutActivating) and
        # never takes focus, so Qt's quitOnLastWindowClosed never fires; the
        # event loop would keep running and the process would hang. Close the
        # window first for a clean teardown, then sys.exit() guarantees the
        # process actually terminates. Do not 'simplify' this back to close().
        self.close()
        sys.exit()