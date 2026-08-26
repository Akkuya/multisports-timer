"""Minimal overlay PoC — test whether PySide6 windows render over E6."""

import sys
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath
from PySide6.QtWidgets import QApplication, QWidget


class TestOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )

        self.setFixedSize(300, 80)

        # Position in top-right corner of primary screen
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - self.width() - 20, 20)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Dark semi-transparent background with rounded corners
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 12, 12)
        painter.fillPath(path, QColor(0, 0, 0, 180))

        # Green border
        painter.setPen(QColor(0, 255, 0))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 12, 12)

        # Label text
        painter.setPen(QColor(0, 255, 0))
        font = QFont("Consolas", 20, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "TEST OVERLAY")

        painter.end()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()


def main():
    app = QApplication(sys.argv)

    overlay = TestOverlay()
    overlay.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()