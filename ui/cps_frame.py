"""
OmniClick — CPS control frame.
Decimal CPS (0.1–200), delay display, optional random range mode.
"""

import customtkinter as ctk
from ui.theme import Theme as T


class CPSFrame(ctk.CTkFrame):

    MIN_CPS = 0.1
    MAX_CPS = 200

    def __init__(
        self, master,
        initial_cps: float = 10.0,
        initial_range: bool = False,
        initial_min: float = 8.0,
        initial_max: float = 12.0,
        on_cps_change=None,
        on_range_toggle=None,
        on_range_min_change=None,
        on_range_max_change=None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_cps_change = on_cps_change
        self._on_range_toggle = on_range_toggle
        self._on_range_min_change = on_range_min_change
        self._on_range_max_change = on_range_max_change
        self._suppress = False

        self.grid_columnconfigure(0, weight=1)

        # ── Header ──────────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="CLICKS PER SECOND",
            font=ctk.CTkFont(family=T.FONT_FAMILY, size=T.FONT_SUBTITLE, weight="bold"),
            text_color=T.TEXT_MUTED,
        ).grid(row=0, column=0, pady=(0, T.PAD_SM))

        # ── CPS entry ───────────────────────────────────────────────
        self._cps_var = ctk.StringVar(value=f"{initial_cps:.1f}")
        self._cps_var.trace_add("write", self._on_entry_changed)

        self._entry = ctk.CTkEntry(
            self, textvariable=self._cps_var,
            font=ctk.CTkFont(family=T.FONT_MONO, size=T.FONT_DATA, weight="bold"),
            width=140, height=54, justify="center",
            fg_color=T.BG_INPUT,
            border_width=2, border_color=T.BG_BORDER,
            corner_radius=T.RADIUS_INPUT,
            text_color=T.ACCENT,
        )
        self._entry.grid(row=1, column=0, pady=(0, T.PAD_MD))

        # ── Slider ──────────────────────────────────────────────────
        self._slider = ctk.CTkSlider(
            self, from_=1, to=200, number_of_steps=199, width=300,
            command=self._on_slider_changed,
            button_color=T.ACCENT, button_hover_color=T.ACCENT_HOVER,
            progress_color=T.ACCENT,
        )
        self._slider.set(max(1, min(200, initial_cps)))
        self._slider.grid(row=2, column=0, pady=(0, T.PAD_XS))

        # ── Delay label ─────────────────────────────────────────────
        self._delay_label = ctk.CTkLabel(
            self, text="",
            font=ctk.CTkFont(size=T.FONT_BODY), text_color=T.TEXT_DIM,
        )
        self._delay_label.grid(row=3, column=0)
        self._update_delay_label(initial_cps)

        # ── Random range toggle ─────────────────────────────────────
        range_row = ctk.CTkFrame(self, fg_color="transparent")
        range_row.grid(row=4, column=0, pady=(T.PAD_MD, 0))

        self._range_var = ctk.BooleanVar(value=initial_range)
        ctk.CTkSwitch(
            range_row, text="Random range",
            variable=self._range_var,
            command=self._on_range_toggled,
            font=ctk.CTkFont(size=T.FONT_SUBTITLE),
            switch_width=36, switch_height=18,
            progress_color=T.ACCENT,
            button_color=T.SWITCH_BUTTON, button_hover_color=T.SWITCH_HOVER,
        ).pack(side="left")

        # ── Min / Max ────────────────────────────────────────────────
        self._range_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._range_frame.grid(row=5, column=0, pady=(T.PAD_SM, 0))

        for label_text, var_val, trace_cb in [
            ("Min:", initial_min, self._on_min_changed),
            ("Max:", initial_max, self._on_max_changed),
        ]:
            ctk.CTkLabel(
                self._range_frame, text=label_text,
                font=ctk.CTkFont(size=T.FONT_SUBTITLE), text_color=T.TEXT_SECONDARY,
            ).pack(side="left", padx=(0 if label_text == "Min:" else 10, 4))

            var = ctk.StringVar(value=f"{var_val:.1f}")
            entry = ctk.CTkEntry(
                self._range_frame, textvariable=var,
                width=60, height=28, justify="center",
                font=ctk.CTkFont(family=T.FONT_MONO, size=T.FONT_BODY),
                fg_color=T.BG_INPUT, border_width=1,
                border_color=T.BG_BORDER, corner_radius=T.RADIUS_SMALL,
            )
            entry.pack(side="left")
            var.trace_add("write", trace_cb)

            if label_text == "Min:":
                self._min_var = var
            else:
                self._max_var = var

        if not initial_range:
            self._range_frame.grid_remove()

    # ── Public ───────────────────────────────────────────────────────

    @property
    def cps(self) -> float:
        return self._parse(self._cps_var.get(), 10.0)

    def set_cps(self, value: float):
        clamped = max(self.MIN_CPS, min(self.MAX_CPS, value))
        self._suppress = True
        self._cps_var.set(f"{clamped:.1f}")
        self._slider.set(max(1, min(200, clamped)))
        self._update_delay_label(clamped)
        self._suppress = False

    # ── Internal ─────────────────────────────────────────────────────

    def _parse(self, text: str, default: float) -> float:
        try:
            return max(self.MIN_CPS, min(self.MAX_CPS, float(text)))
        except ValueError:
            return default

    def _on_entry_changed(self, *_):
        if self._suppress:
            return
        raw = self._cps_var.get()
        filtered = "".join(c for c in raw if c.isdigit() or c == ".")
        if filtered != raw:
            self._cps_var.set(filtered)
            return
        if not filtered or filtered == ".":
            return
        val = self._parse(filtered, 10.0)
        self._suppress = True
        self._slider.set(max(1, min(200, val)))
        self._suppress = False
        self._update_delay_label(val)
        if self._on_cps_change:
            self._on_cps_change(val)

    def _on_slider_changed(self, value: float):
        int_val = int(round(value))
        self._suppress = True
        self._cps_var.set(f"{int_val}.0")
        self._suppress = False
        self._update_delay_label(int_val)
        if self._on_cps_change:
            self._on_cps_change(float(int_val))

    def _on_range_toggled(self):
        on = self._range_var.get()
        if on:
            self._range_frame.grid()
        else:
            self._range_frame.grid_remove()
        if self._on_range_toggle:
            self._on_range_toggle(on)

    def _on_min_changed(self, *_):
        raw = self._min_var.get()
        if not raw or raw == ".":
            return
        try:
            val = float(raw)
        except ValueError:
            return
        if self._on_range_min_change:
            self._on_range_min_change(max(self.MIN_CPS, val))

    def _on_max_changed(self, *_):
        raw = self._max_var.get()
        if not raw or raw == ".":
            return
        try:
            val = float(raw)
        except ValueError:
            return
        if self._on_range_max_change:
            self._on_range_max_change(max(self.MIN_CPS, val))

    def _update_delay_label(self, cps: float):
        if cps <= 0:
            self._delay_label.configure(text="")
            return
        delay_ms = 1000.0 / cps
        if delay_ms >= 1000:
            self._delay_label.configure(text=f"1 click every {delay_ms/1000:.1f}s")
        else:
            self._delay_label.configure(text=f"Delay: {delay_ms:.0f}ms between clicks")
