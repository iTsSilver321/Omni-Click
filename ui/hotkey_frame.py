"""
OmniClick — Hotkey binding frame.
Displays the current hotkey and provides a 'Listen' button to rebind.
"""

import customtkinter as ctk


class HotkeyFrame(ctk.CTkFrame):
    """
    Shows the current hotkey in a styled label and a 'Listen' button
    that enters capture mode. Includes helper text so the user
    knows they can rebind.
    """

    def __init__(
        self,
        master,
        initial_hotkey: str = "F6",
        on_listen_clicked: callable = None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_listen_clicked = on_listen_clicked

        self.grid_columnconfigure(0, weight=1)

        # ── Section label ────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="HOTKEY",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#888888",
        ).grid(row=0, column=0, pady=(0, 2))

        # ── Helper text ──────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text='Click "Listen" then press any key or mouse button to rebind',
            font=ctk.CTkFont(size=10),
            text_color="#606060",
        ).grid(row=1, column=0, pady=(0, 6))

        # ── Hotkey display row ───────────────────────────────────────
        row_frame = ctk.CTkFrame(self, fg_color="transparent")
        row_frame.grid(row=2, column=0)

        self._hotkey_label = ctk.CTkLabel(
            row_frame,
            text=initial_hotkey,
            font=ctk.CTkFont(family="Consolas", size=20, weight="bold"),
            text_color="#39FF14",
            width=140, height=40,
            corner_radius=8,
            fg_color="#1a1a2e",
        )
        self._hotkey_label.pack(side="left", padx=(0, 12))

        self._listen_btn = ctk.CTkButton(
            row_frame,
            text="🎧  Listen",
            width=100, height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=8,
            fg_color="#444444",
            hover_color="#555555",
            command=self._on_listen_pressed,
        )
        self._listen_btn.pack(side="left")

    # ── Public API ───────────────────────────────────────────────────

    def set_hotkey_text(self, text: str):
        """Update the displayed hotkey name."""
        self._hotkey_label.configure(text=text)

    def set_listening(self, listening: bool):
        """Toggle the UI between normal and listening states."""
        if listening:
            self._hotkey_label.configure(text="Press any key…", text_color="#ffaa00")
            self._listen_btn.configure(state="disabled", text="⏳ Waiting…")
        else:
            self._listen_btn.configure(state="normal", text="🎧  Listen")
            self._hotkey_label.configure(text_color="#39FF14")

    # ── Internal ─────────────────────────────────────────────────────

    def _on_listen_pressed(self):
        self.set_listening(True)
        if self._on_listen_clicked:
            self._on_listen_clicked()
