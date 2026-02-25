"""
OmniClick — Premium status indicator frame.
Animated pulsing LED, split Start/Stop buttons, styled counter badge.
"""

import math
import customtkinter as ctk
from ui.theme import Theme as T


class StatusFrame(ctk.CTkFrame):

    def __init__(self, master, on_topmost_toggle, on_start=None, on_stop=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_topmost_toggle = on_topmost_toggle
        self._on_start = on_start
        self._on_stop = on_stop
        self._is_active = False
        self._is_armed = False
        self._mode = "toggle"
        self._pulse_step = 0
        self._pulse_running = False

        self.grid_columnconfigure(0, weight=1)

        # ── LED + status label ───────────────────────────────────────
        status_row = ctk.CTkFrame(self, fg_color="transparent")
        status_row.grid(row=0, column=0, pady=(0, 8))

        self._canvas = ctk.CTkCanvas(
            status_row, width=32, height=32,
            bg=T.BG_ROOT, highlightthickness=0,
        )
        self._canvas.pack(side="left", padx=(0, 12))
        self._outer_glow = self._canvas.create_oval(0, 0, 32, 32,
            fill=T.STATUS_IDLE_DIM, outline="")
        self._glow = self._canvas.create_oval(4, 4, 28, 28,
            fill=T.STATUS_IDLE_DIM, outline="")
        self._dot = self._canvas.create_oval(8, 8, 24, 24,
            fill=T.STATUS_IDLE, outline="")

        self._status_label = ctk.CTkLabel(
            status_row, text="STOPPED",
            font=ctk.CTkFont(family=T.FONT_FAMILY, size=20, weight="bold"),
            text_color=T.STATUS_IDLE,
        )
        self._status_label.pack(side="left")

        # ── Button row ───────────────────────────────────────────────
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=1, column=0, pady=(0, 6))

        self._start_btn = ctk.CTkButton(
            btn_row, text="▶  Start", width=130, height=38,
            font=ctk.CTkFont(family=T.FONT_FAMILY, size=13, weight="bold"),
            corner_radius=T.RADIUS_BUTTON,
            fg_color=T.BTN_START, hover_color=T.BTN_START_HOVER,
            text_color=T.TEXT_PRIMARY,
            command=self._on_start_pressed,
        )
        self._start_btn.pack(side="left", padx=(0, 10))

        self._stop_btn = ctk.CTkButton(
            btn_row, text="■  Stop", width=130, height=38,
            font=ctk.CTkFont(family=T.FONT_FAMILY, size=13, weight="bold"),
            corner_radius=T.RADIUS_BUTTON,
            fg_color=T.BTN_DISABLED, hover_color=T.BTN_DISABLED,
            text_color=T.BTN_DISABLED_TEXT,
            state="disabled",
            command=self._on_stop_pressed,
        )
        self._stop_btn.pack(side="left")

        # ── Hint ─────────────────────────────────────────────────────
        self._hint_label = ctk.CTkLabel(
            self, text="or press F6 to toggle",
            font=ctk.CTkFont(size=T.FONT_CAPTION, slant="italic"),
            text_color=T.TEXT_DIM,
        )
        self._hint_label.grid(row=2, column=0, pady=(0, 6))

        # ── Click counter badge ──────────────────────────────────────
        counter_frame = ctk.CTkFrame(
            self, fg_color=T.BG_INPUT,
            corner_radius=T.RADIUS_PILL, border_width=1,
            border_color=T.BG_BORDER,
        )
        counter_frame.grid(row=3, column=0, pady=(0, 6))

        self._counter_label = ctk.CTkLabel(
            counter_frame, text="  0 clicks  ",
            font=ctk.CTkFont(family=T.FONT_MONO, size=T.FONT_COUNTER),
            text_color=T.ACCENT,
        )
        self._counter_label.pack(padx=12, pady=3)

        # ── Always on top ────────────────────────────────────────────
        self._topmost_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self, text="Always on Top",
            variable=self._topmost_var,
            command=lambda: self._on_topmost_toggle(self._topmost_var.get()),
            font=ctk.CTkFont(size=T.FONT_BODY),
            checkbox_width=20, checkbox_height=20, border_width=2,
            checkmark_color=T.ACCENT,
            border_color=T.BG_BORDER,
            hover_color=T.BG_ELEVATED,
        ).grid(row=4, column=0)

    # ── Public ───────────────────────────────────────────────────────

    def set_active(self, active: bool):
        if self._is_active == active:
            return
        self._is_active = active
        if active:
            self._status_label.configure(text="RUNNING", text_color=T.STATUS_ACTIVE)
            self._start_btn.configure(state="disabled", fg_color=T.BTN_DISABLED,
                                      hover_color=T.BTN_DISABLED, text_color=T.BTN_DISABLED_TEXT)
            self._stop_btn.configure(state="normal", fg_color=T.BTN_STOP,
                                     hover_color=T.BTN_STOP_HOVER, text_color=T.TEXT_PRIMARY)
            self._stop_btn.configure(text="■  Stop")
            self._start_pulse(T.STATUS_ACTIVE, T.STATUS_ACTIVE_DIM)
        else:
            self._stop_pulse()
            if self._is_armed:
                self._show_armed()
            else:
                self._show_stopped()

    def set_armed(self, armed: bool):
        self._is_armed = armed
        if not self._is_active:
            if armed:
                self._show_armed()
            else:
                self._stop_pulse()
                self._show_stopped()

    def set_topmost(self, value: bool):
        self._topmost_var.set(value)

    def set_mode_ui(self, mode: str):
        self._mode = mode
        if not self._is_active and not self._is_armed:
            self._show_stopped()

    def update_hint(self, hotkey: str, mode: str, armed: bool = False):
        self._mode = mode
        if mode == "toggle":
            self._hint_label.configure(text=f"or press  {hotkey}  to toggle")
        elif armed:
            self._hint_label.configure(text="Hold mouse button to autoclick")
        else:
            self._hint_label.configure(text=f"Press  {hotkey}  to arm, then hold mouse")

    def update_click_count(self, count: int):
        self._counter_label.configure(
            text=f"  {count:,} click{'s' if count != 1 else ''}  "
        )

    # ── LED animation ────────────────────────────────────────────────

    def _start_pulse(self, color_hex: str, dim_hex: str):
        self._pulse_color = self._hex_to_rgb(color_hex)
        self._pulse_dim = self._hex_to_rgb(dim_hex)
        self._pulse_step = 0
        if not self._pulse_running:
            self._pulse_running = True
            self._pulse_tick()

    def _stop_pulse(self):
        self._pulse_running = False

    def _pulse_tick(self):
        if not self._pulse_running:
            return
        self._pulse_step += 1
        t = (math.sin(self._pulse_step * 0.15) + 1) / 2  # 0..1 smooth

        # Interpolate between dim and bright
        r = int(self._pulse_dim[0] + (self._pulse_color[0] - self._pulse_dim[0]) * t)
        g = int(self._pulse_dim[1] + (self._pulse_color[1] - self._pulse_dim[1]) * t)
        b = int(self._pulse_dim[2] + (self._pulse_color[2] - self._pulse_dim[2]) * t)
        bright = f"#{r:02x}{g:02x}{b:02x}"

        # Outer glow is even dimmer
        ro = int(self._pulse_dim[0] * 0.5 + (self._pulse_color[0] * 0.4) * t)
        go = int(self._pulse_dim[1] * 0.5 + (self._pulse_color[1] * 0.4) * t)
        bo = int(self._pulse_dim[2] * 0.5 + (self._pulse_color[2] * 0.4) * t)
        glow = f"#{min(ro,255):02x}{min(go,255):02x}{min(bo,255):02x}"

        self._canvas.itemconfig(self._outer_glow, fill=glow)
        self._canvas.itemconfig(self._glow, fill=bright)
        self._canvas.itemconfig(self._dot, fill=bright)

        self.after(50, self._pulse_tick)

    @staticmethod
    def _hex_to_rgb(hex_color: str):
        h = hex_color.lstrip("#")
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    # ── Internal ─────────────────────────────────────────────────────

    def _show_stopped(self):
        self._set_led_static(T.STATUS_IDLE, T.STATUS_IDLE_DIM)
        self._status_label.configure(text="STOPPED", text_color=T.STATUS_IDLE)
        if self._mode == "toggle":
            self._start_btn.configure(text="▶  Start", state="normal",
                                      fg_color=T.BTN_START, hover_color=T.BTN_START_HOVER,
                                      text_color=T.TEXT_PRIMARY)
        else:
            self._start_btn.configure(text="🔒  Arm", state="normal",
                                      fg_color=T.BTN_START, hover_color=T.BTN_START_HOVER,
                                      text_color=T.TEXT_PRIMARY)
        self._stop_btn.configure(text="■  Stop", state="disabled",
                                 fg_color=T.BTN_DISABLED, hover_color=T.BTN_DISABLED,
                                 text_color=T.BTN_DISABLED_TEXT)

    def _show_armed(self):
        self._status_label.configure(text="ARMED", text_color=T.STATUS_ARMED)
        self._start_btn.configure(state="disabled", fg_color=T.BTN_DISABLED,
                                  hover_color=T.BTN_DISABLED, text_color=T.BTN_DISABLED_TEXT)
        self._stop_btn.configure(text="🔓  Disarm", state="normal",
                                 fg_color=T.ACCENT_AMBER_DIM, hover_color=T.ACCENT_AMBER,
                                 text_color=T.TEXT_PRIMARY)
        self._start_pulse(T.STATUS_ARMED, T.STATUS_ARMED_DIM)

    def _set_led_static(self, color: str, dim: str):
        self._canvas.itemconfig(self._outer_glow, fill=dim)
        self._canvas.itemconfig(self._glow, fill=dim)
        self._canvas.itemconfig(self._dot, fill=color)

    def _on_start_pressed(self):
        if self._on_start:
            self._on_start()

    def _on_stop_pressed(self):
        if self._on_stop:
            self._on_stop()
