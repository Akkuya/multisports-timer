from enum import Enum, auto

class SessionState(Enum):
    IDLE = auto()
    RUNNING = auto()
    FINISHED = auto()