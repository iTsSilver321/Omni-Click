"""
OmniClick — Main application window.
Tabbed UI: Main (scrollable) | Effects | Advanced (scrollable) | Keybinds
System tray integration, per-app window targeting.
"""

import sys
import customtkinter as ctk

from engine import ClickEngine
from hotkeys import GlobalHotkeyManager
from mouse_hook import MouseHook
from tray import TrayIcon
from settings import load_settings, save_settings
from ui.theme import Theme as T
from ui.status_frame import StatusFrame
from ui.cps_frame import CPSFrame
from ui.mode_frame import ModeFrame
from ui.effects_frame import EffectsFrame
from ui.advanced_frame import AdvancedFrame
from ui.keybinds_frame import KeybindsFrame
from ui.target_frame import TargetWindowFrame


CLICK_CYCLE = ["left", "right", "middle"]
VERSION = "1.0.0"


class App(ctk.CTk):

    WIDTH  = 460
    HEIGHT = 660

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("OmniClick")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.minsize(420, 520)
        self.configure(fg_color=T.BG_ROOT)

        try:
            self.iconbitmap("assets/icon.ico")
        except Exception:
            pass

        # ── Settings & state ─────────────────────────────────────────
        self._settings = load_settings()
        self._armed = False

        # ── Engine ───────────────────────────────────────────────────
        self._engine = ClickEngine()
        self._engine.cps = self._settings["cps"]
        self._engine.click_type = self._settings["click_type"]
        self._engine.jitter_pixels = self._settings.get("jitter_pixels", 0)
        self._engine.humanize_pct = self._settings.get("humanize_pct", 0.10)
        self._engine.clicks_per_event = self._settings.get("clicks_per_event", 1)
        self._engine.burst_count = self._settings.get("burst_count", 0)
        self._engine.burst_pause = self._settings.get("burst_pause", 0.5)
        self._engine.locations = [tuple(p) for p in self._settings.get("locations", [])]
        self._engine.cps_range = self._settings.get("cps_range", False)
        self._engine.cps_min = self._settings.get("cps_min", 8.0)
        self._engine.cps_max = self._settings.get("cps_max", 12.0)
        self._engine.click_limit = self._settings.get("click_limit", 0)
        self._engine.start_delay = self._settings.get("start_delay", 0.0)
        self._engine.run_duration = self._settings.get("run_duration", 0.0)
        self._engine.target_window = self._settings.get("target_window", "")
        self._engine.set_on_auto_stop(self._on_engine_auto_stop)

        # ── Hotkey manager ───────────────────────────────────────────
        kb = self._settings["keybinds"]
        self._hotkey_mgr = GlobalHotkeyManager()
        self._hotkey_mgr.register("start_stop",  kb.get("start_stop", "F6"), self._on_hotkey_start_stop)
        self._hotkey_mgr.register("cycle_click",  kb.get("cycle_click", ""), self._on_hotkey_cycle_click)
        self._hotkey_mgr.register("cycle_mode",   kb.get("cycle_mode", ""),  self._on_hotkey_cycle_mode)

        # ── Mouse hook ───────────────────────────────────────────────
        self._mouse_hook = MouseHook()
        self._mouse_hook.set_button(self._settings["click_type"])
        self._mouse_hook.set_callbacks(
            on_down=self._on_mouse_hold_start,
            on_up=self._on_mouse_hold_stop,
        )

        # ── System tray ──────────────────────────────────────────────
        self._tray = TrayIcon(
            on_toggle=self._on_tray_toggle,
            on_show=self._on_tray_show,
            on_quit=self._on_tray_quit,
        )
        self._tray.start(is_running=False)

        # ── Build UI ─────────────────────────────────────────────────
        self._build_ui()
        self._hotkey_mgr.start()

        if self._settings.get("always_on_top"):
            self.attributes("-topmost", True)
            self._status_frame.set_topmost(True)

        self._poll_engine()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Build ────────────────────────────────────────────────────────

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ── Title with glow ──────────────────────────────────────────
        title_bg = ctk.CTkFrame(self, fg_color="transparent", height=50)
        title_bg.grid(row=0, column=0, pady=(12, 0), sticky="ew")
        title_bg.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            title_bg, text="⚡ OmniClick",
            font=ctk.CTkFont(family=T.FONT_FAMILY, size=T.FONT_TITLE + 1, weight="bold"),
            text_color=T.ACCENT_DIM,
        ).grid(row=0, column=0)

        ctk.CTkLabel(
            title_bg, text="⚡ OmniClick",
            font=ctk.CTkFont(family=T.FONT_FAMILY, size=T.FONT_TITLE, weight="bold"),
            text_color=T.ACCENT,
        ).grid(row=0, column=0)

        ctk.CTkLabel(
            self, text="Advanced Autoclicker",
            font=ctk.CTkFont(family=T.FONT_FAMILY, size=T.FONT_SUBTITLE),
            text_color=T.TEXT_DIM,
        ).grid(row=1, column=0, pady=(0, T.PAD_SM))

        # ── Tabview ──────────────────────────────────────────────────
        self._tabview = ctk.CTkTabview(
            self,
            fg_color=T.BG_SURFACE,
            segmented_button_fg_color=T.BG_ROOT,
            segmented_button_selected_color=T.TAB_SELECTED,
            segmented_button_selected_hover_color=T.TAB_SELECTED_HOVER,
            segmented_button_unselected_color=T.TAB_UNSELECTED,
            segmented_button_unselected_hover_color=T.TAB_UNSELECTED_HOVER,
            text_color=T.TAB_TEXT,
            corner_radius=T.RADIUS_CARD,
        )
        self._tabview.grid(row=2, column=0, padx=10, pady=(0, T.PAD_SM), sticky="nsew")

        # ── TAB: Main ────────────────────────────────────────────────
        tab_main = self._tabview.add("  ⚡ Main  ")
        tab_main.grid_columnconfigure(0, weight=1)
        tab_main.grid_rowconfigure(0, weight=1)

        scroll_main = ctk.CTkScrollableFrame(
            tab_main, fg_color="transparent",
            scrollbar_button_color=T.TAB_UNSELECTED,
            scrollbar_button_hover_color=T.TAB_UNSELECTED_HOVER,
        )
        scroll_main.grid(row=0, column=0, sticky="nsew")
        scroll_main.grid_columnconfigure(0, weight=1)

        self._status_frame = StatusFrame(
            scroll_main,
            on_topmost_toggle=self._on_topmost_toggle,
            on_start=self._on_start_pressed,
            on_stop=self._on_stop_pressed,
        )
        self._status_frame.grid(row=0, column=0, pady=(T.PAD_SM, T.PAD_MD))
        self._update_hints()

        ctk.CTkFrame(scroll_main, height=1, fg_color=T.BG_DIVIDER).grid(
            row=1, column=0, sticky="ew", padx=T.PAD_XL)

        self._cps_frame = CPSFrame(
            scroll_main,
            initial_cps=self._settings["cps"],
            initial_range=self._settings.get("cps_range", False),
            initial_min=self._settings.get("cps_min", 8.0),
            initial_max=self._settings.get("cps_max", 12.0),
            on_cps_change=self._on_cps_changed,
            on_range_toggle=self._on_range_toggle,
            on_range_min_change=self._on_range_min_changed,
            on_range_max_change=self._on_range_max_changed,
        )
        self._cps_frame.grid(row=2, column=0, pady=T.PAD_MD)

        ctk.CTkFrame(scroll_main, height=1, fg_color=T.BG_DIVIDER).grid(
            row=3, column=0, sticky="ew", padx=T.PAD_XL)

        self._mode_frame = ModeFrame(
            scroll_main,
            initial_mode=self._settings["mode"],
            initial_click_type=self._settings["click_type"],
            on_mode_change=self._on_mode_changed,
            on_click_type_change=self._on_click_type_changed,
        )
        self._mode_frame.grid(row=4, column=0, pady=T.PAD_MD, padx=T.PAD_MD, sticky="ew")

        # ── TAB: Effects ─────────────────────────────────────────────
        tab_fx = self._tabview.add(" 🎨 Effects ")
        tab_fx.grid_columnconfigure(0, weight=1)

        self._effects_frame = EffectsFrame(
            tab_fx,
            initial_jitter=self._settings.get("jitter_pixels", 0),
            initial_humanize=self._settings.get("humanize_pct", 0.10),
            on_jitter_change=self._on_jitter_changed,
            on_humanize_change=self._on_humanize_changed,
        )
        self._effects_frame.grid(row=0, column=0, pady=T.PAD_MD, padx=T.PAD_MD, sticky="ew")

        # ── TAB: Advanced (scrollable) ───────────────────────────────
        tab_adv = self._tabview.add(" ⚙ Advanced ")
        tab_adv.grid_columnconfigure(0, weight=1)
        tab_adv.grid_rowconfigure(0, weight=1)

        adv_scroll = ctk.CTkScrollableFrame(
            tab_adv, fg_color="transparent",
            scrollbar_button_color=T.TAB_UNSELECTED,
            scrollbar_button_hover_color=T.TAB_UNSELECTED_HOVER,
        )
        adv_scroll.grid(row=0, column=0, sticky="nsew")
        adv_scroll.grid_columnconfigure(0, weight=1)

        # Window targeting at top of Advanced
        self._target_frame = TargetWindowFrame(
            adv_scroll,
            initial_target=self._settings.get("target_window", ""),
            on_target_change=self._on_target_changed,
        )
        self._target_frame.grid(row=0, column=0, pady=(T.PAD_SM, T.PAD_MD), padx=T.PAD_MD, sticky="ew")

        self._advanced_frame = AdvancedFrame(
            adv_scroll,
            initial_clicks_per=self._settings.get("clicks_per_event", 1),
            initial_burst_count=self._settings.get("burst_count", 0),
            initial_burst_pause=self._settings.get("burst_pause", 0.5),
            initial_locations=self._settings.get("locations", []),
            initial_click_limit=self._settings.get("click_limit", 0),
            initial_start_delay=self._settings.get("start_delay", 0.0),
            initial_run_duration=self._settings.get("run_duration", 0.0),
            on_clicks_per_change=self._on_clicks_per_changed,
            on_burst_count_change=self._on_burst_count_changed,
            on_burst_pause_change=self._on_burst_pause_changed,
            on_locations_change=self._on_locations_changed,
            on_click_limit_change=self._on_click_limit_changed,
            on_start_delay_change=self._on_start_delay_changed,
            on_run_duration_change=self._on_run_duration_changed,
        )
        self._advanced_frame.grid(row=1, column=0, pady=(0, T.PAD_MD), padx=T.PAD_MD, sticky="ew")

        # ── TAB: Keybinds ────────────────────────────────────────────
        tab_kb = self._tabview.add(" ⌨ Keybinds ")
        tab_kb.grid_columnconfigure(0, weight=1)

        self._keybinds_frame = KeybindsFrame(
            tab_kb,
            keybinds=self._settings["keybinds"],
            on_listen=self._on_listen_clicked,
        )
        self._keybinds_frame.grid(row=0, column=0, pady=T.PAD_MD, padx=T.PAD_MD, sticky="ew")

        # ── Version + minimize hint ──────────────────────────────────
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=3, column=0, pady=(0, T.PAD_SM))

        ctk.CTkLabel(
            footer, text=f"v{VERSION}",
            font=ctk.CTkFont(family=T.FONT_MONO, size=9),
            text_color=T.TEXT_DISABLED,
        ).pack(side="left", padx=(0, T.PAD_MD))

        ctk.CTkButton(
            footer, text="Minimize to Tray", width=110, height=22,
            font=ctk.CTkFont(size=9),
            fg_color="transparent", hover_color=T.BG_ELEVATED,
            text_color=T.TEXT_DISABLED, corner_radius=T.RADIUS_SMALL,
            command=self._minimize_to_tray,
        ).pack(side="left")

    # ── Polling ──────────────────────────────────────────────────────

    def _poll_engine(self):
        running = self._engine.is_running
        self._status_frame.set_active(running)
        self._status_frame.update_click_count(self._engine.click_count)
        self._tray.update_running(running)
        self.after(100, self._poll_engine)

    # ── Helpers ──────────────────────────────────────────────────────

    def _update_hints(self):
        hotkey = self._settings["keybinds"].get("start_stop", "F6")
        mode = self._settings["mode"]
        self._status_frame.update_hint(hotkey, mode, self._armed)
        self._status_frame.set_mode_ui(mode)

    # ── Engine auto-stop ─────────────────────────────────────────────

    def _on_engine_auto_stop(self):
        self.after(0, self._handle_auto_stop)

    def _handle_auto_stop(self):
        self._status_frame.set_active(False)
        if self._armed:
            self._disarm()

    # ── System tray ──────────────────────────────────────────────────

    def _minimize_to_tray(self):
        self.withdraw()

    def _on_tray_toggle(self):
        self.after(0, self._on_hotkey_start_stop)

    def _on_tray_show(self):
        self.after(0, self._show_window)

    def _show_window(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def _on_tray_quit(self):
        self.after(0, self._on_close)

    # ── Callbacks: Main ──────────────────────────────────────────────

    def _on_cps_changed(self, cps: float):
        self._engine.cps = cps
        self._settings["cps"] = cps

    def _on_range_toggle(self, on: bool):
        self._engine.cps_range = on
        self._settings["cps_range"] = on

    def _on_range_min_changed(self, val: float):
        self._engine.cps_min = val
        self._settings["cps_min"] = val

    def _on_range_max_changed(self, val: float):
        self._engine.cps_max = val
        self._settings["cps_max"] = val

    def _on_mode_changed(self, mode: str):
        if self._armed:
            self._disarm()
        self._engine.stop()
        self._settings["mode"] = mode
        self._update_hints()

    def _on_click_type_changed(self, click_type: str):
        self._engine.click_type = click_type
        self._mouse_hook.set_button(click_type)
        self._settings["click_type"] = click_type

    # ── Callbacks: Effects ───────────────────────────────────────────

    def _on_jitter_changed(self, pixels: int):
        self._engine.jitter_pixels = pixels
        self._settings["jitter_pixels"] = pixels

    def _on_humanize_changed(self, pct: float):
        self._engine.humanize_pct = pct
        self._settings["humanize_pct"] = pct

    # ── Callbacks: Advanced ──────────────────────────────────────────

    def _on_clicks_per_changed(self, value: int):
        self._engine.clicks_per_event = value
        self._settings["clicks_per_event"] = value

    def _on_burst_count_changed(self, value: int):
        self._engine.burst_count = value
        self._settings["burst_count"] = value

    def _on_burst_pause_changed(self, value: float):
        self._engine.burst_pause = value
        self._settings["burst_pause"] = value

    def _on_locations_changed(self, locations: list):
        self._engine.locations = locations
        self._settings["locations"] = locations

    def _on_click_limit_changed(self, value: int):
        self._engine.click_limit = value
        self._settings["click_limit"] = value

    def _on_start_delay_changed(self, value: float):
        self._engine.start_delay = value
        self._settings["start_delay"] = value

    def _on_run_duration_changed(self, value: float):
        self._engine.run_duration = value
        self._settings["run_duration"] = value

    def _on_target_changed(self, value: str):
        self._engine.target_window = value
        self._settings["target_window"] = value

    def _on_topmost_toggle(self, value: bool):
        self.attributes("-topmost", value)
        self._settings["always_on_top"] = value

    # ── Keybind listen ───────────────────────────────────────────────

    def _on_listen_clicked(self, binding_name: str):
        self._hotkey_mgr.enter_listen_mode(binding_name, self._on_listen_complete)

    def _on_listen_complete(self, name: str, key_str: str):
        self.after(0, lambda: self._finish_listen(name, key_str))

    def _finish_listen(self, name: str, key_str: str):
        self._keybinds_frame.set_listening(name, False)
        self._keybinds_frame.set_key_text(name, key_str)
        self._settings["keybinds"][name] = key_str
        if name == "start_stop":
            self._update_hints()

    # ── Start / Stop ─────────────────────────────────────────────────

    def _on_start_pressed(self):
        if self._settings["mode"] == "toggle":
            self._engine.start()
        else:
            if not self._armed:
                self._arm()

    def _on_stop_pressed(self):
        if self._settings["mode"] == "toggle":
            self._engine.stop()
        else:
            if self._armed:
                self._disarm()

    def _on_hotkey_start_stop(self):
        if self._settings["mode"] == "toggle":
            self._engine.toggle()
        else:
            if self._armed:
                self._disarm()
            else:
                self._arm()

    # ── Cycle hotkeys ────────────────────────────────────────────────

    def _on_hotkey_cycle_click(self):
        cur = self._settings["click_type"]
        idx = CLICK_CYCLE.index(cur) if cur in CLICK_CYCLE else 0
        new_type = CLICK_CYCLE[(idx + 1) % len(CLICK_CYCLE)]
        self._engine.click_type = new_type
        self._mouse_hook.set_button(new_type)
        self._settings["click_type"] = new_type
        self.after(0, lambda: self._mode_frame.set_click_type(new_type))

    def _on_hotkey_cycle_mode(self):
        cur = self._settings["mode"]
        new_mode = "hold" if cur == "toggle" else "toggle"
        if self._armed:
            self._disarm()
        self._engine.stop()
        self._settings["mode"] = new_mode
        self.after(0, lambda: self._mode_frame.set_mode(new_mode))
        self.after(0, self._update_hints)

    # ── Hold mode ────────────────────────────────────────────────────

    def _arm(self):
        self._armed = True
        self._mouse_hook.set_button(self._settings["click_type"])
        self._mouse_hook.start()
        self.after(0, lambda: self._status_frame.set_armed(True))
        self.after(0, lambda: self._status_frame.update_hint(
            self._settings["keybinds"].get("start_stop", "F6"), "hold", True))

    def _disarm(self):
        self._armed = False
        self._engine.stop()
        self._mouse_hook.stop()
        self.after(0, lambda: self._status_frame.set_armed(False))
        self.after(0, lambda: self._status_frame.update_hint(
            self._settings["keybinds"].get("start_stop", "F6"), "hold", False))

    def _on_mouse_hold_start(self):
        if self._armed and not self._engine.is_running:
            self._engine.start()

    def _on_mouse_hold_stop(self):
        if self._armed and self._engine.is_running:
            self._engine.stop()

    # ── Cleanup ──────────────────────────────────────────────────────

    def _on_close(self):
        self._engine.stop()
        self._hotkey_mgr.stop()
        self._mouse_hook.stop()
        self._tray.stop()
        save_settings(self._settings)
        self.destroy()
        sys.exit(0)
