"""
OmniClick — Window targeting UI card.
Lets users pick a window to restrict clicking to.
Lists open windows and has a "Capture Active" button.
"""

import ctypes
import ctypes.wintypes
import customtkinter as ctk
from ui.theme import Theme as T


# Win32 for enumerating windows
EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.c_void_p)
GetWindowTextW = ctypes.windll.user32.GetWindowTextW
GetWindowTextLengthW = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
GetForegroundWindow = ctypes.windll.user32.GetForegroundWindow
GetForegroundWindow.restype = ctypes.wintypes.HWND


def _list_windows() -> list[str]:
    """Return list of visible window titles."""
    titles = []

    def callback(hwnd, _):
        if not IsWindowVisible(hwnd):
            return True
        length = GetWindowTextLengthW(hwnd)
        if length <= 0:
            return True
        buf = ctypes.create_unicode_buffer(length + 1)
        GetWindowTextW(hwnd, buf, length + 1)
        title = buf.value.strip()
        if title and title != "OmniClick":
            titles.append(title)
        return True

    EnumWindows(EnumWindowsProc(callback), 0)
    return sorted(set(titles))


def _get_foreground_title() -> str:
    """Get current foreground window title."""
    hwnd = GetForegroundWindow()
    if not hwnd:
        return ""
    length = GetWindowTextLengthW(hwnd)
    if length <= 0:
        return ""
    buf = ctypes.create_unicode_buffer(length + 1)
    GetWindowTextW(hwnd, buf, length + 1)
    return buf.value.strip()


