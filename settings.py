"""
OmniClick — Persistent settings manager.
"""

import json
import os

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

DEFAULT_SETTINGS = {
    "cps": 10.0,
    "mode": "toggle",
    "click_type": "left",
    "always_on_top": False,
    "jitter_pixels": 0,
    "humanize_pct": 0.10,
    "clicks_per_event": 1,
    "burst_count": 0,
    "burst_pause": 0.5,
    "locations": [],
    "cps_range": False,
    "cps_min": 8.0,
    "cps_max": 12.0,
    "click_limit": 0,
    "start_delay": 0.0,
    "run_duration": 0.0,
    "keybinds": {
        "start_stop":  "F6",
        "cycle_click": "",
        "cycle_mode":  "",
    },
    "target_window": "",
}


def load_settings() -> dict:
    settings = DEFAULT_SETTINGS.copy()
    settings["keybinds"] = DEFAULT_SETTINGS["keybinds"].copy()
    settings["locations"] = []
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            for key in DEFAULT_SETTINGS:
                if key in saved:
                    if key == "keybinds":
                        for k in DEFAULT_SETTINGS["keybinds"]:
                            if k in saved.get("keybinds", {}):
                                settings["keybinds"][k] = saved["keybinds"][k]
                    elif key == "locations":
                        settings["locations"] = [
                            (p[0], p[1]) for p in saved.get("locations", [])
                            if isinstance(p, (list, tuple)) and len(p) >= 2
                        ]
                    else:
                        settings[key] = saved[key]
        except (json.JSONDecodeError, OSError):
            pass
    return settings


def save_settings(settings: dict) -> None:
    try:
        data = dict(settings)
        data["locations"] = [list(p) for p in settings.get("locations", [])]
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass
