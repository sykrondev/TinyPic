"""Theme registry — PINKCORE, ÆTHER, WEBCORE."""
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

_ASSETS = Path(__file__).resolve().parent / "assets"
FONTS_DIR = _ASSETS / "fonts"
CURSORS_DIR = _ASSETS / "cursors"

FONT_DISPLAY = "VT323"
FONT_BODY = "Press Start 2P"
FONT_UI = "Space Mono"

_TOKEN_ALIASES = {
    "BG_BASE": "bg_base",
    "PRIMARY": "primary",
    "ACCENT": "accent",
    "SECONDARY": "secondary",
    "CYAN_HUD": "cyan_hud",
    "GLITCH_CYAN": "glitch_cyan",
    "GLITCH_MAGENTA": "glitch_magenta",
    "GLITCH_LIME": "glitch_lime",
    "TEXT_MAIN": "text_main",
    "TEXT_MUTED": "text_muted",
    "TEXT_DARK": "text_dark",
    "BG_PANEL": "bg_panel",
    "BG_INPUT": "bg_input",
    "BORDER_LIGHT": "border_light",
    "BORDER_DARK": "border_dark",
    "GRAD_TOP": "grad_top",
    "GRAD_MID": "grad_mid",
    "GRAD_LOW": "grad_low",
    "BLUE_GLOW": "blue_glow",
    "MARQUEE_DEFAULT": "marquee_text",
}


@dataclass(frozen=True)
class ThemeTokens:
    id: str
    label: str
    surface_mode: str
    bg_base: str
    primary: str
    accent: str
    secondary: str
    cyan_hud: str
    glitch_cyan: str
    glitch_magenta: str
    glitch_lime: str
    text_main: str
    text_muted: str
    text_dark: str
    bg_panel: str
    bg_input: str
    border_light: str
    border_dark: str
    grad_top: str
    grad_mid: str
    grad_low: str
    blue_glow: str
    marquee_text: str
    cursor_asset: str
    tray_icon_mode: str
    title_glow: bool
    holo_border: bool
    particle_symbols: tuple
    overlay_dim_alpha: int = 190
    scanline_step: int = 3
    scanline_alpha: int = 30


PINKCORE = ThemeTokens(
    id="pinkcore",
    label="PINKCORE",
    surface_mode="pinkcore",
    bg_base="#1a0530",
    primary="#ff4dcb",
    accent="#ffb3e6",
    secondary="#c44bff",
    cyan_hud="#aaffff",
    glitch_cyan="#00ffff",
    glitch_magenta="#ff00ff",
    glitch_lime="#e8ff00",
    text_main="#ffffff",
    text_muted="#ffb3e6",
    text_dark="#1a0530",
    bg_panel="rgba(255, 179, 230, 0.16)",
    bg_input="rgba(255, 179, 230, 0.25)",
    border_light="#ffb3e6",
    border_dark="#4a0d68",
    grad_top="#1a0530",
    grad_mid="#4a0d68",
    grad_low="#2d0a4a",
    blue_glow="#4466ff",
    marquee_text="♡ ★ ✧ TE AMO FLANISHY ♡ ★ ✧ ",
    cursor_asset="pink_heart_pointer.png",
    tray_icon_mode="pinkcore",
    title_glow=False,
    holo_border=True,
    particle_symbols=("✦", "✧", "♡", "★", "dot", "plus"),
    overlay_dim_alpha=190,
    scanline_step=6,
    scanline_alpha=18,
)

AETHER = ThemeTokens(
    id="aether",
    label="ÆTHER",
    surface_mode="aether",
    bg_base="#000000",
    primary="#ffffff",
    accent="#c8c8c8",
    secondary="#4a4a4a",
    cyan_hud="#e8e8e8",
    glitch_cyan="#cccccc",
    glitch_magenta="#888888",
    glitch_lime="#aaaaaa",
    text_main="#ffffff",
    text_muted="#888888",
    text_dark="#000000",
    bg_panel="rgba(255, 255, 255, 0.06)",
    bg_input="#0d0d0d",
    border_light="#ffffff",
    border_dark="#333333",
    grad_top="#000000",
    grad_mid="#0a0a0a",
    grad_low="#141414",
    blue_glow="#666666",
    marquee_text="† ÆTHERIUM † MMXXVI † ÆTHERIUM † ",
    cursor_asset="aether_cross.png",
    tray_icon_mode="aether",
    title_glow=True,
    holo_border=False,
    particle_symbols=("ash", "cross", "dot"),
    overlay_dim_alpha=178,
    scanline_step=4,
    scanline_alpha=40,
)

WEBCORE = ThemeTokens(
    id="webcore",
    label="WEBCORE",
    surface_mode="webcore",
    bg_base="#020018",
    primary="#00d4ff",
    accent="#7b5cff",
    secondary="#1a3a6e",
    cyan_hud="#00ffff",
    glitch_cyan="#00ffff",
    glitch_magenta="#ff44aa",
    glitch_lime="#a8ff00",
    text_main="#e8f4ff",
    text_muted="#6eb8ff",
    text_dark="#020018",
    bg_panel="rgba(0, 212, 255, 0.08)",
    bg_input="#050520",
    border_light="#00d4ff",
    border_dark="#0a1840",
    grad_top="#0a1848",
    grad_mid="#050a28",
    grad_low="#020010",
    blue_glow="#4466ff",
    marquee_text="+++ WEBCORE / TELL ME IM DREAMING +++ ",
    cursor_asset="aether_cross.png",
    tray_icon_mode="webcore",
    title_glow=False,
    holo_border=False,
    particle_symbols=("+", "†", "_", "dot", "★"),
    overlay_dim_alpha=200,
    scanline_step=3,
    scanline_alpha=45,
)

THEMES: Dict[str, ThemeTokens] = {
    "pinkcore": PINKCORE,
    "aether": AETHER,
    "webcore": WEBCORE,
}

active: ThemeTokens = PINKCORE


def set_active(theme_id: str) -> ThemeTokens:
    global active
    tid = theme_id if theme_id in THEMES else "pinkcore"
    active = THEMES[tid]
    return active


def theme_ids() -> list[str]:
    return list(THEMES.keys())


def __getattr__(name: str):
    if name in _TOKEN_ALIASES:
        return getattr(active, _TOKEN_ALIASES[name])
    if name == "PINK_CURSOR":
        return CURSORS_DIR / "pink_heart_pointer.png"
    raise AttributeError(f"module 'theme' has no attribute {name!r}")
