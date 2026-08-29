import sys

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QTimer, Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QLinearGradient, QPainter, QPainterPath
from PySide6.QtWidgets import QApplication, QLabel, QWidget

from audio.media_player import AlertPlayer
from paths import resource_path
from timer.state import SessionState
from input.hotkeys import GlobalHotkeyManager
from timer.session import SessionTimer

# ---- palette ---------------------------------------------------------------
PANEL_BG = QColor(16, 20, 24, 216)      # dark slate scrim, translucent
PANEL_BORDER = QColor(42, 50, 59, 255)  # soft panel edge
TEXT_MAIN = QColor(255, 255, 255, 255)
TEXT_MUTED = QColor(190, 200, 210, 255)
ACCENT_LIVE = QColor(56, 232, 160, 255)   # golf-green "live" accent
ACCENT_WARN = QColor(255, 176, 32, 255)   # amber, low time
ACCENT_ENDING = QColor(240, 160, 180, 255)  # soft rose, final seconds
ALERT_LIGHT = QColor(184, 167, 212, 255)  # soft lavender pulse (finished)
ALERT_DARK = QColor(142, 120, 184, 255)   # muted orchid-purple pulse (finished)
TEXT_FINISHED = QColor(250, 248, 255, 255)  # soft white-cream on finished

PANEL_W, PANEL_H = 320, 96
WARN_SECONDS = 60   # amber + "LAST MINUTE" when <= 60s left
ENDING_SECONDS = 10 # "ENDING SOON" cue in the final seconds


