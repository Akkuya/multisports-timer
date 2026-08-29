from dataclasses import dataclass
from typing import Callable

import keyboard
from PySide6.QtCore import QObject, Signal


@dataclass
class HotkeyBinding:
    key: str
    description: str
    handler: Callable[[], None]


class GlobalHotkeyManager(QObject):
    """Registers global hotkeys and dispatches them on the Qt thread.

    The ``keyboard`` library fires callbacks on its own background thread, so
    the key name is hopped across to the GUI thread via a Qt signal before
    invoking the handler — widgets must only be touched on the Qt thread.
    """

    _trigger = Signal(str)

    def __init__(self):
        super().__init__()
        self._bindings: dict[str, HotkeyBinding] = {}
        self._enabled = True
        self._trigger.connect(self._dispatch)

    def register(self, key: str, description: str, handler: Callable[[], None]):
        binding = HotkeyBinding(key=key, description=description, handler=handler)
        self._bindings[key] = binding
        # add_hotkey accepts both single keys ("r") and chords ("ctrl+shift+q").
        keyboard.add_hotkey(key, lambda: self._trigger.emit(key))

    def _dispatch(self, key: str):
        if not self._enabled:
            return
        binding = self._bindings.get(key)
        if binding is None:
            return
        binding.handler()

    def set_enabled(self, enabled: bool):
        self._enabled = enabled
