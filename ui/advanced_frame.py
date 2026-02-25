"""
OmniClick — Advanced features frame.
Click Multiplier, Burst Mode, Multi-Location, Click Limit, Scheduling.
All cards use the shared design system.
"""

import ctypes
import ctypes.wintypes
import customtkinter as ctk
from ui.theme import Theme as T


class AdvancedFrame(ctk.CTkFrame):

    def __init__(
        self,
        master,
        initial_clicks_per: int = 1,
        initial_burst_count: int = 0,
        initial_burst_pause: float = 0.5,
        initial_locations: list = None,
        initial_click_limit: int = 0,
        initial_start_delay: float = 0.0,
        initial_run_duration: float = 0.0,
        on_clicks_per_change=None,
        on_burst_count_change=None,
        on_burst_pause_change=None,
        on_locations_change=None,
        on_click_limit_change=None,
        on_start_delay_change=None,
        on_run_duration_change=None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_clicks_per_change = on_clicks_per_change
        self._on_burst_count_change = on_burst_count_change
        self._on_burst_pause_change = on_burst_pause_change
        self._on_locations_change = on_locations_change
        self._on_click_limit_change = on_click_limit_change
        self._on_start_delay_change = on_start_delay_change
        self._on_run_duration_change = on_run_duration_change
        self._locations = list(initial_locations or [])

        self.grid_columnconfigure(0, weight=1)

        # ═══ CLICK MULTIPLIER ════════════════════════════════════════
        multi_card = ctk.CTkFrame(self, **T.card_kwargs())
        multi_card.grid(row=0, column=0, sticky="ew", pady=(0, T.PAD_MD))
        multi_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            multi_card, text="🖱  CLICK MULTIPLIER",
            font=ctk.CTkFont(family=T.FONT_FAMILY, size=T.FONT_HEADING, weight="bold"),
            text_color=T.ACCENT_PURPLE, anchor="w",
        ).grid(row=0, column=0, padx=T.PAD_LG, pady=(T.PAD_MD, T.PAD_XS), sticky="w")

        ctk.CTkLabel(
            multi_card, text="Clicks fired per event",
            font=ctk.CTkFont(size=T.FONT_CAPTION), text_color=T.TEXT_DIM,
        ).grid(row=1, column=0, padx=T.PAD_LG, sticky="w")

        multi_map = {1: "Single", 2: "Double", 3: "Triple"}
        self._multi_var = ctk.StringVar(value=multi_map.get(initial_clicks_per, "Single"))
        ctk.CTkSegmentedButton(
            multi_card, values=["Single", "Double", "Triple"],
            variable=self._multi_var,
            command=self._on_multi_selected,
            font=ctk.CTkFont(family=T.FONT_FAMILY, size=T.FONT_BODY, weight="bold"),
            selected_color=T.ACCENT_PURPLE, selected_hover_color="#6a5acd",
            unselected_color=T.BG_ELEVATED, unselected_hover_color=T.TAB_UNSELECTED_HOVER,
            text_color=T.TEXT_PRIMARY, corner_radius=T.RADIUS_INPUT,
        ).grid(row=2, column=0, padx=T.PAD_LG, pady=(T.PAD_MD, T.PAD_MD), sticky="ew")

        # ═══ BURST MODE ═════════════════════════════════════════════
        burst_card = ctk.CTkFrame(self, **T.card_kwargs())
        burst_card.grid(row=1, column=0, sticky="ew", pady=(0, T.PAD_MD))
        burst_card.grid_columnconfigure(0, weight=1)

        bh = ctk.CTkFrame(burst_card, fg_color="transparent")
        bh.grid(row=0, column=0, padx=T.PAD_LG, pady=(T.PAD_MD, T.PAD_XS), sticky="ew")
        bh.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            bh, text="💥  BURST MODE",
            font=ctk.CTkFont(family=T.FONT_FAMILY, size=T.FONT_HEADING, weight="bold"),
            text_color=T.ACCENT_RED, anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self._burst_on = ctk.BooleanVar(value=initial_burst_count > 0)
        ctk.CTkSwitch(
            bh, text="", variable=self._burst_on,
            command=self._on_burst_toggle,
            switch_width=36, switch_height=18,
            progress_color=T.ACCENT_RED,
            button_color=T.SWITCH_BUTTON, button_hover_color=T.SWITCH_HOVER,
        ).grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            burst_card, text="Fire N clicks rapidly, pause, repeat",
            font=ctk.CTkFont(size=T.FONT_CAPTION), text_color=T.TEXT_DIM,
        ).grid(row=1, column=0, padx=T.PAD_LG, sticky="w")

        # Burst count
        bc_row = ctk.CTkFrame(burst_card, fg_color="transparent")
        bc_row.grid(row=2, column=0, padx=T.PAD_LG, pady=(T.PAD_MD, T.PAD_XS), sticky="ew")

        ctk.CTkLabel(bc_row, text="Clicks:", font=ctk.CTkFont(size=T.FONT_SUBTITLE),
                     text_color=T.TEXT_SECONDARY).pack(side="left", padx=(0, T.PAD_MD))

        self._burst_slider = ctk.CTkSlider(
            bc_row, from_=2, to=50, number_of_steps=48, width=160,
            command=self._on_burst_count_slide,
            button_color=T.ACCENT_RED, button_hover_color="#cc3344",
            progress_color=T.ACCENT_RED,
        )
        bval = max(2, initial_burst_count) if initial_burst_count > 0 else 5
        self._burst_slider.set(bval)
        self._burst_slider.pack(side="left", padx=(0, T.PAD_MD))

        self._burst_count_label = ctk.CTkLabel(
            bc_row, text=str(bval),
            font=ctk.CTkFont(family=T.FONT_MONO, size=T.FONT_HEADING, weight="bold"),
            text_color=T.ACCENT_RED, width=30,
        )
        self._burst_count_label.pack(side="left")

        # Burst pause
        bp_row = ctk.CTkFrame(burst_card, fg_color="transparent")
        bp_row.grid(row=3, column=0, padx=T.PAD_LG, pady=(T.PAD_XS, T.PAD_MD), sticky="ew")

        ctk.CTkLabel(bp_row, text="Pause:", font=ctk.CTkFont(size=T.FONT_SUBTITLE),
                     text_color=T.TEXT_SECONDARY).pack(side="left", padx=(0, T.PAD_MD))

        self._pause_slider = ctk.CTkSlider(
            bp_row, from_=1, to=30, number_of_steps=29, width=160,
            command=self._on_burst_pause_slide,
            button_color=T.ACCENT_PINK, button_hover_color="#ee5a6f",
            progress_color=T.ACCENT_PINK,
        )
        pval = int(initial_burst_pause * 10) if initial_burst_pause > 0 else 5
        self._pause_slider.set(max(1, pval))
        self._pause_slider.pack(side="left", padx=(0, T.PAD_MD))

        self._pause_label = ctk.CTkLabel(
            bp_row, text=f"{initial_burst_pause:.1f}s",
            font=ctk.CTkFont(family=T.FONT_MONO, size=T.FONT_HEADING, weight="bold"),
            text_color=T.ACCENT_PINK, width=40,
        )
        self._pause_label.pack(side="left")

        if not self._burst_on.get():
            self._burst_slider.configure(state="disabled")
            self._pause_slider.configure(state="disabled")
            self._burst_count_label.configure(text_color=T.TEXT_DISABLED)
            self._pause_label.configure(text_color=T.TEXT_DISABLED)

        # ═══ MULTI-LOCATION ═════════════════════════════════════════
        loc_card = ctk.CTkFrame(self, **T.card_kwargs())
        loc_card.grid(row=2, column=0, sticky="ew", pady=(0, T.PAD_MD))
        loc_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            loc_card, text="📍  MULTI-LOCATION",
            font=ctk.CTkFont(family=T.FONT_FAMILY, size=T.FONT_HEADING, weight="bold"),
            text_color=T.ACCENT_TEAL, anchor="w",
        ).grid(row=0, column=0, padx=T.PAD_LG, pady=(T.PAD_MD, T.PAD_XS), sticky="w")

        ctk.CTkLabel(
            loc_card, text="Click at saved screen positions in order",
            font=ctk.CTkFont(size=T.FONT_CAPTION), text_color=T.TEXT_DIM,
        ).grid(row=1, column=0, padx=T.PAD_LG, sticky="w")

        self._loc_list_frame = ctk.CTkFrame(loc_card, fg_color="transparent")
        self._loc_list_frame.grid(row=2, column=0, padx=T.PAD_LG, pady=(T.PAD_MD, T.PAD_XS), sticky="ew")
        self._loc_list_frame.grid_columnconfigure(0, weight=1)
        self._loc_widgets: list = []
        self._rebuild_loc_list()

        btn_row = ctk.CTkFrame(loc_card, fg_color="transparent")
        btn_row.grid(row=3, column=0, padx=T.PAD_LG, pady=(T.PAD_SM, T.PAD_SM))

        self._capture_btn = ctk.CTkButton(
            btn_row, text="📍 Capture Position", width=150, height=32,
            font=ctk.CTkFont(family=T.FONT_FAMILY, size=T.FONT_BODY, weight="bold"),
            corner_radius=T.RADIUS_INPUT,
            fg_color=T.ACCENT_TEAL, hover_color="#10ac84", text_color="#000000",
            command=self._on_capture_pressed,
        )
        self._capture_btn.pack(side="left", padx=(0, T.PAD_MD))

        ctk.CTkButton(
            btn_row, text="🗑 Clear All", width=100, height=32,
            font=ctk.CTkFont(family=T.FONT_FAMILY, size=T.FONT_BODY, weight="bold"),
            corner_radius=T.RADIUS_INPUT,
            fg_color=T.BG_ELEVATED, hover_color=T.TAB_UNSELECTED_HOVER,
            text_color=T.TEXT_SECONDARY,
            command=self._on_clear_all,
        ).pack(side="left")

        ctk.CTkLabel(
            loc_card, text="Captures cursor position after 3s countdown",
            font=ctk.CTkFont(size=T.FONT_CAPTION), text_color=T.TEXT_DISABLED,
        ).grid(row=4, column=0, padx=T.PAD_LG, pady=(0, T.PAD_MD))

        # ═══ CLICK LIMIT ════════════════════════════════════════════
        limit_card = ctk.CTkFrame(self, **T.card_kwargs())
        limit_card.grid(row=3, column=0, sticky="ew", pady=(0, T.PAD_MD))
        limit_card.grid_columnconfigure(0, weight=1)

        lmh = ctk.CTkFrame(limit_card, fg_color="transparent")
        lmh.grid(row=0, column=0, padx=T.PAD_LG, pady=(T.PAD_MD, T.PAD_XS), sticky="ew")
        lmh.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            lmh, text="🎯  CLICK LIMIT",
            font=ctk.CTkFont(family=T.FONT_FAMILY, size=T.FONT_HEADING, weight="bold"),
            text_color=T.ACCENT_AMBER, anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self._limit_on = ctk.BooleanVar(value=initial_click_limit > 0)
        ctk.CTkSwitch(
            lmh, text="", variable=self._limit_on,
            command=self._on_limit_toggle,
            switch_width=36, switch_height=18,
            progress_color=T.ACCENT_AMBER,
            button_color=T.SWITCH_BUTTON, button_hover_color=T.SWITCH_HOVER,
        ).grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            limit_card, text="Automatically stop after N clicks",
            font=ctk.CTkFont(size=T.FONT_CAPTION), text_color=T.TEXT_DIM,
        ).grid(row=1, column=0, padx=T.PAD_LG, sticky="w")

        limit_row = ctk.CTkFrame(limit_card, fg_color="transparent")
        limit_row.grid(row=2, column=0, padx=T.PAD_LG, pady=(T.PAD_MD, T.PAD_MD))

        ctk.CTkLabel(limit_row, text="Stop after:", font=ctk.CTkFont(size=T.FONT_SUBTITLE),
                     text_color=T.TEXT_SECONDARY).pack(side="left", padx=(0, T.PAD_MD))

        self._limit_var = ctk.StringVar(
            value=str(initial_click_limit) if initial_click_limit > 0 else "100"
        )
        self._limit_entry = ctk.CTkEntry(
            limit_row, textvariable=self._limit_var,
            width=70, height=28, justify="center",
            font=ctk.CTkFont(family=T.FONT_MONO, size=T.FONT_BODY),
            fg_color=T.BG_INPUT, border_width=1,
            border_color=T.BG_BORDER, corner_radius=T.RADIUS_SMALL,
        )
        self._limit_entry.pack(side="left", padx=(0, T.PAD_MD))
        self._limit_var.trace_add("write", self._on_limit_value_changed)

        ctk.CTkLabel(limit_row, text="clicks", font=ctk.CTkFont(size=T.FONT_SUBTITLE),
                     text_color=T.TEXT_SECONDARY).pack(side="left")

        if not self._limit_on.get():
            self._limit_entry.configure(state="disabled")

        # ═══ SCHEDULING ═════════════════════════════════════════════
        sched_card = ctk.CTkFrame(self, **T.card_kwargs())
        sched_card.grid(row=4, column=0, sticky="ew")
        sched_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            sched_card, text="⏱  SCHEDULING",
            font=ctk.CTkFont(family=T.FONT_FAMILY, size=T.FONT_HEADING, weight="bold"),
            text_color=T.ACCENT_BLUE, anchor="w",
        ).grid(row=0, column=0, padx=T.PAD_LG, pady=(T.PAD_MD, T.PAD_XS), sticky="w")

        ctk.CTkLabel(
            sched_card, text="Delay before starting, auto-stop after duration",
            font=ctk.CTkFont(size=T.FONT_CAPTION), text_color=T.TEXT_DIM,
        ).grid(row=1, column=0, padx=T.PAD_LG, sticky="w")

        for row_i, (lbl, init_val, unit, trace_cb) in enumerate([
            ("Start delay:", initial_start_delay, "seconds", self._on_delay_changed),
            ("Run for:", initial_run_duration, "seconds  (0 = unlimited)", self._on_duration_changed),
        ]):
            r = ctk.CTkFrame(sched_card, fg_color="transparent")
            r.grid(row=row_i + 2, column=0, padx=T.PAD_LG,
                   pady=(T.PAD_MD if row_i == 0 else T.PAD_XS,
                         T.PAD_XS if row_i == 0 else T.PAD_MD), sticky="ew")

            ctk.CTkLabel(r, text=lbl, font=ctk.CTkFont(size=T.FONT_SUBTITLE),
                         text_color=T.TEXT_SECONDARY).pack(side="left", padx=(0, T.PAD_MD))

            var = ctk.StringVar(
                value=f"{init_val:.1f}" if init_val > 0 else "0"
            )
            ctk.CTkEntry(
                r, textvariable=var,
                width=55, height=28, justify="center",
                font=ctk.CTkFont(family=T.FONT_MONO, size=T.FONT_BODY),
                fg_color=T.BG_INPUT, border_width=1,
                border_color=T.BG_BORDER, corner_radius=T.RADIUS_SMALL,
            ).pack(side="left", padx=(0, T.PAD_MD))
            var.trace_add("write", trace_cb)

            ctk.CTkLabel(r, text=unit, font=ctk.CTkFont(size=T.FONT_SUBTITLE),
                         text_color=T.TEXT_DIM).pack(side="left")

            if lbl.startswith("Start"):
                self._delay_var = var
            else:
                self._duration_var = var

    # ── Public properties ────────────────────────────────────────────

    @property
    def click_limit(self) -> int:
        if not self._limit_on.get():
            return 0
        try:
            return max(0, int(self._limit_var.get()))
        except ValueError:
            return 0

    @property
    def start_delay(self) -> float:
        try:
            return max(0.0, float(self._delay_var.get()))
        except ValueError:
            return 0.0

    @property
    def run_duration(self) -> float:
        try:
            return max(0.0, float(self._duration_var.get()))
        except ValueError:
            return 0.0

    # ── Click Multiplier ─────────────────────────────────────────────

    def _on_multi_selected(self, value):
        m = {"Single": 1, "Double": 2, "Triple": 3}
        if self._on_clicks_per_change:
            self._on_clicks_per_change(m.get(value, 1))

    # ── Burst Mode ───────────────────────────────────────────────────

    def _on_burst_toggle(self):
        on = self._burst_on.get()
        self._burst_slider.configure(state="normal" if on else "disabled")
        self._pause_slider.configure(state="normal" if on else "disabled")
        self._burst_count_label.configure(text_color=T.ACCENT_RED if on else T.TEXT_DISABLED)
        self._pause_label.configure(text_color=T.ACCENT_PINK if on else T.TEXT_DISABLED)
        if self._on_burst_count_change:
            self._on_burst_count_change(int(round(self._burst_slider.get())) if on else 0)

    def _on_burst_count_slide(self, value):
        count = int(round(value))
        self._burst_count_label.configure(text=str(count))
        if self._on_burst_count_change and self._burst_on.get():
            self._on_burst_count_change(count)

    def _on_burst_pause_slide(self, value):
        secs = value / 10.0
        self._pause_label.configure(text=f"{secs:.1f}s")
        if self._on_burst_pause_change:
            self._on_burst_pause_change(secs)

    # ── Multi-Location ───────────────────────────────────────────────

    def _rebuild_loc_list(self):
        for w in self._loc_widgets:
            w.destroy()
        self._loc_widgets.clear()

        if not self._locations:
            lbl = ctk.CTkLabel(
                self._loc_list_frame, text="No positions saved",
                font=ctk.CTkFont(size=T.FONT_SUBTITLE, slant="italic"),
                text_color=T.TEXT_DISABLED,
            )
            lbl.grid(row=0, column=0, pady=T.PAD_XS)
            self._loc_widgets.append(lbl)
            return

        for i, (x, y) in enumerate(self._locations):
            row = ctk.CTkFrame(self._loc_list_frame, fg_color=T.BG_INPUT,
                               corner_radius=T.RADIUS_SMALL, height=28)
            row.grid(row=i, column=0, sticky="ew", pady=1)
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                row, text=f"  {i+1}.",
                font=ctk.CTkFont(family=T.FONT_MONO, size=T.FONT_SUBTITLE),
                text_color=T.ACCENT_TEAL, width=30,
            ).grid(row=0, column=0, sticky="w")

            ctk.CTkLabel(
                row, text=f"({x}, {y})",
                font=ctk.CTkFont(family=T.FONT_MONO, size=T.FONT_BODY, weight="bold"),
                text_color=T.TEXT_SECONDARY,
            ).grid(row=0, column=1, sticky="w")

            ctk.CTkButton(
                row, text="✕", width=28, height=24,
                font=ctk.CTkFont(size=T.FONT_SUBTITLE),
                fg_color=T.ACCENT_RED_DIM, hover_color=T.ACCENT_RED,
                text_color="#ff8888", corner_radius=T.RADIUS_SMALL,
                command=lambda idx=i: self._remove_location(idx),
            ).grid(row=0, column=2, padx=(0, 4), pady=2)

            self._loc_widgets.append(row)

    def _on_capture_pressed(self):
        self._capture_btn.configure(text="3…", state="disabled")
        self.after(1000, lambda: self._capture_btn.configure(text="2…"))
        self.after(2000, lambda: self._capture_btn.configure(text="1…"))
        self.after(3000, self._do_capture)

    def _do_capture(self):
        pt = ctypes.wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        self._locations.append((pt.x, pt.y))
        self._rebuild_loc_list()
        self._capture_btn.configure(text="📍 Capture Position", state="normal")
        self._fire_locations()

    def _remove_location(self, idx: int):
        if 0 <= idx < len(self._locations):
            self._locations.pop(idx)
            self._rebuild_loc_list()
            self._fire_locations()

    def _on_clear_all(self):
        self._locations.clear()
        self._rebuild_loc_list()
        self._fire_locations()

    def _fire_locations(self):
        if self._on_locations_change:
            self._on_locations_change(list(self._locations))

    # ── Click Limit ──────────────────────────────────────────────────

    def _on_limit_toggle(self):
        on = self._limit_on.get()
        self._limit_entry.configure(state="normal" if on else "disabled")
        if self._on_click_limit_change:
            self._on_click_limit_change(self.click_limit)

    def _on_limit_value_changed(self, *_):
        raw = self._limit_var.get()
        filtered = "".join(c for c in raw if c.isdigit())
        if filtered != raw:
            self._limit_var.set(filtered)
            return
        if self._on_click_limit_change and self._limit_on.get():
            try:
                self._on_click_limit_change(max(0, int(filtered)) if filtered else 0)
            except ValueError:
                pass

    # ── Scheduling ───────────────────────────────────────────────────

    def _on_delay_changed(self, *_):
        raw = self._delay_var.get()
        if not raw or raw == ".":
            return
        try:
            val = max(0.0, float(raw))
        except ValueError:
            return
        if self._on_start_delay_change:
            self._on_start_delay_change(val)

    def _on_duration_changed(self, *_):
        raw = self._duration_var.get()
        if not raw or raw == ".":
            return
        try:
            val = max(0.0, float(raw))
        except ValueError:
            return
        if self._on_run_duration_change:
            self._on_run_duration_change(val)