class Overlay(QWidget):

    def __init__(self):
        super().__init__()
        self.HkManager = GlobalHotkeyManager()
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

        self.screen = QApplication.primaryScreen().geometry()
        self._normal_pos = (self.screen.width() - PANEL_W - 20, 20)

        self.session = SessionTimer()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_tick)
        self.timer.start(1000)
        self._register_keybinds()
        self.alert_player = AlertPlayer(resource_path("assets", "alert.mp3"))
        self._finished_entered = False

        # finished-state pulse
        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self.toggle_pulse)
        self._pulse_on = False

        # opacity fade between the compact panel and the fullscreen end screen,
        # so the end screen eases in instead of popping up.
        self.fade = QPropertyAnimation(self, b"windowOpacity")
        self.fade.setDuration(700)
        self.fade.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._fade_on_finished = None

        # widget setup
        self.lbl_time = QLabel("15:00", self)
        self.lbl_caption = QLabel("TIME REMAINING", self)
        self._style_labels()
        self.setFixedSize(PANEL_W, PANEL_H)
        self.move(*self._normal_pos)

    # ---- styling -----------------------------------------------------------
    def _style_labels(self):
        self.lbl_time.setFont(QFont("Segoe UI", 44, QFont.Weight.Black))
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_time.setStyleSheet("color: #FFFFFF; background: transparent;")
        self.lbl_caption.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        self.lbl_caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_caption.setStyleSheet("color: #BEC8D2; background: transparent; letter-spacing: 3px;")

    def _lay_out_normal(self):
        self.lbl_time.setGeometry(0, 8, PANEL_W, 60)
        self.lbl_caption.setGeometry(0, 66, PANEL_W, 18)

    # ---- painting ----------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.session.state == SessionState.FINISHED:
            self._paint_finished(painter)
        else:
            self._paint_panel(painter)

    def _paint_panel(self, painter):
        rect = self.rect()
        path = QPainterPath()
        radius = 16
        path.addRoundedRect(rect, radius, radius)
        painter.fillPath(path, PANEL_BG)
        painter.setPen(PANEL_BORDER)
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), radius, radius)

        # left accent bar — green while running, amber in the final minute.
        # A calm "ENDING SOON" caption eases into the end so the finished
        # state doesn't arrive as a surprise.
        accent = ACCENT_LIVE
        if self.session.state == SessionState.RUNNING and self.session.remaining <= ENDING_SECONDS:
            accent = ACCENT_ENDING
            self.lbl_caption.setText("ENDING SOON")
        elif self.session.state == SessionState.RUNNING and self.session.remaining <= WARN_SECONDS:
            accent = ACCENT_WARN
            self.lbl_caption.setText("LAST MINUTE")
        elif self.session.state != SessionState.FINISHED:
            self.lbl_caption.setText("TIME REMAINING")
        color = accent
        color.setAlpha(230)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawRoundedRect(rect.left() + 5, rect.top() + 5, 5, rect.height() - 10, 3, 3)

        painter.end()

    def _paint_finished(self, painter):
        # gentle two-tone pastel pulse — soft lavender / orchid-purple instead
        # of a harsh saturated red; the end screen should feel calm, not jar.
        top = ALERT_LIGHT if self._pulse_on else ALERT_DARK
        bottom = ALERT_DARK if self._pulse_on else ALERT_LIGHT
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0, top)
        grad.setColorAt(1.0, bottom)
        painter.fillRect(self.rect(), grad)
        painter.end()

    def toggle_pulse(self):
        self._pulse_on = not self._pulse_on
        # gentle text dimming for the breathing effect — stays readable
        text = TEXT_FINISHED if self._pulse_on else TEXT_FINISHED.darker(115)
        self.lbl_time.setStyleSheet(
            f"color: {text.name()}; background: transparent;"
        )
        self.update()

    # ---- state transitions -------------------------------------------------
    def on_tick(self):
        self.session.tick()
        self.lbl_time.setText(self.session.formatted())
        if self.session.state == SessionState.FINISHED:
            self.show_finished_state()
        else:
            self.update()  # re-evaluate warning accent each second

    def show_finished_state(self):
        first = not self._finished_entered
        if first:
            self.play_alert()
        self._finished_entered = True
        self.setFixedSize(self.screen.width(), self.screen.height())
        self.move(0, 0)
        self.lbl_time.setText("Session complete")
        self.lbl_time.setStyleSheet(f"color: {TEXT_FINISHED.name()}; background: transparent;")
        self.lbl_caption.setText("PLEASE SEE A MEMBER OF STAFF")
        self.lbl_caption.setStyleSheet(
            f"color: {TEXT_FINISHED.darker(110).name()}; background: transparent; letter-spacing: 3px;"
        )
        # size the headline so it always fits the screen regardless of
        # resolution — scale down until it clears ~92% of the display width.
        size = 120
        max_w = int(self.screen.width() * 0.92)
        while size > 30:
            f = QFont("Segoe UI", size, QFont.Weight.Black)
            if QFontMetrics(f).horizontalAdvance("Session complete") <= max_w:
                break
            size -= 4
        self.lbl_time.setFont(QFont("Segoe UI", size, QFont.Weight.Black))
        self.lbl_time.setGeometry(0, self.height() // 2 - size * 2, self.width(), size * 4)
        self.lbl_caption.setGeometry(0, self.height() // 2 + size * 2 + 10, self.width(), 20)
        self.pulse_timer.start(900)
        # ease the end screen in from transparent only on first entry, so it
        # doesn't pop up — and so later ticks don't restart the fade.
        if first:
            self.setWindowOpacity(0.0)
            self._fade_to(1.0)

    def restore_normal_state(self):
        # fade out of the fullscreen end screen, swap back to the compact
        # panel, then fade back in for a smooth hand-off.
        self.pulse_timer.stop()
        self._pulse_on = False
        self._fade_to(0.0, on_finished=self._swap_to_normal)

    def _swap_to_normal(self):
        self.setFixedSize(PANEL_W, PANEL_H)
        self.move(*self._normal_pos)
        self.lbl_time.setFont(QFont("Segoe UI", 44, QFont.Weight.Black))
        self.lbl_time.setText(self.session.formatted())
        self.lbl_time.setStyleSheet("color: #FFFFFF; background: transparent;")
        self.lbl_caption.setText("TIME REMAINING")
        self._lay_out_normal()
        self._style_labels()
        self.update()
        self._fade_to(1.0)

    def _fade_to(self, opacity, on_finished=None):
        """Animate window opacity to `opacity`, then run `on_finished`.

        Swap visible content while the window is transparent so changes are
        invisible — the end screen eases in from the compact panel instead of
        popping up.
        """
        self.fade.stop()
        self.fade.setStartValue(self.windowOpacity())
        self.fade.setEndValue(opacity)
        if self._fade_on_finished is not None:
            self.fade.finished.disconnect(self._fade_on_finished)
        self._fade_on_finished = on_finished
        if on_finished is not None:
            self.fade.finished.connect(on_finished)
        self.fade.start()

    def reset_session(self):
        self.session.reset()
        self._finished_entered = False
        self.restore_normal_state()

    # ---- hotkeys -----------------------------------------------------------
    def _register_keybinds(self):
        self.HkManager.register("enter", "toggle pause", self.session.toggle_pause)
        self.HkManager.register("r", "reset timer", self.reset_session)
        self.HkManager.register("s", "start game", self.session.start)
        self.HkManager.register("ctrl+shift+q", "quit app", self.exit)

    def play_alert(self):
        self.alert_player.play()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.session.state != SessionState.FINISHED:
            self._lay_out_normal()

    def exit(self):
        # self.close() alone is NOT enough to quit here. The overlay is
        # deliberately shown without activating (WA_ShowWithoutActivating) and
        # never takes focus, so Qt's quitOnLastWindowClosed never fires; the
        # event loop would keep running and the process would hang. Close the
        # window first for a clean teardown, then sys.exit() guarantees the
        # process actually terminates. Do not 'simplify' this back to close().
        self.close()
        sys.exit()
