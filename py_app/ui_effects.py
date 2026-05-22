"""UI motion / density presets (full, calm, minimal)."""
from dataclasses import dataclass

_LEVELS = ("full", "calm", "minimal")


@dataclass(frozen=True)
class UIEffectsParams:
    particle_count_pinkcore: int
    particle_count_aether: int
    scanline_step_mult: float
    scanline_alpha_mult: float
    crt_enabled: bool
    crt_opacity_min: float
    marquee_enabled: bool
    marquee_speed: float
    marquee_opacity: int
    glow_pulse: bool
    image_holo: bool
    image_sparkles: bool
    image_washi: bool
    image_corners: bool
    vhs_on_preview: bool
    reading_panel_bg: str | None
    animate_background: bool
    holo_border: bool


_PRESETS: dict[str, UIEffectsParams] = {
    "full": UIEffectsParams(
        particle_count_pinkcore=220,
        particle_count_aether=140,
        scanline_step_mult=1.0,
        scanline_alpha_mult=1.0,
        crt_enabled=True,
        crt_opacity_min=0.92,
        marquee_enabled=True,
        marquee_speed=0.9,
        marquee_opacity=255,
        glow_pulse=True,
        image_holo=True,
        image_sparkles=True,
        image_washi=True,
        image_corners=True,
        vhs_on_preview=True,
        reading_panel_bg=None,
        animate_background=True,
        holo_border=True,
    ),
    "calm": UIEffectsParams(
        particle_count_pinkcore=90,
        particle_count_aether=80,
        scanline_step_mult=2.0,
        scanline_alpha_mult=0.5,
        crt_enabled=False,
        crt_opacity_min=1.0,
        marquee_enabled=False,
        marquee_speed=0.35,
        marquee_opacity=140,
        glow_pulse=False,
        image_holo=False,
        image_sparkles=False,
        image_washi=False,
        image_corners=True,
        vhs_on_preview=False,
        reading_panel_bg="rgba(26, 5, 48, 0.55)",
        animate_background=True,
        holo_border=False,
    ),
    "minimal": UIEffectsParams(
        particle_count_pinkcore=0,
        particle_count_aether=0,
        scanline_step_mult=3.0,
        scanline_alpha_mult=0.2,
        crt_enabled=False,
        crt_opacity_min=1.0,
        marquee_enabled=False,
        marquee_speed=0.0,
        marquee_opacity=0,
        glow_pulse=False,
        image_holo=False,
        image_sparkles=False,
        image_washi=False,
        image_corners=False,
        vhs_on_preview=False,
        reading_panel_bg="rgba(26, 5, 48, 0.65)",
        animate_background=False,
        holo_border=False,
    ),
}

_active: UIEffectsParams = _PRESETS["calm"]


def normalize_level(level: str | None) -> str:
    if level in _PRESETS:
        return level
    return "calm"


def set_level(level: str | None) -> UIEffectsParams:
    global _active
    _active = _PRESETS[normalize_level(level)]
    return _active


def active() -> UIEffectsParams:
    return _active


def level_labels() -> list[tuple[str, str]]:
    return [
        ("full", "Full effects"),
        ("calm", "Calm (default)"),
        ("minimal", "Minimal"),
    ]
