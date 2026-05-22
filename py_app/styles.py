from theme import ThemeTokens, active, FONT_DISPLAY, FONT_UI
import ui_effects


def build_stylesheet(t: ThemeTokens | None = None) -> str:
    t = t or active
    tid = t.id
    is_aether = tid == "aether"
    is_webcore = tid == "webcore"
    is_pinkcore = tid == "pinkcore"

    if is_webcore:
        btn_bg = "#0a0a1a"
        btn_fg = t.text_main
        btn_hover_bg = t.cyan_hud
        btn_hover_text = t.text_dark
        btn_pressed_bg = t.secondary
        input_bg = t.bg_input
        input_border = t.border_dark
        group_title_bg = "#0a2040"
    elif is_aether:
        btn_bg = "#1a1a1a"
        btn_fg = t.text_main
        btn_hover_bg = "#ffffff"
        btn_hover_text = t.text_dark
        btn_pressed_bg = "#333333"
        input_bg = "#0d0d0d"
        input_border = "#555555"
        group_title_bg = "#222222"
    else:
        btn_bg = t.primary
        btn_fg = t.text_main
        btn_hover_bg = t.accent
        btn_hover_text = t.text_dark
        btn_pressed_bg = t.secondary
        input_bg = t.bg_input
        input_border = t.secondary
        group_title_bg = t.secondary

    if is_webcore:
        btn_secondary_hover_bg = "rgba(0, 212, 255, 0.2)"
        btn_discard_hover_bg = "rgba(123, 92, 255, 0.25)"
        btn_hotkey_rec_bg = "rgba(0, 212, 255, 0.25)"
        btn_close_hover = t.primary
        btn_close_hover_text = t.text_dark
        group_border = "rgba(0, 212, 255, 0.35)"
        scroll_border = "rgba(0, 212, 255, 0.25)"
        lbl_image_bg = "rgba(0, 20, 40, 0.5)"
        btn_disabled_bg = "rgba(26, 58, 110, 0.5)"
        footer_bg = "rgba(2, 0, 24, 0.85)"
        footer_border = "rgba(0, 212, 255, 0.3)"
        preview_canvas_bg = "rgba(0, 20, 40, 0.5)"
    elif is_pinkcore:
        btn_secondary_hover_bg = "rgba(255, 179, 230, 0.45)"
        btn_discard_hover_bg = "rgba(255, 77, 203, 0.25)"
        btn_hotkey_rec_bg = "rgba(255, 77, 203, 0.35)"
        btn_close_hover = "#ff0066"
        btn_close_hover_text = t.text_main
        group_border = "rgba(255, 179, 230, 0.35)"
        scroll_border = "rgba(255, 179, 230, 0.3)"
        lbl_image_bg = "rgba(26, 5, 48, 0.6)"
        btn_disabled_bg = "rgba(196, 75, 255, 0.35)"
        footer_bg = "rgba(26, 5, 48, 0.75)"
        footer_border = "rgba(255, 179, 230, 0.35)"
        preview_canvas_bg = "rgba(0, 0, 0, 0.45)"
    else:
        btn_secondary_hover_bg = "rgba(255, 255, 255, 0.2)"
        btn_discard_hover_bg = "rgba(255, 255, 255, 0.12)"
        btn_hotkey_rec_bg = "rgba(255, 255, 255, 0.15)"
        btn_close_hover = "#ffffff"
        btn_close_hover_text = t.text_dark
        group_border = "rgba(255, 255, 255, 0.2)"
        scroll_border = "rgba(255, 255, 255, 0.15)"
        lbl_image_bg = "rgba(0, 0, 0, 0.5)"
        btn_disabled_bg = "rgba(80, 80, 80, 0.5)"
        footer_bg = "rgba(0, 0, 0, 0.75)"
        footer_border = "rgba(255, 255, 255, 0.15)"
        preview_canvas_bg = "rgba(0, 0, 0, 0.45)"

    fx = ui_effects.active()
    reading_bg = fx.reading_panel_bg
    if reading_bg is None and is_webcore:
        reading_bg = "rgba(5, 10, 32, 0.55)"
    if reading_bg is None:
        reading_bg = "transparent"

    return f"""
QWidget {{
    font-family: '{FONT_UI}', monospace;
    font-size: 11px;
    color: {t.text_main};
    background-color: transparent;
}}
QDialog {{ background: transparent; }}

QPushButton {{
    background-color: {btn_bg};
    color: {btn_fg};
    border: 2px solid {t.border_light};
    border-radius: 0px;
    padding: 8px 16px;
    font-family: '{FONT_DISPLAY}';
    font-size: 14px;
    min-width: 78px;
}}
QPushButton:hover {{
    background-color: {btn_hover_bg};
    color: {btn_hover_text};
    border: 2px solid {t.cyan_hud};
}}
QPushButton:pressed {{
    background-color: {btn_pressed_bg};
    padding-top: 9px;
    padding-left: 17px;
}}
QPushButton:disabled {{
    background-color: {btn_disabled_bg};
    color: {t.text_muted};
}}

QPushButton#btn_secondary {{
    background-color: {t.bg_panel};
    color: {t.accent};
    border: 2px solid {t.secondary};
}}
QPushButton#btn_secondary:hover {{
    background-color: {btn_secondary_hover_bg};
    color: {t.text_main};
}}

QPushButton#btn_sky {{
    background-color: {t.secondary};
    border-color: {t.cyan_hud};
}}
QPushButton#btn_sky:hover {{ background-color: {t.primary}; }}

QPushButton#btn_discard {{
    background-color: transparent;
    color: {t.text_muted};
    border: 2px solid transparent;
}}
QPushButton#btn_discard:hover {{
    background-color: {btn_discard_hover_bg};
    border-color: {t.primary};
}}

QPushButton#btn_round {{
    background-color: {t.bg_panel};
    border: 2px solid {t.accent};
    border-radius: 0px;
    padding: 4px 8px;
    min-width: 0;
    font-family: '{FONT_DISPLAY}';
    font-size: 14px;
}}

QPushButton#btn_hotkey {{
    background-color: {input_bg};
    color: {t.text_main};
    border: 2px solid {t.secondary};
    border-radius: 0px;
    padding: 6px 9px;
    font-family: '{FONT_UI}', monospace;
    font-size: 11px;
    text-align: left;
    min-width: 190px;
}}
QPushButton#btn_hotkey:hover {{
    border-color: {t.cyan_hud};
}}
QPushButton#btn_hotkey[recording="true"] {{
    background-color: {btn_hotkey_rec_bg};
    color: {t.accent};
    border-color: {t.primary};
}}

QPushButton#btn_close {{
    background-color: {t.accent};
    color: {t.text_dark};
    border: 2px solid {t.border_light};
    border-radius: 0px;
    font-family: 'Segoe UI';
    font-size: 14px;
    font-weight: bold;
    min-width: 26px;
    max-width: 26px;
    min-height: 26px;
    max-height: 26px;
    padding: 0px;
    margin: 0px;
}}
QPushButton#btn_close:hover {{
    background-color: {btn_close_hover};
    color: {btn_close_hover_text};
    border-color: {t.cyan_hud};
}}
QPushButton#btn_close:pressed {{
    padding: 0px;
    background-color: {t.primary};
}}

QLineEdit {{
    background-color: {input_bg};
    color: {t.text_main};
    border: 2px solid {input_border};
    border-radius: 0px;
    padding: 7px 10px;
    font-family: '{FONT_UI}', monospace;
    font-size: 11px;
    selection-background-color: {t.primary};
    selection-color: {t.text_main};
}}
QLineEdit:focus {{
    border-color: {t.cyan_hud};
}}
QLineEdit:disabled {{
    color: {t.text_muted};
}}

QComboBox {{
    background-color: {input_bg};
    color: {t.text_main};
    border: 2px solid {input_border};
    border-radius: 0px;
    padding: 6px 10px;
    font-family: '{FONT_UI}', monospace;
    min-width: 100px;
}}
QComboBox:hover, QComboBox:focus {{
    border-color: {t.cyan_hud};
}}
QComboBox::drop-down {{ border: none; width: 22px; }}
QComboBox::down-arrow {{ image: none; width: 0; height: 0; }}
QComboBox QAbstractItemView {{
    background-color: {t.bg_base};
    color: {t.accent};
    border: 2px solid {t.primary};
    selection-background-color: {t.primary};
    selection-color: {t.text_main};
    padding: 4px;
}}

QCheckBox {{
    color: {t.text_main};
    spacing: 9px;
    font-family: '{FONT_UI}', monospace;
}}
QCheckBox:hover {{ color: {t.accent}; }}
QCheckBox::indicator {{
    width: 14px;
    height: 14px;
    border: 2px solid {t.secondary};
    border-radius: 0px;
    background-color: {input_bg};
}}
QCheckBox::indicator:checked {{
    background-color: {t.primary};
    border-color: {t.cyan_hud};
}}

QWidget#settings_body {{
    background: transparent;
}}
QWidget#settings_reading_panel {{
    background-color: {reading_bg};
    border: none;
    border-radius: 0px;
}}
QWidget#settings_footer {{
    background-color: {footer_bg};
    border-top: 1px solid {footer_border};
}}
QGroupBox {{
    background-color: {t.bg_panel};
    color: {t.text_main};
    border: 2px solid {group_border};
    border-radius: 0px;
    margin-top: 22px;
    padding: 18px 12px 12px 12px;
    font-family: 'Segoe UI';
    font-size: 13px;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    top: 2px;
    padding: 2px 10px;
    background-color: {group_title_bg};
    color: {t.text_main};
    border: 2px solid {t.border_light};
}}

QLabel {{ background: transparent; color: {t.text_main}; }}
QLabel#lbl_field {{
    font-family: '{FONT_UI}', monospace;
    font-size: 12px;
    color: {t.text_main};
}}
QLabel#lbl_hint {{
    font-family: '{FONT_UI}', monospace;
    font-size: 10px;
    color: {t.text_muted};
}}
QLabel#lbl_info {{
    font-family: '{FONT_UI}', monospace;
    font-size: 11px;
    color: {t.cyan_hud};
    font-weight: bold;
}}
QLabel#lbl_image {{
    background-color: {lbl_image_bg};
    border: none;
}}
QWidget#preview_canvas {{
    background-color: {preview_canvas_bg};
    border: none;
}}
QLabel#lbl_preview_image {{
    background: transparent;
    border: none;
}}

QScrollArea {{
    border: 2px solid {scroll_border};
    border-radius: 0px;
    background-color: transparent;
}}
QScrollBar:vertical {{
    background: {t.bg_input};
    width: 10px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {t.primary};
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{ background: {t.accent}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}

QMenu {{
    background-color: {t.bg_base};
    color: {t.accent};
    border: 2px solid {t.primary};
    border-radius: 0px;
    padding: 5px;
    font-family: '{FONT_UI}', monospace;
}}
QMenu::item {{
    padding: 7px 28px 7px 14px;
}}
QMenu::item:selected {{
    background-color: {t.primary};
    color: {t.text_main};
}}
QMenu::separator {{
    height: 2px;
    background: {t.secondary};
    margin: 5px 4px;
}}

QToolTip {{
    background-color: {t.bg_base};
    color: {t.accent};
    border: 2px solid {t.primary};
    padding: 4px 7px;
    font-family: '{FONT_UI}', monospace;
}}
"""


def sync_legacy_styles():
    """Keep MAIN_STYLE / PREVIEW_STYLE aliases in sync after apply_theme."""
    global MAIN_STYLE, PREVIEW_STYLE
    sheet = build_stylesheet(active)
    MAIN_STYLE = sheet
    PREVIEW_STYLE = sheet
    return sheet


MAIN_STYLE = build_stylesheet(active)
PREVIEW_STYLE = MAIN_STYLE
