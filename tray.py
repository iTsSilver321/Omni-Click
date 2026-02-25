"""
OmniClick — System tray icon.
Minimize-to-tray with right-click context menu.
Uses pystray + Pillow.
"""

import threading
from PIL import Image, ImageDraw
import pystray


def _create_tray_icon_image(size=64):
    """Create a simple neon-green lightning bolt icon."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Dark circle background
    draw.ellipse([2, 2, size - 2, size - 2], fill=(13, 13, 26, 255))

    # Lightning bolt (neon green)
    cx, cy = size // 2, size // 2
    bolt = [
        (cx + 2,  cy - 22),
        (cx - 5,  cy - 2),
        (cx + 1,  cy - 2),
        (cx - 6,  cy + 22),
        (cx + 7,  cy + 2),
        (cx + 1,  cy + 2),
    ]
    draw.polygon(bolt, fill=(57, 255, 20, 255))
    return img


class TrayIcon:
    """System tray icon with Start/Stop and Quit controls."""

    def __init__(self, on_toggle=None, on_show=None, on_quit=None):
        self._on_toggle = on_toggle
        self._on_show = on_show
        self._on_quit = on_quit
        self._icon: pystray.Icon | None = None
        self._thread: threading.Thread | None = None
        self._is_running = False

    def start(self, is_running: bool = False):
        """Create and show the tray icon in a daemon thread."""
        self._is_running = is_running
        menu = pystray.Menu(
            pystray.MenuItem(
                lambda _: "■ Stop" if self._is_running else "▶ Start",
                self._handle_toggle,
                default=True,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Show Window", self._handle_show),
            pystray.MenuItem("Quit", self._handle_quit),
        )
        self._icon = pystray.Icon(
            "OmniClick", _create_tray_icon_image(),
            "OmniClick", menu,
        )
        self._thread = threading.Thread(target=self._icon.run, daemon=True)
        self._thread.start()

    def stop(self):
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass
            self._icon = None

    def update_running(self, running: bool):
        """Update internal state and tooltip."""
        self._is_running = running
        if self._icon:
            self._icon.title = "OmniClick — " + ("Running" if running else "Stopped")

    # ── Handlers ─────────────────────────────────────────────────────

    def _handle_toggle(self, icon, item):
        if self._on_toggle:
            self._on_toggle()

    def _handle_show(self, icon, item):
        if self._on_show:
            self._on_show()

    def _handle_quit(self, icon, item):
        if self._on_quit:
            self._on_quit()
