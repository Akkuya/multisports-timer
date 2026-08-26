from overlay import Overlay
import sys
from PySide6.QtWidgets import QApplication

import signal

def main():
    app = QApplication(sys.argv)
    
    overlay = Overlay()
    overlay.show()
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
