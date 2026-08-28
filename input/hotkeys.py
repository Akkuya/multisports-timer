from dataclasses import dataclass
from typing import Callable
from PySide6.QtCore import Signal, QObject
import keyboard


@dataclass
class HotkeyBinding:
    key: str
    description: str
    handler: Callable[[], None]


class GlobalHotkeyManager(QObject):
    _trigger = Signal(str)  # internal: key name crosses thread here

    def __init__(self):
        super().__init__()
        self._bindings: dict[str, HotkeyBinding] = {}
        self._enabled = True
        self._trigger.connect(self._dispatch)

    def register(self, key: str, description: str, handler: Callable[[], None]):
        # your job: store the binding, wire up keyboard.on_press_key
        # so the callback emits self._trigger.emit(key) instead of
        # calling handler() directly (that's the thread-hop)
        
        hotkey = HotkeyBinding(key=key, description=description, handler=handler)
        self._bindings[key] = hotkey
        print(hotkey)
        keyboard.on_press_key(key, callback=lambda _, k=key: self._trigger.emit(k))

        
    def _dispatch(self, key: str):
        # your job: look up the binding, check self._enabled, call handler
        if not self._enabled: return
        binding = self._bindings.get(key)
        if not binding: return
        
        binding.handler()

    def set_enabled(self, enabled: bool):
        self._enabled = enabled