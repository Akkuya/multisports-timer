from PySide6.QtCore import QTimer
from timer.state import SessionState


class SessionTimer:
    """Pure countdown state machine with no Qt/UI coupling."""

    def __init__(self, duration_seconds=15):
        self.duration = duration_seconds
        self.reset()

    def start(self):
        if self.state != SessionState.IDLE:
            return
        self.remaining = self.duration
        self.state = SessionState.RUNNING

    def tick(self):
        if self.state != SessionState.RUNNING:
            return
        self.remaining -= 1
        if self.remaining <= 0:
            self.state = SessionState.FINISHED

    def reset(self):
        self.remaining = self.duration
        self.state = SessionState.IDLE

    def toggle_pause(self):
        if self.state == SessionState.FINISHED:
            return
        self.state = (
            SessionState.PAUSED
            if self.state == SessionState.RUNNING
            else SessionState.RUNNING
        )

    def formatted(self):
        mins, secs = divmod(max(self.remaining, 0), 60)
        return f"{mins:02d}:{secs:02d}"

    def add_min(self):
        self.remaining+=60