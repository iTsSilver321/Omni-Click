"""
OmniClick — Central design system.
All colors, fonts, spacing, and radii in one place for consistency.
"""


class Theme:
    """Design tokens for the entire application."""

    # ── Background layers ────────────────────────────────────────────
    BG_ROOT      = "#0d0d1a"   # Deepest, window root
    BG_SURFACE   = "#111125"   # Tab content / panels
    BG_CARD      = "#1a1a36"   # Card backgrounds
    BG_CARD_ALT  = "#1e1e3a"   # Alternate card shade
    BG_ELEVATED  = "#222244"   # Hover / focused elements
    BG_INPUT     = "#0e0e1e"   # Text entry fields
    BG_BORDER    = "#2a2a50"   # Subtle card borders
    BG_DIVIDER   = "#2a2a44"   # Section divider lines

    # ── Accent palette ───────────────────────────────────────────────
    ACCENT         = "#39FF14"   # Neon green (primary)
    ACCENT_DIM     = "#1a7a0a"   # Dimmed green
    ACCENT_HOVER   = "#30cc10"   # Green hover
    ACCENT_PURPLE  = "#7b68ee"   # Multiplier / secondary
    ACCENT_RED     = "#ff4757"   # Burst / danger / stop
    ACCENT_RED_DIM = "#8b2020"   # Dark red
    ACCENT_AMBER   = "#ffa502"   # Armed / warning / limit
    ACCENT_AMBER_DIM = "#7a5500"
    ACCENT_BLUE    = "#70a1ff"   # Schedule / info
    ACCENT_TEAL    = "#1dd1a1"   # Multi-location / success
    ACCENT_PINK    = "#ff6b81"   # Burst pause

    # ── Text colors ──────────────────────────────────────────────────
    TEXT_PRIMARY   = "#f0f0f0"
    TEXT_SECONDARY = "#bbbbbb"
    TEXT_MUTED     = "#888888"
    TEXT_DIM       = "#666666"
    TEXT_DISABLED  = "#444444"

    # ── Statuses ─────────────────────────────────────────────────────
    STATUS_IDLE       = "#555555"
    STATUS_IDLE_DIM   = "#333333"
    STATUS_ACTIVE     = ACCENT
    STATUS_ACTIVE_DIM = ACCENT_DIM
    STATUS_ARMED      = ACCENT_AMBER
    STATUS_ARMED_DIM  = ACCENT_AMBER_DIM

    # ── Fonts ────────────────────────────────────────────────────────
    FONT_FAMILY    = "Segoe UI"
    FONT_MONO      = "Consolas"
    FONT_TITLE     = 24
    FONT_SUBTITLE  = 11
    FONT_HEADING   = 13
    FONT_BODY      = 12
    FONT_CAPTION   = 10
    FONT_DATA      = 32
    FONT_COUNTER   = 13

    # ── Spacing ──────────────────────────────────────────────────────
    PAD_XS  = 2
    PAD_SM  = 4
    PAD_MD  = 8
    PAD_LG  = 14
    PAD_XL  = 20

    # ── Border radius ────────────────────────────────────────────────
    RADIUS_CARD    = 12
    RADIUS_INPUT   = 8
    RADIUS_BUTTON  = 10
    RADIUS_PILL    = 20
    RADIUS_SMALL   = 6

    # ── Button colors ────────────────────────────────────────────────
    BTN_START      = "#1e6b1e"
    BTN_START_HOVER = "#258f25"
    BTN_STOP       = "#6b1e1e"
    BTN_STOP_HOVER = "#8f2525"
    BTN_DISABLED   = "#2a2a3a"
    BTN_DISABLED_TEXT = "#555555"

    # ── Tab bar ──────────────────────────────────────────────────────
    TAB_BG         = "#16162e"
    TAB_SELECTED   = ACCENT
    TAB_SELECTED_HOVER = ACCENT_HOVER
    TAB_UNSELECTED = "#2a2a44"
    TAB_UNSELECTED_HOVER = "#3a3a55"
    TAB_TEXT       = "#000000"

    # ── Switch / toggle ──────────────────────────────────────────────
    SWITCH_ON      = ACCENT
    SWITCH_BUTTON  = "#e0e0e0"
    SWITCH_HOVER   = "#ffffff"

    # ── Slider ───────────────────────────────────────────────────────
    SLIDER_TRACK   = "#2a2a44"

    # ── Card factory ─────────────────────────────────────────────────
    @classmethod
    def card_kwargs(cls):
        """Standard card styling kwargs."""
        return dict(
            fg_color=cls.BG_CARD,
            border_width=1,
            border_color=cls.BG_BORDER,
            corner_radius=cls.RADIUS_CARD,
        )
