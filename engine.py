"""
OmniClick — Click engine.
Threaded click loop using Win32 SendInput.
Features: jitter, humanizer, click multiplier, burst mode,
multi-location, random CPS range, click limit, scheduling,
per-app window targeting.
"""

import ctypes
import ctypes.wintypes
import random
import threading
import time

# ── Window targeting ─────────────────────────────────────────────────────────

GetForegroundWindow = ctypes.windll.user32.GetForegroundWindow
GetForegroundWindow.restype = ctypes.wintypes.HWND

GetWindowTextW = ctypes.windll.user32.GetWindowTextW
GetWindowTextW.argtypes = [ctypes.wintypes.HWND, ctypes.c_wchar_p, ctypes.c_int]

GetWindowTextLengthW = ctypes.windll.user32.GetWindowTextLengthW
GetWindowTextLengthW.argtypes = [ctypes.wintypes.HWND]

# ── Win32 constants ──────────────────────────────────────────────────────────

INPUT_MOUSE = 0
SYNTHETIC_MARKER = 0x4F4D4E49

MOUSEEVENTF_MOVE       = 0x0001
MOUSEEVENTF_LEFTDOWN   = 0x0002
MOUSEEVENTF_LEFTUP     = 0x0004
MOUSEEVENTF_RIGHTDOWN  = 0x0008
MOUSEEVENTF_RIGHTUP    = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP   = 0x0040

CLICK_EVENTS = {
    "left":   (MOUSEEVENTF_LEFTDOWN,   MOUSEEVENTF_LEFTUP),
    "right":  (MOUSEEVENTF_RIGHTDOWN,  MOUSEEVENTF_RIGHTUP),
    "middle": (MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP),
}

# ── Win32 structures ────────────────────────────────────────────────────────

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx",          ctypes.wintypes.LONG),
        ("dy",          ctypes.wintypes.LONG),
        ("mouseData",   ctypes.wintypes.DWORD),
        ("dwFlags",     ctypes.wintypes.DWORD),
        ("time",        ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    ]

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]
    _fields_ = [
        ("type", ctypes.wintypes.DWORD),
        ("ii",   _INPUT),
    ]

SendInput = ctypes.windll.user32.SendInput
SendInput.argtypes = [ctypes.c_uint, ctypes.POINTER(INPUT), ctypes.c_int]
SendInput.restype = ctypes.c_uint

SetCursorPos = ctypes.windll.user32.SetCursorPos

# ── Click engine ─────────────────────────────────────────────────────────────

