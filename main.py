import signal
import sys

from PySide6.QtWidgets import QApplication

from sessions_log import log_event
from ui.overlay import Overlay


def main():
    app = QApplication(sys.argv)

    overlay = Overlay()
    overlay.show()
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    log_event("app_start", "Application started")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
