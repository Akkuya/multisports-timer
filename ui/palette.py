"""Centralized presentation tokens for the overlay.

Keeping the color palette here, rather than inline in the overlay, lets the
UI stay focused on behavior while the look lives in one obvious place. Tweak
these values to restyle the whole app without touching any logic.
"""

from PySide6.QtGui import QColor

# ---- compact countdown panel ------------------------------------------------
PANEL_BG = QColor(16, 20, 24, 216)      # dark slate scrim, translucent
PANEL_BORDER = QColor(42, 50, 59, 255)  # soft panel edge
TEXT_MAIN = QColor(255, 255, 255, 255)
TEXT_MUTED = QColor(190, 200, 210, 255)

# Accent bar that runs alongside the countdown, signalling the phase.
ACCENT_LIVE = QColor(56, 232, 160, 255)     # golf-green "live"
ACCENT_WARN = QColor(255, 176, 32, 255)     # amber, last minute
ACCENT_ENDING = QColor(240, 160, 180, 255)  # soft rose, final seconds

# ---- fullscreen finished screen --------------------------------------------
ALERT_LIGHT = QColor(184, 167, 212, 255)  # soft lavender pulse
ALERT_DARK = QColor(142, 120, 184, 255)   # muted orchid-purple pulse
TEXT_FINISHED = QColor(250, 248, 255, 255)  # soft white-cream on finished
