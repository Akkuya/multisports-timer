import sys
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication, QLabel, QWidget

from SessionState import SessionState
from timer import SessionTimer



class Overlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setFixedSize(300, 80)
        self.label = QLabel("15:00", self)
        self.label.setStyleSheet("color: white; font-size: 60px;")
        # Position in top-right corner of primary screen
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - self.width() - 20, 20)
        
        self.session = SessionTimer()
        self.session.start()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_tick)
        self.timer.start(1000)

    def on_tick(self):
        self.session.tick()
        self.label.setText(self.session.formatted())
        
        if self.session.state == SessionState.FINISHED:    
            self.show_finished_state()
    
    def show_finished_state(self):
        self.setFixedSize(1920, 1080)
        self.move(0,0)
        self.label.setText("Done")