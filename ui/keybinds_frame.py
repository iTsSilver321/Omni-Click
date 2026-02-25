"""
OmniClick — Keybinds customization frame.
Card-based layout for each binding with Listen buttons.
"""

import customtkinter as ctk
from ui.theme import Theme as T


BINDING_INFO = {
    "start_stop":  ("Start / Stop",  "Toggle clicking or arm/disarm hold mode"),
    "cycle_click": ("Cycle Click",   "Cycle through Left → Right → Middle"),
    "cycle_mode":  ("Cycle Mode",    "Switch between Toggle and Hold modes"),
}


class KeybindsFrame(ctk.CTkFrame):

    def __init__(self, master, keybinds: dict, on_listen=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_listen = on_listen
        self._cards = {}

        self.grid_columnconfigure(0, weight=1)

        for i, (name, key_str) in enumerate(keybinds.items()):
            title, desc = BINDING_INFO.get(name, (name, ""))
            card = ctk.CTkFrame(self, **T.card_kwargs())
            card.grid(row=i, column=0, pady=(0, T.PAD_MD), sticky="ew")
            card.grid_columnconfigure(1, weight=1)

            # ── Left: title + description ────────────────────────────
            left = ctk.CTkFrame(card, fg_color="transparent")
            left.grid(row=0, column=0, padx=T.PAD_LG, pady=T.PAD_MD, sticky="w")

            ctk.CTkLabel(
                left, text=title,
                font=ctk.CTkFont(family=T.FONT_FAMILY, size=T.FONT_BODY, weight="bold"),
                text_color=T.TEXT_PRIMARY,
            ).pack(anchor="w")

            ctk.CTkLabel(
                left, text=desc,
                font=ctk.CTkFont(size=T.FONT_CAPTION), text_color=T.TEXT_DIM,
            ).pack(anchor="w")

            # ── Right: key badge + listen button ─────────────────────
            right = ctk.CTkFrame(card, fg_color="transparent")
            right.grid(row=0, column=1, padx=T.PAD_LG, pady=T.PAD_MD, sticky="e")

            key_badge = ctk.CTkLabel(
                right, text=key_str if key_str else "None",
                font=ctk.CTkFont(family=T.FONT_MONO, size=T.FONT_BODY, weight="bold"),
                text_color=T.ACCENT if key_str else T.TEXT_DISABLED,
                fg_color=T.BG_INPUT,
                corner_radius=T.RADIUS_SMALL,
                width=70, height=28,
            )
            key_badge.pack(side="left", padx=(0, T.PAD_MD))

            listen_btn = ctk.CTkButton(
                right, text="Listen", width=70, height=28,
                font=ctk.CTkFont(size=T.FONT_SUBTITLE, weight="bold"),
                corner_radius=T.RADIUS_SMALL,
                fg_color=T.BG_ELEVATED, hover_color=T.TAB_UNSELECTED_HOVER,
                text_color=T.TEXT_SECONDARY,
                command=lambda n=name: self._on_listen_clicked(n),
            )
            listen_btn.pack(side="left")

            self._cards[name] = {"badge": key_badge, "btn": listen_btn}

    def set_key_text(self, name: str, key_str: str):
        if name in self._cards:
            badge = self._cards[name]["badge"]
            badge.configure(
                text=key_str if key_str else "None",
                text_color=T.ACCENT if key_str else T.TEXT_DISABLED,
            )

    def set_listening(self, name: str, listening: bool):
        if name in self._cards:
            btn = self._cards[name]["btn"]
            if listening:
                btn.configure(text="Press key…", fg_color=T.ACCENT_RED,
                              text_color=T.TEXT_PRIMARY)
            else:
                btn.configure(text="Listen", fg_color=T.BG_ELEVATED,
                              text_color=T.TEXT_SECONDARY)

    def _on_listen_clicked(self, name: str):
        self.set_listening(name, True)
        if self._on_listen:
            self._on_listen(name)
