"""
OmniClick — Global hotkey manager.
Supports multiple named keybindings with independent listen modes.
"""

from __future__ import annotations

import threading
from typing import Callable, Dict, Optional

from pynput import keyboard, mouse


def _key_to_str(key) -> str:
    if isinstance(key, keyboard.Key):
        return key.name.replace("_", " ").title().replace(" ", "")
    if isinstance(key, keyboard.KeyCode):
        if key.vk is not None and key.char is None:
            return f"VK{key.vk}"
        return (key.char or "").upper()
    return str(key)


def _button_to_str(button: mouse.Button) -> str:
    mapping = {
        mouse.Button.left: "Mouse Left",
        mouse.Button.right: "Mouse Right",
        mouse.Button.middle: "Mouse Middle",
    }
    if button in mapping:
        return mapping[button]
    name = str(button).replace("Button.", "").replace("_", " ").title()
    return f"Mouse {name}"


class Binding:
    """A single keybinding with its raw key reference and callback."""
    def __init__(self, name: str, key_str: str = "", callback: Optional[Callable] = None):
        self.name = name
        self.key_str = key_str
        self.raw_key = None
        self.is_keyboard = True
        self.callback = callback

    def resolve_key(self, key_str: str):
        """Resolve a string key name to a pynput key/button object."""
        self.key_str = key_str
        self.raw_key = None
        self.is_keyboard = True

        if not key_str:
            return

        lower = key_str.lower()
        for btn in mouse.Button:
            if _button_to_str(btn).lower() == lower:
                self.raw_key = btn
                self.is_keyboard = False
                return

        try:
            self.raw_key = keyboard.Key[lower]
            return
        except (KeyError, ValueError):
            pass

        if len(key_str) == 1:
            self.raw_key = keyboard.KeyCode.from_char(key_str.lower())

    def matches(self, key) -> bool:
        if self.raw_key is None:
            return False
        if isinstance(self.raw_key, keyboard.Key):
            return key == self.raw_key
        if isinstance(self.raw_key, keyboard.KeyCode) and isinstance(key, keyboard.KeyCode):
            if self.raw_key.vk and key.vk:
                return self.raw_key.vk == key.vk
            if self.raw_key.char and key.char:
                return self.raw_key.char.lower() == key.char.lower()
        return False

    def matches_button(self, button) -> bool:
        if self.raw_key is None or self.is_keyboard:
            return False
        return button == self.raw_key


class GlobalHotkeyManager:
    """
    Manages multiple named global keybindings.
    """

    def __init__(self):
        self._bindings: Dict[str, Binding] = {}
        self._listen_target: Optional[str] = None
        self._on_listen_complete: Optional[Callable[[str, str], None]] = None

        self._kb_listener: Optional[keyboard.Listener] = None
        self._mouse_listener: Optional[mouse.Listener] = None
        self._lock = threading.Lock()

    def register(self, name: str, key_str: str, callback: Callable):
        """Register a named keybinding."""
        b = Binding(name, key_str, callback)
        b.resolve_key(key_str)
        self._bindings[name] = b

    def update_key(self, name: str, key_str: str):
        """Update the key for an existing binding."""
        if name in self._bindings:
            self._bindings[name].resolve_key(key_str)

    def get_key_str(self, name: str) -> str:
        if name in self._bindings:
            return self._bindings[name].key_str
        return ""

    def enter_listen_mode(self, binding_name: str, callback: Callable[[str, str], None]):
        """Listen for the next key press and assign it to the named binding.
        callback receives (binding_name, key_str)."""
        self._on_listen_complete = callback
        self._listen_target = binding_name

    def start(self):
        if self._kb_listener is None:
            self._kb_listener = keyboard.Listener(on_press=self._on_kb_press)
            self._kb_listener.daemon = True
            self._kb_listener.start()
        if self._mouse_listener is None:
            self._mouse_listener = mouse.Listener(on_click=self._on_mouse_click)
            self._mouse_listener.daemon = True
            self._mouse_listener.start()

    def stop(self):
        if self._kb_listener:
            self._kb_listener.stop()
            self._kb_listener = None
        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None

    def _on_kb_press(self, key):
        with self._lock:
            if self._listen_target:
                key_str = _key_to_str(key)
                name = self._listen_target
                self._listen_target = None
                if name in self._bindings:
                    self._bindings[name].resolve_key(key_str)
                    self._bindings[name].key_str = key_str
                if self._on_listen_complete:
                    self._on_listen_complete(name, key_str)
                return

            for b in self._bindings.values():
                if b.is_keyboard and b.matches(key) and b.callback:
                    b.callback()

    def _on_mouse_click(self, x, y, button, pressed):
        with self._lock:
            if self._listen_target and pressed:
                key_str = _button_to_str(button)
                name = self._listen_target
                self._listen_target = None
                if name in self._bindings:
                    self._bindings[name].raw_key = button
                    self._bindings[name].is_keyboard = False
                    self._bindings[name].key_str = key_str
                if self._on_listen_complete:
                    self._on_listen_complete(name, key_str)
                return

            if not pressed:
                return
            for b in self._bindings.values():
                if not b.is_keyboard and b.matches_button(button) and b.callback:
                    b.callback()