class TargetWindowFrame(ctk.CTkFrame):
    """Card for selecting a target window — clicks only fire when that window is focused."""

    def __init__(self, master, initial_target: str = "", on_target_change=None, **kwargs):
        super().__init__(master, **T.card_kwargs(), **kwargs)
        self._on_target_change = on_target_change

        self.grid_columnconfigure(0, weight=1)

        # ── Header ──────────────────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=T.PAD_LG, pady=(T.PAD_MD, T.PAD_XS), sticky="ew")
        hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hdr, text="🎯  WINDOW TARGETING",
            font=ctk.CTkFont(family=T.FONT_FAMILY, size=T.FONT_HEADING, weight="bold"),
            text_color=T.ACCENT_AMBER, anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self._enabled_var = ctk.BooleanVar(value=bool(initial_target))
        ctk.CTkSwitch(
            hdr, text="", variable=self._enabled_var,
            command=self._on_toggle,
            switch_width=36, switch_height=18,
            progress_color=T.ACCENT_AMBER,
            button_color=T.SWITCH_BUTTON, button_hover_color=T.SWITCH_HOVER,
        ).grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            self, text="Only click when this window is in focus",
            font=ctk.CTkFont(size=T.FONT_CAPTION), text_color=T.TEXT_DIM,
        ).grid(row=1, column=0, padx=T.PAD_LG, sticky="w")

        # ── Controls ────────────────────────────────────────────────
        self._controls = ctk.CTkFrame(self, fg_color="transparent")
        self._controls.grid(row=2, column=0, padx=T.PAD_LG, pady=(T.PAD_MD, T.PAD_XS), sticky="ew")
        self._controls.grid_columnconfigure(0, weight=1)

        # Target entry
        self._target_var = ctk.StringVar(value=initial_target)
        self._target_entry = ctk.CTkEntry(
            self._controls, textvariable=self._target_var,
            placeholder_text="Window title (substring match)",
            font=ctk.CTkFont(family=T.FONT_MONO, size=T.FONT_BODY),
            fg_color=T.BG_INPUT, border_width=1,
            border_color=T.BG_BORDER, corner_radius=T.RADIUS_SMALL,
            height=30,
        )
        self._target_entry.grid(row=0, column=0, sticky="ew", pady=(0, T.PAD_SM))
        self._target_var.trace_add("write", self._on_entry_changed)

        # Button row
        btn_row = ctk.CTkFrame(self._controls, fg_color="transparent")
        btn_row.grid(row=1, column=0, sticky="ew", pady=(0, T.PAD_XS))

        self._capture_btn = ctk.CTkButton(
            btn_row, text="📍 Capture in 3s", width=130, height=30,
            font=ctk.CTkFont(family=T.FONT_FAMILY, size=T.FONT_SUBTITLE, weight="bold"),
            corner_radius=T.RADIUS_INPUT,
            fg_color=T.ACCENT_AMBER_DIM, hover_color=T.ACCENT_AMBER,
            text_color=T.TEXT_PRIMARY,
            command=self._on_capture,
        )
        self._capture_btn.pack(side="left", padx=(0, T.PAD_MD))

        ctk.CTkButton(
            btn_row, text="📋 Pick Window", width=110, height=30,
            font=ctk.CTkFont(family=T.FONT_FAMILY, size=T.FONT_SUBTITLE, weight="bold"),
            corner_radius=T.RADIUS_INPUT,
            fg_color=T.BG_ELEVATED, hover_color=T.TAB_UNSELECTED_HOVER,
            text_color=T.TEXT_SECONDARY,
            command=self._on_pick_window,
        ).pack(side="left", padx=(0, T.PAD_MD))

        ctk.CTkButton(
            btn_row, text="✕ Clear", width=70, height=30,
            font=ctk.CTkFont(family=T.FONT_FAMILY, size=T.FONT_SUBTITLE, weight="bold"),
            corner_radius=T.RADIUS_INPUT,
            fg_color=T.BG_ELEVATED, hover_color=T.ACCENT_RED_DIM,
            text_color=T.TEXT_MUTED,
            command=self._on_clear,
        ).pack(side="left")

        # Status label
        self._status_label = ctk.CTkLabel(
            self, text=self._status_text(initial_target),
            font=ctk.CTkFont(size=T.FONT_CAPTION, slant="italic"),
            text_color=T.ACCENT_AMBER if initial_target else T.TEXT_DISABLED,
        )
        self._status_label.grid(row=3, column=0, padx=T.PAD_LG, pady=(0, T.PAD_MD))

        if not self._enabled_var.get():
            self._controls.grid_remove()
            self._status_label.grid_remove()

    # ── Callbacks ────────────────────────────────────────────────────

    def _on_toggle(self):
        on = self._enabled_var.get()
        if on:
            self._controls.grid()
            self._status_label.grid()
        else:
            self._controls.grid_remove()
            self._status_label.grid_remove()
            self._target_var.set("")
            self._fire_change("")

    def _on_entry_changed(self, *_):
        val = self._target_var.get().strip()
        self._update_status(val)
        self._fire_change(val)

    def _on_capture(self):
        self._capture_btn.configure(text="3…", state="disabled")
        self.after(1000, lambda: self._capture_btn.configure(text="2…"))
        self.after(2000, lambda: self._capture_btn.configure(text="1…"))
        self.after(3000, self._do_capture)

    def _do_capture(self):
        title = _get_foreground_title()
        if title:
            self._target_var.set(title)
        self._capture_btn.configure(text="📍 Capture in 3s", state="normal")

    def _on_pick_window(self):
        """Open a popup with the list of open windows."""
        windows = _list_windows()
        if not windows:
            return

        popup = ctk.CTkToplevel(self)
        popup.title("Select Window")
        popup.geometry("400x300")
        popup.configure(fg_color=T.BG_ROOT)
        popup.transient(self)
        popup.grab_set()
        popup.attributes("-topmost", True)

        ctk.CTkLabel(
            popup, text="Select a window:",
            font=ctk.CTkFont(family=T.FONT_FAMILY, size=T.FONT_HEADING, weight="bold"),
            text_color=T.ACCENT_AMBER,
        ).pack(pady=(T.PAD_MD, T.PAD_SM))

        scroll = ctk.CTkScrollableFrame(
            popup, fg_color=T.BG_SURFACE,
            scrollbar_button_color=T.TAB_UNSELECTED,
        )
        scroll.pack(fill="both", expand=True, padx=T.PAD_MD, pady=(0, T.PAD_MD))

        for title in windows:
            short = title if len(title) <= 50 else title[:47] + "…"
            ctk.CTkButton(
                scroll, text=short, anchor="w", height=28,
                font=ctk.CTkFont(size=T.FONT_SUBTITLE),
                fg_color="transparent", hover_color=T.BG_ELEVATED,
                text_color=T.TEXT_SECONDARY,
                command=lambda t=title, p=popup: self._select_window(t, p),
            ).pack(fill="x", pady=1)

    def _select_window(self, title: str, popup):
        self._target_var.set(title)
        self._enabled_var.set(True)
        self._controls.grid()
        self._status_label.grid()
        popup.destroy()

    def _on_clear(self):
        self._target_var.set("")

    def _fire_change(self, value: str):
        if self._on_target_change:
            self._on_target_change(value)

    def _update_status(self, target: str):
        if target:
            self._status_label.configure(
                text=f'Targeting: "{target}"',
                text_color=T.ACCENT_AMBER,
            )
        else:
            self._status_label.configure(
                text="No target — clicking everywhere",
                text_color=T.TEXT_DISABLED,
            )

    @staticmethod
    def _status_text(target: str) -> str:
        if target:
            return f'Targeting: "{target}"'
        return "No target — clicking everywhere"
