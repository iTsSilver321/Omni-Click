"""
OmniClick — Low-level mouse hook using ctypes.
Detects real (non-synthetic) mouse button presses/releases by checking
dwExtraInfo in MSLLHOOKSTRUCT.
"""

import ctypes
import ctypes.wintypes
import threading
from typing import Callable, Optional

# ── Constants ────────────────────────────────────────────────────────────────

WH_MOUSE_LL = 14
WM_QUIT = 0x0012

WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP   = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP   = 0x0205
WM_MBUTTONDOWN = 0x0207
WM_MBUTTONUP   = 0x0208

SYNTHETIC_MARKER = 0x4F4D4E49

BUTTON_DOWN = {
    "left": WM_LBUTTONDOWN, "right": WM_RBUTTONDOWN, "middle": WM_MBUTTONDOWN,
}
BUTTON_UP = {
    "left": WM_LBUTTONUP, "right": WM_RBUTTONUP, "middle": WM_MBUTTONUP,
}

# ── Win32 structures ─────────────────────────────────────────────────────────

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt",          ctypes.wintypes.POINT),
        ("mouseData",   ctypes.wintypes.DWORD),
        ("flags",       ctypes.wintypes.DWORD),
        ("time",        ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    ]

HOOKPROC = ctypes.WINFUNCTYPE(
    ctypes.c_ssize_t, ctypes.c_int,
    ctypes.wintypes.WPARAM, ctypes.wintypes.LPARAM,
)

SetWindowsHookExW   = ctypes.windll.user32.SetWindowsHookExW
UnhookWindowsHookEx = ctypes.windll.user32.UnhookWindowsHookEx
CallNextHookEx      = ctypes.windll.user32.CallNextHookEx
GetMessageW         = ctypes.windll.user32.GetMessageW
TranslateMessage    = ctypes.windll.user32.TranslateMessage
DispatchMessageW    = ctypes.windll.user32.DispatchMessageW
PostThreadMessageW  = ctypes.windll.user32.PostThreadMessageW
GetCurrentThreadId  = ctypes.windll.kernel32.GetCurrentThreadId


class MouseHook:
    """
    WH_MOUSE_LL hook that detects REAL mouse button events.
    Reads self._button dynamically so click-type changes take effect immediately.
    """

    def __init__(self):
        self._thread: Optional[threading.Thread] = None
        self._thread_id: Optional[int] = None
        self._ready = threading.Event()
        self._hook = None
        self._proc = None

        self._button: str = "left"
        self._on_real_down: Optional[Callable] = None
        self._on_real_up: Optional[Callable] = None

    def set_button(self, button: str):
        if button in BUTTON_DOWN:
            self._button = button

    def set_callbacks(self, on_down: Callable, on_up: Callable):
        self._on_real_down = on_down
        self._on_real_up = on_up

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._ready.clear()
        self._thread = threading.Thread(target=self._hook_thread, daemon=True)
        self._thread.start()
        self._ready.wait(timeout=2.0)

    def stop(self):
        if self._thread_id:
            PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._thread = None
        self._thread_id = None

    def restart(self):
        """Restart the hook (e.g. after changing button while armed)."""
        self.stop()
        self.start()

    def _hook_thread(self):
        self._thread_id = GetCurrentThreadId()

        def hook_proc(nCode, wParam, lParam):
            if nCode >= 0:
                info = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT))[0]
                if info.dwExtraInfo != SYNTHETIC_MARKER:
                    # Read current button DYNAMICALLY (not from closure)
                    cur_down = BUTTON_DOWN.get(self._button)
                    cur_up = BUTTON_UP.get(self._button)
                    if wParam == cur_down and self._on_real_down:
                        self._on_real_down()
                    elif wParam == cur_up and self._on_real_up:
                        self._on_real_up()
            return CallNextHookEx(None, nCode, wParam, lParam)

        self._proc = HOOKPROC(hook_proc)
        self._hook = SetWindowsHookExW(WH_MOUSE_LL, self._proc, None, 0)
        self._ready.set()

        msg = ctypes.wintypes.MSG()
        while GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            TranslateMessage(ctypes.byref(msg))
            DispatchMessageW(ctypes.byref(msg))

        if self._hook:
            UnhookWindowsHookEx(self._hook)
            self._hook = None
