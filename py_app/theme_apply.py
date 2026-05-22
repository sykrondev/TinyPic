import sys

from pathlib import Path

from typing import TYPE_CHECKING



from PyQt6.QtWidgets import (

    QApplication,

    QWidget,

    QPushButton,

    QLineEdit,

    QComboBox,

    QCheckBox,

)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QFontDatabase, QCursor, QPixmap




from theme import set_active, ThemeTokens, FONTS_DIR, CURSORS_DIR, active

from styles import build_stylesheet, sync_legacy_styles

import ui_effects



if TYPE_CHECKING:

    from frameless import FramelessWindow



_CURSOR_HOTSPOT = (2, 2)





def _asset_base() -> Path:

    if getattr(sys, "frozen", False):

        return Path(sys._MEIPASS)  # type: ignore[attr-defined]

    return Path(__file__).resolve().parent





def load_fonts():

    base = _asset_base() / "assets" / "fonts"

    if not base.is_dir():

        base = FONTS_DIR

    for ttf in base.glob("*.ttf"):

        QFontDatabase.addApplicationFont(str(ttf))





def _cursor_path(t: ThemeTokens) -> Path:

    base = _asset_base() / "assets" / "cursors"

    if not base.is_dir():

        base = CURSORS_DIR

    path = base / t.cursor_asset

    if path.is_file():

        return path

    return CURSORS_DIR / "pink_heart_pointer.png"





def make_theme_cursor(t: ThemeTokens | None = None) -> QCursor | None:

    t = t or active

    path = _cursor_path(t)

    if not path.is_file():

        return None

    px = QPixmap(str(path))

    if px.isNull():

        return None

    hx, hy = _CURSOR_HOTSPOT

    if t.cursor_asset.endswith("_cross.png"):

        hx, hy = px.width() // 2, px.height() // 2

    return QCursor(px, hx, hy)





def load_cursor(app: QApplication, t: ThemeTokens | None = None):

    """Default arrow for app; per-window cursors set in apply_window_cursors."""

    app.restoreOverrideCursor()

    app.setOverrideCursor(Qt.CursorShape.ArrowCursor)





def apply_window_cursors(window: "FramelessWindow"):

    t = active

    custom = make_theme_cursor(t)

    window._surface.setCursor(custom or Qt.CursorShape.ArrowCursor)

    window._title_bar.setCursor(custom or Qt.CursorShape.ArrowCursor)



    window._title_bar._close.setCursor(Qt.CursorShape.PointingHandCursor)



    for w in window._content.findChildren(QWidget):

        if w is window._content:

            continue

        if isinstance(w, QPushButton):

            w.setCursor(Qt.CursorShape.PointingHandCursor)

        elif isinstance(w, (QLineEdit, QComboBox, QCheckBox)):

            w.setCursor(Qt.CursorShape.ArrowCursor)

        else:

            w.setCursor(Qt.CursorShape.ArrowCursor)





def build_palette(t: ThemeTokens) -> QPalette:

    C = QColor

    pal = QPalette()

    pal.setColor(QPalette.ColorRole.Window, C(t.bg_base))

    pal.setColor(QPalette.ColorRole.WindowText, C(t.text_main))

    pal.setColor(QPalette.ColorRole.Base, C(t.bg_base))

    pal.setColor(QPalette.ColorRole.AlternateBase, C(t.secondary))

    pal.setColor(QPalette.ColorRole.ToolTipBase, C(t.bg_base))

    pal.setColor(QPalette.ColorRole.ToolTipText, C(t.accent))

    pal.setColor(QPalette.ColorRole.Text, C(t.text_main))

    pal.setColor(QPalette.ColorRole.Button, C(t.primary))

    pal.setColor(QPalette.ColorRole.ButtonText, C(t.text_main))

    pal.setColor(QPalette.ColorRole.BrightText, C(t.accent))

    pal.setColor(QPalette.ColorRole.Highlight, C(t.primary))

    pal.setColor(QPalette.ColorRole.HighlightedText, C(t.text_main))

    pal.setColor(QPalette.ColorRole.Link, C(t.secondary))

    pal.setColor(QPalette.ColorRole.PlaceholderText, C(t.text_muted))

    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, C(t.text_muted))

    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, C(t.text_muted))

    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, C(t.text_muted))

    return pal





def apply_theme(

    app: QApplication,

    theme_id: str,

    ui_effects_level: str | None = None,

) -> ThemeTokens:

    if ui_effects_level is not None:

        ui_effects.set_level(ui_effects_level)

    t = set_active(theme_id)

    app.setStyle("Fusion")

    sheet = build_stylesheet(t)

    sync_legacy_styles()

    app.setStyleSheet(sheet)

    app.setPalette(build_palette(t))

    load_cursor(app, t)

    return t


