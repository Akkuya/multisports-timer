import signal
import sys

from PySide6.QtWidgets import QApplication

import sessions_log
from ui.overlay import Overlay


def main():
    app = QApplication(sys.argv)

    overlay = Overlay()
    overlay.show()

    # Flush any buffered log lines before terminating on Ctrl+C / SIGINT, so a
    # long-running instance that is interrupted never loses the tail of its
    # event log.
    def _on_interrupt(signum, frame):
        sessions_log.flush()
        sys.exit(0)

    signal.signal(signal.SIGINT, _on_interrupt)

    sessions_log.log_event("app_start", "Application started")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
