"""
OmniClick — Effects frame.
Mouse Jitter (vibration) + Timing Humanizer.
"""

import customtkinter as ctk
from ui.theme import Theme as T


class EffectsFrame(ctk.CTkFrame):

    def __init__(
        self, master,
        initial_jitter: int = 0,
        initial_humanize: float = 0.10,
        on_jitter_change=None,
        on_humanize_change=None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_jitter_change = on_jitter_change
        self._on_humanize_change = on_humanize_change

        self.grid_columnconfigure(0, weight=1)

        # ═════════════════════════════════════════════════════════════
        # MOUSE JITTER
        # ═════════════════════════════════════════════════════════════
        jitter_card = ctk.CTkFrame(self, **T.card_kwargs())
        jitter_card.grid(row=0, column=0, sticky="ew", pady=(0, T.PAD_MD))
        jitter_card.grid_columnconfigure(0, weight=1)

        jh = ctk.CTkFrame(jitter_card, fg_color="transparent")
        jh.grid(row=0, column=0, padx=T.PAD_LG, pady=(T.PAD_MD, T.PAD_XS), sticky="ew")
        jh.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            jh, text="🎯  MOUSE JITTER",
            font=ctk.CTkFont(family=T.FONT_FAMILY, size=T.FONT_HEADING, weight="bold"),
            text_color=T.ACCENT_TEAL, anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self._jitter_on = ctk.BooleanVar(value=initial_jitter > 0)
        ctk.CTkSwitch(
            jh, text="", variable=self._jitter_on,
            command=self._on_jitter_toggle,
            switch_width=36, switch_height=18,
            progress_color=T.ACCENT_TEAL,
            button_color=T.SWITCH_BUTTON, button_hover_color=T.SWITCH_HOVER,
        ).grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            jitter_card, text="Vibrate cursor around click position",
            font=ctk.CTkFont(size=T.FONT_CAPTION), text_color=T.TEXT_DIM,
        ).grid(row=1, column=0, padx=T.PAD_LG, sticky="w")

        j_row = ctk.CTkFrame(jitter_card, fg_color="transparent")
        j_row.grid(row=2, column=0, padx=T.PAD_LG, pady=(T.PAD_MD, T.PAD_MD), sticky="ew")

        self._jitter_slider = ctk.CTkSlider(
            j_row, from_=1, to=25, number_of_steps=24, width=200,
            command=self._on_jitter_slide,
            button_color=T.ACCENT_TEAL, button_hover_color="#10ac84",
            progress_color=T.ACCENT_TEAL,
        )
        jval = max(1, initial_jitter) if initial_jitter > 0 else 5
        self._jitter_slider.set(jval)
        self._jitter_slider.pack(side="left", padx=(0, T.PAD_MD))

        self._jitter_label = ctk.CTkLabel(
            j_row, text=f"±{jval}px",
            font=ctk.CTkFont(family=T.FONT_MONO, size=T.FONT_HEADING, weight="bold"),
            text_color=T.ACCENT_TEAL, width=55,
        )
        self._jitter_label.pack(side="left")

        if not self._jitter_on.get():
            self._jitter_slider.configure(state="disabled")
            self._jitter_label.configure(text_color=T.TEXT_DISABLED)

        # ═════════════════════════════════════════════════════════════
        # TIMING HUMANIZER
        # ═════════════════════════════════════════════════════════════
        human_card = ctk.CTkFrame(self, **T.card_kwargs())
        human_card.grid(row=1, column=0, sticky="ew")
        human_card.grid_columnconfigure(0, weight=1)

        hh = ctk.CTkFrame(human_card, fg_color="transparent")
        hh.grid(row=0, column=0, padx=T.PAD_LG, pady=(T.PAD_MD, T.PAD_XS), sticky="ew")
        hh.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hh, text="⏱  TIMING HUMANIZER",
            font=ctk.CTkFont(family=T.FONT_FAMILY, size=T.FONT_HEADING, weight="bold"),
            text_color=T.ACCENT_BLUE, anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self._human_on = ctk.BooleanVar(value=initial_humanize > 0)
        ctk.CTkSwitch(
            hh, text="", variable=self._human_on,
            command=self._on_human_toggle,
            switch_width=36, switch_height=18,
            progress_color=T.ACCENT_BLUE,
            button_color=T.SWITCH_BUTTON, button_hover_color=T.SWITCH_HOVER,
        ).grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            human_card, text="Randomize delay between clicks",
            font=ctk.CTkFont(size=T.FONT_CAPTION), text_color=T.TEXT_DIM,
        ).grid(row=1, column=0, padx=T.PAD_LG, sticky="w")

        h_row = ctk.CTkFrame(human_card, fg_color="transparent")
        h_row.grid(row=2, column=0, padx=T.PAD_LG, pady=(T.PAD_MD, T.PAD_MD), sticky="ew")

        self._human_slider = ctk.CTkSlider(
            h_row, from_=1, to=500, number_of_steps=499, width=200,
            command=self._on_human_slide,
            button_color=T.ACCENT_BLUE, button_hover_color="#5b8ad8",
            progress_color=T.ACCENT_BLUE,
        )
        hval = int(initial_humanize * 1000) if initial_humanize > 0 else 100
        self._human_slider.set(max(1, hval))
        self._human_slider.pack(side="left", padx=(0, T.PAD_MD))

        pct = initial_humanize * 100
        self._human_label = ctk.CTkLabel(
            h_row, text=f"±{pct:.1f}%",
            font=ctk.CTkFont(family=T.FONT_MONO, size=T.FONT_HEADING, weight="bold"),
            text_color=T.ACCENT_BLUE, width=65,
        )
        self._human_label.pack(side="left")

        if not self._human_on.get():
            self._human_slider.configure(state="disabled")
            self._human_label.configure(text_color=T.TEXT_DISABLED)

    # ── Jitter ───────────────────────────────────────────────────────

    def _on_jitter_toggle(self):
        on = self._jitter_on.get()
        self._jitter_slider.configure(state="normal" if on else "disabled")
        self._jitter_label.configure(text_color=T.ACCENT_TEAL if on else T.TEXT_DISABLED)
        pixels = int(round(self._jitter_slider.get())) if on else 0
        if self._on_jitter_change:
            self._on_jitter_change(pixels)

    def _on_jitter_slide(self, value):
        px = int(round(value))
        self._jitter_label.configure(text=f"±{px}px")
        if self._on_jitter_change and self._jitter_on.get():
            self._on_jitter_change(px)

    # ── Humanizer ────────────────────────────────────────────────────

    def _on_human_toggle(self):
        on = self._human_on.get()
        self._human_slider.configure(state="normal" if on else "disabled")
        self._human_label.configure(text_color=T.ACCENT_BLUE if on else T.TEXT_DISABLED)
        pct = self._human_slider.get() / 1000.0 if on else 0.0
        if self._on_humanize_change:
            self._on_humanize_change(pct)

    def _on_human_slide(self, value):
        pct = value / 10.0
        self._human_label.configure(text=f"±{pct:.1f}%")
        if self._on_humanize_change and self._human_on.get():
            self._on_humanize_change(value / 1000.0)
