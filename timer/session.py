from typing import Callable, Optional

from timer.state import SessionState


class SessionTimer:
    """Pure countdown state machine with no Qt/UI coupling.

    UI layers may pass an ``on_state_change`` callback invoked with the new
    state on every actual transition, so they can react immediately instead
    of polling.
    """

    def __init__(self, duration_seconds: int = 15, on_state_change: Optional[Callable[[SessionState], None]] = None):
        self.on_state_change = on_state_change
        self.duration = duration_seconds
        self.remaining = self.duration
        self.state = SessionState.IDLE

    def _set_state(self, target: SessionState):
        if self.state == target:
            return
        self.state = target
        if self.on_state_change is not None:
            self.on_state_change(target)

    @property
    def is_paused(self) -> bool:
        return self.state == SessionState.PAUSED

    def start(self):
        if self.state != SessionState.IDLE:
            return
        self.remaining = self.duration
        self._set_state(SessionState.RUNNING)

    def tick(self):
        if self.state != SessionState.RUNNING:
            return
        self.remaining -= 1
        if self.remaining <= 0:
            self._set_state(SessionState.FINISHED)

    def reset(self):
        self.remaining = self.duration
        self._set_state(SessionState.IDLE)

    def toggle_pause(self):
        # Only toggle a session that is already in progress: pause a running
        # timer or resume a paused one. A start (from IDLE) is a deliberate,
        # separate action — the Enter key must never silently kick a new
        # session off from the menu.
        if self.state == SessionState.RUNNING:
            self._set_state(SessionState.PAUSED)
        elif self.state == SessionState.PAUSED:
            self._set_state(SessionState.RUNNING)

    def formatted(self):
        mins, secs = divmod(max(self.remaining, 0), 60)
        return f"{mins:02d}:{secs:02d}"

    def add_min(self):
        self.remaining += 60
