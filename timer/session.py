import sys

from PySide6.QtCore import QTimer
from SessionState import SessionState

class SessionTimer:
    def __init__(self, duration_seconds=15*60):
        self.duration = duration_seconds
        self.reset()
        
    def start(self):
        self.remaining = self.duration
        self.state = SessionState.RUNNING
    
    def tick(self):
        if self.state != SessionState.RUNNING: return
        self.remaining -= 1
        if self.remaining <= 0:
            self.state = SessionState.FINISHED
    
    def reset(self):
        self.remaining = self.duration
        self.state = SessionState.IDLE

        
    def toggle_pause(self):
        if self.state == SessionState.FINISHED: return
        
        if self.state == SessionState.RUNNING:
            self.state = SessionState.PAUSED
        elif self.state in [SessionState.PAUSED, SessionState.IDLE]:
            self.state = SessionState.RUNNING
    
    def formatted(self):
        mins, secs = divmod(max(self.remaining, 0), 60)
        return f"{mins:02d}:{secs:02d}"
        
        
    