class ClickEngine:
    def __init__(self):
        self._cps: float = 10.0
        self._click_type: str = "left"
        self._jitter_pixels: int = 0
        self._humanize_pct: float = 0.0
        self._clicks_per_event: int = 1
        self._burst_count: int = 0
        self._burst_pause: float = 0.5
        self._locations: list = []
        self._location_idx: int = 0
        # Precision & control
        self._cps_range: bool = False
        self._cps_min: float = 8.0
        self._cps_max: float = 12.0
        self._click_limit: int = 0       # 0 = unlimited
        self._start_delay: float = 0.0   # seconds
        self._run_duration: float = 0.0  # seconds, 0 = unlimited
        self._target_window: str = ""      # window title substring, "" = any
        # Internal
        self._running = threading.Event()
        self._thread: threading.Thread | None = None
        self._stop_flag = threading.Event()
        self._click_count: int = 0
        self._lock = threading.Lock()
        self._jitter_dx: int = 0
        self._jitter_dy: int = 0
        self._delay_timer: threading.Timer | None = None
        self._on_auto_stop: callable = None  # callback when engine auto-stops

    # ── Properties ───────────────────────────────────────────────────

    @property
    def cps(self) -> float:
        return self._cps

    @cps.setter
    def cps(self, value: float):
        self._cps = max(0.1, float(value))

    @property
    def click_type(self) -> str:
        return self._click_type

    @click_type.setter
    def click_type(self, value: str):
        if value in CLICK_EVENTS:
            self._click_type = value

    @property
    def jitter_pixels(self) -> int:
        return self._jitter_pixels

    @jitter_pixels.setter
    def jitter_pixels(self, value: int):
        self._jitter_pixels = max(0, min(25, int(value)))

    @property
    def humanize_pct(self) -> float:
        return self._humanize_pct

    @humanize_pct.setter
    def humanize_pct(self, value: float):
        self._humanize_pct = max(0.0, min(0.50, float(value)))

    @property
    def clicks_per_event(self) -> int:
        return self._clicks_per_event

    @clicks_per_event.setter
    def clicks_per_event(self, value: int):
        self._clicks_per_event = max(1, min(3, int(value)))

    @property
    def burst_count(self) -> int:
        return self._burst_count

    @burst_count.setter
    def burst_count(self, value: int):
        self._burst_count = max(0, min(50, int(value)))

    @property
    def burst_pause(self) -> float:
        return self._burst_pause

    @burst_pause.setter
    def burst_pause(self, value: float):
        self._burst_pause = max(0.1, min(5.0, float(value)))

    @property
    def locations(self) -> list:
        return self._locations

    @locations.setter
    def locations(self, value: list):
        self._locations = value
        self._location_idx = 0

    @property
    def cps_range(self) -> bool:
        return self._cps_range

    @cps_range.setter
    def cps_range(self, value: bool):
        self._cps_range = bool(value)

    @property
    def cps_min(self) -> float:
        return self._cps_min

    @cps_min.setter
    def cps_min(self, value: float):
        self._cps_min = max(0.1, float(value))

    @property
    def cps_max(self) -> float:
        return self._cps_max

    @cps_max.setter
    def cps_max(self, value: float):
        self._cps_max = max(0.1, float(value))

    @property
    def click_limit(self) -> int:
        return self._click_limit

    @click_limit.setter
    def click_limit(self, value: int):
        self._click_limit = max(0, int(value))

    @property
    def start_delay(self) -> float:
        return self._start_delay

    @start_delay.setter
    def start_delay(self, value: float):
        self._start_delay = max(0.0, float(value))

    @property
    def run_duration(self) -> float:
        return self._run_duration

    @run_duration.setter
    def run_duration(self, value: float):
        self._run_duration = max(0.0, float(value))

    @property
    def is_running(self) -> bool:
        return self._running.is_set()

    @property
    def click_count(self) -> int:
        return self._click_count

    def reset_click_count(self):
        with self._lock:
            self._click_count = 0

    def set_on_auto_stop(self, callback):
        self._on_auto_stop = callback

    @property
    def target_window(self) -> str:
        return self._target_window

    @target_window.setter
    def target_window(self, value: str):
        self._target_window = value.strip()

    def _is_target_focused(self) -> bool:
        """Return True if the target window is currently in the foreground."""
        if not self._target_window:
            return True  # no target = always allowed
        hwnd = GetForegroundWindow()
        if not hwnd:
            return False
        length = GetWindowTextLengthW(hwnd)
        if length <= 0:
            return False
        buf = ctypes.create_unicode_buffer(length + 1)
        GetWindowTextW(hwnd, buf, length + 1)
        return self._target_window.lower() in buf.value.lower()

    # ── Control ──────────────────────────────────────────────────────

    def start(self):
        if self._running.is_set():
            return
        if self._start_delay > 0:
            self._delay_timer = threading.Timer(self._start_delay, self._do_start)
            self._delay_timer.daemon = True
            self._delay_timer.start()
        else:
            self._do_start()

    def _do_start(self):
        if self._running.is_set():
            return
        self._stop_flag.clear()
        self._jitter_dx = 0
        self._jitter_dy = 0
        self._location_idx = 0
        self.reset_click_count()
        self._running.set()
        self._thread = threading.Thread(target=self._click_loop, daemon=True)
        self._thread.start()

    def stop(self):
        if self._delay_timer:
            self._delay_timer.cancel()
            self._delay_timer = None
        self._running.clear()
        self._stop_flag.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.5)
        self._thread = None
        self._undo_jitter()

    def toggle(self):
        if self._running.is_set():
            self.stop()
        else:
            self.start()

    # ── Internal ─────────────────────────────────────────────────────

    def _move_mouse(self, dx: int, dy: int):
        move = (INPUT * 1)()
        move[0].type = INPUT_MOUSE
        move[0].ii.mi.dx = dx
        move[0].ii.mi.dy = dy
        move[0].ii.mi.dwFlags = MOUSEEVENTF_MOVE
        move[0].ii.mi.dwExtraInfo = SYNTHETIC_MARKER
        SendInput(1, move, ctypes.sizeof(INPUT))

    def _undo_jitter(self):
        if self._jitter_dx != 0 or self._jitter_dy != 0:
            self._move_mouse(-self._jitter_dx, -self._jitter_dy)
            self._jitter_dx = 0
            self._jitter_dy = 0

    def _send_click(self):
        if self._locations:
            x, y = self._locations[self._location_idx % len(self._locations)]
            self._location_idx = (self._location_idx + 1) % len(self._locations)
            self._undo_jitter()
            SetCursorPos(x, y)

        if self._jitter_pixels > 0:
            if self._jitter_dx != 0 or self._jitter_dy != 0:
                self._move_mouse(-self._jitter_dx, -self._jitter_dy)
            dx = random.randint(-self._jitter_pixels, self._jitter_pixels)
            dy = random.randint(-self._jitter_pixels, self._jitter_pixels)
            self._move_mouse(dx, dy)
            self._jitter_dx = dx
            self._jitter_dy = dy

        down_flag, up_flag = CLICK_EVENTS[self._click_type]
        for i in range(self._clicks_per_event):
            inputs = (INPUT * 2)()
            inputs[0].type = INPUT_MOUSE
            inputs[0].ii.mi.dwFlags = down_flag
            inputs[0].ii.mi.dwExtraInfo = SYNTHETIC_MARKER
            inputs[1].type = INPUT_MOUSE
            inputs[1].ii.mi.dwFlags = up_flag
            inputs[1].ii.mi.dwExtraInfo = SYNTHETIC_MARKER
            SendInput(2, inputs, ctypes.sizeof(INPUT))
            if i < self._clicks_per_event - 1:
                time.sleep(0.04)

        with self._lock:
            self._click_count += self._clicks_per_event

    def _get_delay(self) -> float:
        if self._cps_range and self._cps_min < self._cps_max:
            cps = random.uniform(self._cps_min, self._cps_max)
        else:
            cps = self._cps
        delay = 1.0 / max(0.1, cps)
        if self._humanize_pct > 0:
            delay *= random.uniform(1.0 - self._humanize_pct, 1.0 + self._humanize_pct)
        return delay

    def _check_limits(self, start_time: float) -> bool:
        """Return True if we should stop."""
        if self._click_limit > 0 and self._click_count >= self._click_limit:
            return True
        if self._run_duration > 0 and time.time() - start_time >= self._run_duration:
            return True
        return False

    def _click_loop(self):
        start_time = time.time()
        while self._running.is_set():
            if self._check_limits(start_time):
                self._running.clear()
                if self._on_auto_stop:
                    self._on_auto_stop()
                break

            # ── Per-app targeting: wait until target window is focused ──
            if not self._is_target_focused():
                if self._stop_flag.wait(timeout=0.05):
                    break
                continue

            if self._burst_count > 0:
                for i in range(self._burst_count):
                    if not self._running.is_set() or self._check_limits(start_time):
                        self._running.clear()
                        if self._on_auto_stop:
                            self._on_auto_stop()
                        return
                    if not self._is_target_focused():
                        break
                    self._send_click()
                    if i < self._burst_count - 1:
                        if self._stop_flag.wait(timeout=self._get_delay()):
                            return
                if self._stop_flag.wait(timeout=self._burst_pause):
                    return
            else:
                self._send_click()
                if self._stop_flag.wait(timeout=self._get_delay()):
                    break
