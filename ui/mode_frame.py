"""
OmniClick — Mode selection frame.
Activation mode (Toggle/Hold) + Click type dropdown.
"""

import customtkinter as ctk
from ui.theme import Theme as T


class ModeFrame(ctk.CTkFrame):

    def __init__(
        self, master,
        initial_mode: str = "toggle",
        initial_click_type: str = "left",
        on_mode_change=None,
        on_click_type_change=None,
        **kwargs,
    ):
        super().__init__(master, **T.card_kwargs(), **kwargs)
        self._on_mode_change = on_mode_change
        self._on_click_type_change = on_click_type_change

        self.grid_columnconfigure(0, weight=1)

        # ── Header ──────────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="⚙  MODE",
            font=ctk.CTkFont(family=T.FONT_FAMILY, size=T.FONT_HEADING, weight="bold"),
            text_color=T.TEXT_SECONDARY, anchor="w",
        ).grid(row=0, column=0, padx=T.PAD_LG, pady=(T.PAD_MD, T.PAD_XS), sticky="w")

        # ── Activation mode ──────────────────────────────────────────
        self._mode_var = ctk.StringVar(value=initial_mode.capitalize())
        self._mode_seg = ctk.CTkSegmentedButton(
            self, values=["Toggle", "Hold"],
            variable=self._mode_var,
            command=self._on_mode_selected,
            font=ctk.CTkFont(family=T.FONT_FAMILY, size=T.FONT_BODY, weight="bold"),
            selected_color=T.ACCENT, selected_hover_color=T.ACCENT_HOVER,
            unselected_color=T.BG_ELEVATED, unselected_hover_color=T.TAB_UNSELECTED_HOVER,
            text_color="#000000", corner_radius=T.RADIUS_INPUT,
        )
        self._mode_seg.grid(row=1, column=0, padx=T.PAD_LG, pady=(0, T.PAD_SM), sticky="ew")

        # ── Mode description ─────────────────────────────────────────
        self._desc_label = ctk.CTkLabel(
            self, text=self._desc_text(initial_mode),
            font=ctk.CTkFont(size=T.FONT_CAPTION), text_color=T.TEXT_DIM,
        )
        self._desc_label.grid(row=2, column=0, padx=T.PAD_LG, sticky="w")

        # ── Click type ───────────────────────────────────────────────
        ct_row = ctk.CTkFrame(self, fg_color="transparent")
        ct_row.grid(row=3, column=0, padx=T.PAD_LG, pady=(T.PAD_MD, T.PAD_MD))

        ctk.CTkLabel(
            ct_row, text="Click button:",
            font=ctk.CTkFont(size=T.FONT_BODY), text_color=T.TEXT_SECONDARY,
        ).pack(side="left", padx=(0, T.PAD_MD))

        self._click_type_var = ctk.StringVar(value=initial_click_type.capitalize())
        self._click_menu = ctk.CTkOptionMenu(
            ct_row, values=["Left", "Right", "Middle"],
            variable=self._click_type_var,
            command=self._on_click_type_selected,
            font=ctk.CTkFont(size=T.FONT_BODY, weight="bold"),
            width=110, height=30,
            fg_color=T.BG_INPUT, button_color=T.BG_ELEVATED,
            button_hover_color=T.TAB_UNSELECTED_HOVER,
            dropdown_fg_color=T.BG_CARD, dropdown_hover_color=T.BG_ELEVATED,
            corner_radius=T.RADIUS_SMALL,
        )
        self._click_menu.pack(side="left")

    # ── Public ───────────────────────────────────────────────────────

    def set_mode(self, mode: str):
        self._mode_var.set(mode.capitalize())
        self._desc_label.configure(text=self._desc_text(mode))

    def set_click_type(self, click_type: str):
        self._click_type_var.set(click_type.capitalize())

    # ── Internal ─────────────────────────────────────────────────────

    def _on_mode_selected(self, value: str):
        mode = value.lower()
        self._desc_label.configure(text=self._desc_text(mode))
        if self._on_mode_change:
            self._on_mode_change(mode)

    def _on_click_type_selected(self, value: str):
        if self._on_click_type_change:
            self._on_click_type_change(value.lower())

    @staticmethod
    def _desc_text(mode: str) -> str:
        if mode == "hold":
            return "Arm, then hold mouse button to autoclick"
        return "Press hotkey to start / stop clicking"
