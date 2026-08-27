import sys
from PySide6 import QtCore
from PySide6.QtWidgets import QKeySequenceEdit
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication, QLabel, QWidget

from SessionState import SessionState
from hotkeyManager import GlobalHotkeyManager
from timer import SessionTimer
from typing import override


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
        self.move(self.screen.width() - self.width() - 20, 20)
        self.session = SessionTimer()
        self.session.start()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_tick)
        self.timer.start(1000)
        self._register_keybinds()
        

    def on_tick(self):
        self.session.tick()
        self.label.setText(self.session.formatted())
        
        if self.session.state == SessionState.FINISHED:    
            self.show_finished_state()
            
    
    def show_finished_state(self):
        self.setFixedSize(self.screen.width(), self.screen.height())
        self.move(0,0)
        self.label.setText("Done")
    
    def _register_keybinds(self):
        self.HkManager.register("enter", "toggle pause", self.session.toggle_pause)   