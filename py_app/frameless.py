import math
import random
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from config import Config

from PyQt6.QtWidgets import (
    QApplication, QDialog, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QGraphicsDropShadowEffect, QSizePolicy, QGraphicsOpacityEffect,
)
from PyQt6.QtCore import Qt, QPoint, QPointF, QRectF, QTimer, pyqtSignal, QEvent
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QLinearGradient, QRadialGradient,
    QPainterPath, QMouseEvent, QFont, QConicalGradient,
)

import theme
import ui_effects
from theme import ThemeTokens, FONT_DISPLAY, FONT_UI
from widgets.glitch_label import GlitchLabel
from styles import build_stylesheet
from theme_apply import apply_window_cursors, make_theme_cursor


def soft_shadow(widget: QWidget, color: str | None = None, blur: int = 18, alpha: int = 100, y: int = 4):
    t = theme.active
    color = color or t.primary
    fx = QGraphicsDropShadowEffect()
    fx.setBlurRadius(blur)
    c = QColor(color)
    c.setAlpha(alpha)
    fx.setColor(c)
    fx.setOffset(0, y)
    widget.setGraphicsEffect(fx)
    return fx


class PinkcoreSurface(QWidget):
    RADIUS = 8

    def __init__(self, parent=None):
        super().__init__(parent)
        self._particles: list = []
        self._tick = 0.0
        self._holo_angle = 0.0
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self.setAutoFillBackground(False)
        self._timer = QTimer(self)
        self._timer.setInterval(33)
        self._timer.timeout.connect(self._animate)
        self._apply_motion_mode()

    def _apply_motion_mode(self):
        fx = ui_effects.active()
        if fx.animate_background:
            if not self._timer.isActive():
                self._timer.start()
        else:
            self._timer.stop()
        self._regen_particles()
        self.update()

    def refresh_theme(self):
        self._apply_motion_mode()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._regen_particles()

    def _star_count(self) -> int:
        fx = ui_effects.active()
        mode = theme.active.surface_mode
        if mode == "pinkcore":
            return fx.particle_count_pinkcore
        return fx.particle_count_aether

    def _regen_particles(self):
        t = theme.active
        rng = random.Random(7)
        w, h = max(1, self.width()), max(1, self.height())
        self._particles.clear()
        pool = list(t.particle_symbols)
        if t.surface_mode == "pinkcore":
            colors = ["#ffffff", t.accent, t.cyan_hud, t.primary]
        elif t.surface_mode == "webcore":
            colors = ["#00ffff", "#00d4ff", "#e8f4ff", "#7b5cff"]
        else:
            colors = ["#666666", "#888888", "#aaaaaa", "#cccccc", "#ffffff"]
        for _ in range(self._star_count()):
            x = rng.uniform(8, max(9, w - 8))
            y = rng.uniform(8, max(9, h - 8))
            size = rng.choice([1, 2, 3, 4])
            opacity = rng.randint(80, 220)
            kind = rng.choice(pool)
            color = rng.choice(colors)
            if kind == "ash":
                speed = rng.uniform(0.35, 0.9)
                drift = rng.uniform(-0.15, 0.15)
            elif kind == "cross":
                speed = rng.uniform(0.02, 0.08)
                drift = rng.uniform(-0.05, 0.05)
            else:
                speed = rng.uniform(0.15, 0.7)
                drift = rng.uniform(-0.2, 0.2)
            phase = rng.uniform(0, 6.28)
            if kind == "cross":
                sym = rng.choice(["+", "†"])
            else:
                sym = kind
            self._particles.append([x, y, size, opacity, sym, color, speed, drift, phase, kind])

    def _animate(self):
        if not ui_effects.active().animate_background:
            return
        self._tick += 0.033
        self._holo_angle = (self._holo_angle + 2) % 360
        w, h = max(1, self.width()), max(1, self.height())
        mode = theme.active.surface_mode
        for s in self._particles:
            s[0] += s[7]
            if mode in ("pinkcore", "webcore"):
                s[1] += s[6]
                if s[1] > h + 8:
                    s[1] = -8
            elif s[9] == "ash":
                s[1] += s[6]
                if s[1] > h + 8:
                    s[1] = -8
            elif s[9] == "cross":
                pass
            else:
                s[1] += s[6] * 0.4
                if s[1] > h + 8:
                    s[1] = -8
            if s[0] < -8:
                s[0] = w + 8
            elif s[0] > w + 8:
                s[0] = -8
        self.update()

    def _paint_pinkcore(self, p: QPainter, rect: QRectF, t: ThemeTokens):
        fx = ui_effects.active()
        tick = self._tick if fx.animate_background else 0.0
        if fx.animate_background:
            blobs = [
                (0.25 + 0.08 * math.sin(tick * 0.4), 0.3 + 0.06 * math.cos(tick * 0.35), t.primary),
                (0.75 + 0.07 * math.cos(tick * 0.3), 0.65 + 0.08 * math.sin(tick * 0.42), t.secondary),
                (0.5 + 0.1 * math.sin(tick * 0.25), 0.5, t.blue_glow),
            ]
        else:
            blobs = [(0.25, 0.3, t.primary), (0.75, 0.65, t.secondary), (0.5, 0.5, t.blue_glow)]
        for i, (cx, cy, col) in enumerate(blobs):
            rg = QRadialGradient(rect.width() * cx, rect.height() * cy, rect.width() * 0.55)
            c = QColor(col)
            c.setAlpha(90 if i < 2 else 60)
            rg.setColorAt(0, c)
            rg.setColorAt(1, QColor(0, 0, 0, 0))
            p.fillRect(rect, QBrush(rg))
        lg = QLinearGradient(0, 0, rect.width(), rect.height())
        lg.setColorAt(0.0, QColor(t.grad_top))
        lg.setColorAt(0.45, QColor(t.grad_mid))
        lg.setColorAt(0.75, QColor(t.secondary))
        lg.setColorAt(1.0, QColor(t.grad_low))
        p.fillRect(rect, QBrush(lg))
        if fx.holo_border and t.holo_border:
            holo = QConicalGradient(rect.center(), self._holo_angle)
            holo.setColorAt(0, QColor(t.primary))
            holo.setColorAt(0.33, QColor(t.secondary))
            holo.setColorAt(0.66, QColor(t.blue_glow))
            holo.setColorAt(1, QColor(t.primary))
            p.setPen(QPen(QBrush(holo), 2))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRect(rect.adjusted(2, 2, -2, -2))

    def _paint_aether(self, p: QPainter, rect: QRectF, t: ThemeTokens):
        p.fillRect(rect, QColor(t.bg_base))
        rg = QRadialGradient(rect.center(), max(rect.width(), rect.height()) * 0.65)
        rg.setColorAt(0, QColor(30, 30, 30, 0))
        rg.setColorAt(0.7, QColor(0, 0, 0, 180))
        rg.setColorAt(1, QColor(0, 0, 0, 220))
        p.fillRect(rect, QBrush(rg))
        lg = QLinearGradient(0, 0, 0, rect.height())
        lg.setColorAt(0.0, QColor(t.grad_top))
        lg.setColorAt(0.5, QColor(t.grad_mid))
        lg.setColorAt(1.0, QColor(t.grad_low))
        p.fillRect(rect, QBrush(lg))

    def _paint_webcore(self, p: QPainter, rect: QRectF, t: ThemeTokens):
        p.fillRect(rect, QColor(t.bg_base))
        lg = QLinearGradient(0, 0, 0, rect.height())
        lg.setColorAt(0.0, QColor(t.grad_top))
        lg.setColorAt(0.45, QColor(t.grad_mid))
        lg.setColorAt(1.0, QColor(t.grad_low))
        p.fillRect(rect, QBrush(lg))
        rg = QRadialGradient(rect.width() * 0.5, rect.height() * 0.15, rect.width() * 0.75)
        glow = QColor(t.primary)
        glow.setAlpha(50)
        rg.setColorAt(0, glow)
        rg.setColorAt(1, QColor(0, 0, 0, 0))
        p.fillRect(rect, QBrush(rg))
        pen = QPen(QColor(t.cyan_hud), 1)
        p.setPen(pen)
        inset = 6
        L = 18
        corners = [
            (rect.left() + inset, rect.top() + inset, 1, 1),
            (rect.right() - inset, rect.top() + inset, -1, 1),
            (rect.left() + inset, rect.bottom() - inset, 1, -1),
            (rect.right() - inset, rect.bottom() - inset, -1, -1),
        ]
        for cx, cy, sx, sy in corners:
            p.drawLine(int(cx), int(cy), int(cx + L * sx), int(cy))
            p.drawLine(int(cx), int(cy), int(cx), int(cy + L * sy))

    def paintEvent(self, event):
        p = QPainter(self)
        t = theme.active
        mode = t.surface_mode
        is_pinkcore = mode == "pinkcore"
        p.setRenderHint(QPainter.RenderHint.Antialiasing, is_pinkcore)
        rect = QRectF(0.5, 0.5, max(1, self.width()) - 1, max(1, self.height()) - 1)
        clip_path = None
        if is_pinkcore:
            clip_path = QPainterPath()
            clip_path.addRoundedRect(rect, self.RADIUS, self.RADIUS)
            p.setClipPath(clip_path)

        if mode == "aether":
            self._paint_aether(p, rect, t)
        elif mode == "webcore":
            self._paint_webcore(p, rect, t)
        else:
            self._paint_pinkcore(p, rect, t)

        if mode in ("aether", "webcore"):
            p.setPen(QPen(QColor(t.border_light), 2))
            p.drawLine(0, 0, int(rect.width()), 0)
            p.drawLine(0, 0, 0, int(rect.height()))
            p.setPen(QPen(QColor(t.border_dark), 2))
            p.drawLine(int(rect.width()) - 1, 0, int(rect.width()) - 1, int(rect.height()))
            p.drawLine(0, int(rect.height()) - 1, int(rect.width()), int(rect.height()) - 1)

        anim = ui_effects.active().animate_background
        for x, y, size, opacity, sym, color, speed, drift, phase, kind in self._particles:
            pulse = 0.7 + 0.3 * math.sin(phase + self._tick * 3) if anim else 1.0
            col = QColor(color)
            col.setAlpha(int(opacity * pulse))
            p.setPen(col)
            if sym in ("✦", "✧", "♡", "★", "+", "†"):
                p.setFont(QFont(FONT_DISPLAY, int(size * 4 + 6)))
                p.drawText(int(x), int(y), sym)
            elif kind == "ash":
                p.setBrush(QBrush(col))
                p.drawEllipse(QPointF(x, y), size / 2 * pulse, size / 4 * pulse)
            elif sym == "dot" or kind == "dot":
                p.setBrush(QBrush(col))
                p.drawEllipse(QPointF(x, y), size / 2 * pulse, size / 2 * pulse)
            else:
                xi, yi = int(x), int(y)
                p.drawLine(xi - size, yi, xi + size, yi)
                p.drawLine(xi, yi - size, xi, yi + size)

        fx = ui_effects.active()
        scan_alpha = max(0, int(t.scanline_alpha * fx.scanline_alpha_mult))
        scan_step = max(1, int(t.scanline_step * fx.scanline_step_mult))
        if mode == "webcore":
            p.setPen(QPen(QColor(0, 212, 255, scan_alpha)))
        elif mode == "aether":
            p.setPen(QPen(QColor(255, 255, 255, scan_alpha // 2)))
        else:
            p.setPen(QPen(QColor(0, 0, 0, scan_alpha)))
        for y in range(0, int(rect.height()), scan_step):
            p.drawLine(0, y, int(rect.width()), y)

        p.setClipping(False)
        if clip_path is not None:
            p.setPen(QPen(QColor(t.border_light), 1))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPath(clip_path)


class CrtFlickerOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        fx = QGraphicsOpacityEffect(self)
        fx.setOpacity(1.0)
        self.setGraphicsEffect(fx)
        self._fx = fx
        self._timer = QTimer(self)
        self._timer.setInterval(80)
        self._timer.timeout.connect(self._flicker)
        self._apply_crt_mode()

    def _apply_crt_mode(self):
        fx = ui_effects.active()
        if fx.crt_enabled:
            self._fx.setOpacity(1.0)
            if not self._timer.isActive():
                self._timer.start()
        else:
            self._timer.stop()
            self._fx.setOpacity(1.0)

    def _flicker(self):
        import random
        fx = ui_effects.active()
        if not fx.crt_enabled:
            self._fx.setOpacity(1.0)
            return
        lo = fx.crt_opacity_min
        self._fx.setOpacity(random.uniform(lo, 1.0))

    def paintEvent(self, event):
        pass


class TitleBar(QWidget):
    close_clicked = pyqtSignal()

    def __init__(self, title: str = "", subtitle: str = "", parent=None, use_glitch: bool = False):
        super().__init__(parent)
        self._drag_offset: Optional[QPoint] = None
        self._use_glitch = use_glitch
        self.setObjectName("title_bar")
        if subtitle:
            bar_h = 56
        elif use_glitch:
            bar_h = 36
        else:
            bar_h = 30
        self.setFixedHeight(bar_h)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._apply_bar_style()

        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 12, 12, 8)
        lay.setSpacing(0)

        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        title_box.setContentsMargins(0, 0, 0, 0)

        if use_glitch:
            self._title = GlitchLabel(title)
            self._title.setFixedHeight(22)
        else:
            self._title = QLabel(title)
            self._refresh_title_style()

        self._subtitle = QLabel(subtitle)
        self._refresh_subtitle_style()

        title_box.addWidget(self._title)
        if subtitle:
            title_box.addWidget(self._subtitle)

        lay.addLayout(title_box)
        lay.addStretch()

        self._close = QPushButton("×")
        self._close.setObjectName("btn_close")
        self._close.setFixedSize(26, 26)
        self._close.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._close.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close.clicked.connect(self.close_clicked.emit)
        self._refresh_close_style()
        lay.addWidget(self._close, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    def _apply_bar_style(self):
        t = theme.active
        if t.surface_mode == "aether":
            self.setStyleSheet(
                f"#title_bar {{ background: qlineargradient("
                f"x1:0,y1:0,x2:1,y2:0, stop:0 #1a1a1a, stop:1 #000000); "
                f"border-bottom: 2px solid {t.border_dark}; }}"
            )
        elif t.surface_mode == "webcore":
            self.setStyleSheet(
                f"#title_bar {{ background: qlineargradient("
                f"x1:0,y1:0,x2:1,y2:0, stop:0 #0a1848, stop:1 #020010); "
                f"border-bottom: 2px solid {t.primary}; }}"
            )
        else:
            self.setStyleSheet(
                f"#title_bar {{ background-color: rgba(181, 23, 158, 190); "
                f"border-top-left-radius: 8px; border-top-right-radius: 8px; "
                f"border-bottom: 1px solid rgba(255, 214, 241, 0.55); }}"
            )

    def _refresh_title_style(self):
        if self._use_glitch:
            return
        t = theme.active
        glow = ""
        if t.title_glow:
            glow += " letter-spacing:1px;"
        if t.surface_mode == "pinkcore":
            font = "'Segoe UI'"
        else:
            font = f"'{FONT_DISPLAY}'"
        self._title.setStyleSheet(
            f"color:#FFFFFF; font-family:{font}; font-size:15px; font-weight:700; "
            f"letter-spacing:0; background:transparent;{glow}"
        )

    def _refresh_subtitle_style(self):
        t = theme.active
        if t.surface_mode == "pinkcore":
            sub_color = "#FFE5F8"
            font = "'Segoe UI'"
        else:
            sub_color = t.text_muted if t.surface_mode == "webcore" else t.text_main
            font = f"'{FONT_UI}',monospace"
        self._subtitle.setStyleSheet(
            f"color:{sub_color}; font-family:{font}; font-size:11px; "
            f"background:transparent;"
        )

    def _refresh_close_style(self):
        t = theme.active
        if t.surface_mode == "pinkcore":
            hover_bg, hover_fg = "#ff0066", "#ffffff"
        elif t.surface_mode == "webcore":
            hover_bg, hover_fg = t.primary, t.text_dark
        else:
            hover_bg, hover_fg = "#ffffff", "#000000"
        self._close.setStyleSheet(
            f"QPushButton#btn_close {{"
            f"  background-color: {t.accent};"
            f"  color: {t.text_dark};"
            f"  border: 2px solid {t.border_light};"
            f"  border-radius: 0px;"
            f"  font-family: 'Segoe UI';"
            f"  font-size: 14px;"
            f"  font-weight: bold;"
            f"  padding: 0px;"
            f"  margin: 0px;"
            f"  min-width: 26px; max-width: 26px;"
            f"  min-height: 26px; max-height: 26px;"
            f"}}"
            f"QPushButton#btn_close:hover {{"
            f"  background-color: {hover_bg};"
            f"  color: {hover_fg};"
            f"  border-color: {t.cyan_hud};"
            f"}}"
            f"QPushButton#btn_close:pressed {{"
            f"  padding: 0px;"
            f"  background-color: {t.primary};"
            f"}}"
        )

    def refresh_theme(self):
        self._apply_bar_style()
        if self._use_glitch and hasattr(self._title, "refresh_theme"):
            self._title.refresh_theme()
        elif not self._use_glitch:
            self._refresh_title_style()
        self._refresh_subtitle_style()
        self._refresh_close_style()

    def set_title(self, title: str, subtitle: str = ""):
        self._title.setText(title)
        if subtitle:
            self._subtitle.setText(subtitle)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.window().pos()
            win = self.window()
            if hasattr(win, "_surface") and hasattr(win._surface, "_timer"):
                win._surface._timer.stop()
                ge = win._surface.graphicsEffect()
                if ge:
                    ge.setEnabled(False)
            if hasattr(win, "_crt") and hasattr(win._crt, "_timer"):
                win._crt._timer.stop()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_offset and event.buttons() & Qt.MouseButton.LeftButton:
            self.window().move(event.globalPosition().toPoint() - self._drag_offset)

    def mouseReleaseEvent(self, event: QMouseEvent):
        win = self.window()
        if hasattr(win, "_surface"):
            if hasattr(win._surface, "_apply_motion_mode"):
                win._surface._apply_motion_mode()
            ge = win._surface.graphicsEffect()
            if ge:
                ge.setEnabled(True)
        if hasattr(win, "_crt") and hasattr(win._crt, "_apply_crt_mode"):
            win._crt._apply_crt_mode()
        self._drag_offset = None


StarrySurface = PinkcoreSurface


def _cursor_for_resize_edge(edge: Qt.Edge | None) -> Qt.CursorShape:
    if edge is None:
        return Qt.CursorShape.ArrowCursor
    if edge == (Qt.Edge.LeftEdge | Qt.Edge.TopEdge):
        return Qt.CursorShape.SizeFDiagCursor
    if edge == (Qt.Edge.RightEdge | Qt.Edge.TopEdge):
        return Qt.CursorShape.SizeBDiagCursor
    if edge == (Qt.Edge.LeftEdge | Qt.Edge.BottomEdge):
        return Qt.CursorShape.SizeBDiagCursor
    if edge == (Qt.Edge.RightEdge | Qt.Edge.BottomEdge):
        return Qt.CursorShape.SizeFDiagCursor
    if edge & Qt.Edge.LeftEdge or edge & Qt.Edge.RightEdge:
        return Qt.CursorShape.SizeHorCursor
    if edge & Qt.Edge.TopEdge or edge & Qt.Edge.BottomEdge:
        return Qt.CursorShape.SizeVerCursor
    return Qt.CursorShape.ArrowCursor


class ResizeEdgeGrip(QWidget):
    """Invisible strip on window edge for native resize."""

    def __init__(self, edge: Qt.Edge, parent: QWidget):
        super().__init__(parent)
        self._edge = edge
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setStyleSheet("background: transparent;")
        self.setCursor(_cursor_for_resize_edge(edge))
        self.setMouseTracking(True)

    def enterEvent(self, event):
        win = self.window()
        if hasattr(win, "_set_resize_override"):
            win._set_resize_override(self._edge)
        super().enterEvent(event)

    def leaveEvent(self, event):
        win = self.window()
        if hasattr(win, "_clear_resize_override"):
            win._clear_resize_override()
        super().leaveEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        win = self.window()
        if hasattr(win, "_set_resize_override"):
            win._set_resize_override(self._edge)
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            win = self.window()
            wh = win.windowHandle() if win else None
            if wh is not None:
                wh.startSystemResize(self._edge)
            event.accept()
            return
        super().mousePressEvent(event)


class FramelessWindow(QDialog):
    SHADOW_MARGIN = 18
    RESIZE_GRIP = 7

    def __init__(
        self,
        title: str = "",
        subtitle: str = "",
        parent=None,
        glitch_title: bool = False,
        geometry_slot: str | None = None,
        config: "Config | None" = None,
    ):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self._geometry_slot = geometry_slot
        self._config = config
        self._geom_timer = QTimer(self)
        self._geom_timer.setSingleShot(True)
        self._geom_timer.setInterval(300)
        self._geom_timer.timeout.connect(self._persist_geometry)

        outer = QVBoxLayout(self)
        m = self.SHADOW_MARGIN
        outer.setContentsMargins(m, m, m, m)
        outer.setSpacing(0)

        self._surface = PinkcoreSurface()
        self._surface.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        t = theme.active
        soft_shadow(self._surface, t.primary, blur=6 if t.surface_mode == "pinkcore" else 4, alpha=80, y=4)
        outer.addWidget(self._surface)

        surface_lay = QVBoxLayout(self._surface)
        surface_lay.setContentsMargins(0, 0, 0, 0)
        surface_lay.setSpacing(0)

        self._title_bar = TitleBar(title, subtitle, parent=self._surface, use_glitch=glitch_title)
        self._title_bar.close_clicked.connect(self.reject)
        surface_lay.addWidget(self._title_bar)

        self._content = QWidget()
        self._content.setObjectName("content_panel")
        self._content.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(16, 10, 16, 14)
        self._content_layout.setSpacing(12)
        surface_lay.addWidget(self._content, 1)
        self._apply_content_panel_style()

        self._crt = CrtFlickerOverlay(self._content)
        self._content.installEventFilter(self)
        self._resize_cursor_active = False
        apply_window_cursors(self)

        self._grip_widgets: dict[str, ResizeEdgeGrip] = {}
        for name, edge in (
            ("tl", Qt.Edge.LeftEdge | Qt.Edge.TopEdge),
            ("tr", Qt.Edge.RightEdge | Qt.Edge.TopEdge),
            ("bl", Qt.Edge.LeftEdge | Qt.Edge.BottomEdge),
            ("br", Qt.Edge.RightEdge | Qt.Edge.BottomEdge),
            ("top", Qt.Edge.TopEdge),
            ("left", Qt.Edge.LeftEdge),
            ("right", Qt.Edge.RightEdge),
            ("bottom", Qt.Edge.BottomEdge),
        ):
            g = ResizeEdgeGrip(edge, self)
            self._grip_widgets[name] = g
        self._wire_resize_cursor_tracking()

    def _wire_resize_cursor_tracking(self):
        tracked: list[QWidget] = [self, self._surface, self._title_bar]
        tracked.extend(self._grip_widgets.values())
        tracked.extend(self._title_bar.findChildren(QWidget))
        seen: set[int] = set()
        for w in tracked:
            if w is self._crt or id(w) in seen:
                continue
            seen.add(id(w))
            w.setMouseTracking(True)
            w.installEventFilter(self)

    def _clear_resize_override(self):
        if self._resize_cursor_active:
            QApplication.restoreOverrideCursor()
            self._resize_cursor_active = False

    def _set_resize_override(self, edge: Qt.Edge):
        c = _cursor_for_resize_edge(edge)
        if self._resize_cursor_active:
            QApplication.changeOverrideCursor(c)
        else:
            QApplication.setOverrideCursor(c)
            self._resize_cursor_active = True

    def _apply_content_panel_style(self):
        self._content.setStyleSheet("QWidget#content_panel { background: transparent; }")

    def refresh_theme(self):
        t = theme.active
        self.setStyleSheet(build_stylesheet(t))
        self._apply_content_panel_style()
        self._title_bar.refresh_theme()
        self._surface.refresh_theme()
        self._crt._apply_crt_mode()
        soft_shadow(self._surface, t.primary, blur=6 if t.surface_mode == "pinkcore" else 4, alpha=80, y=4)
        self._content.update()
        apply_window_cursors(self)

    def _hit_surface_resize_edge(self, pos: QPoint) -> Qt.Edge | None:
        s = self._surface.geometry()
        g = self.RESIZE_GRIP
        x, y = pos.x(), pos.y()
        sx, sy, sw, sh = s.x(), s.y(), s.width(), s.height()
        on_l = sx <= x < sx + g
        on_r = sx + sw - g < x <= sx + sw
        on_t = sy <= y < sy + g
        on_b = sy + sh - g < y <= sy + sh
        if not (on_l or on_r or on_t or on_b):
            return None
        edge = Qt.Edge(0)
        if on_l:
            edge |= Qt.Edge.LeftEdge
        if on_r:
            edge |= Qt.Edge.RightEdge
        if on_t:
            edge |= Qt.Edge.TopEdge
        if on_b:
            edge |= Qt.Edge.BottomEdge
        return edge if edge else None

    def _position_resize_grips(self):
        g = self.RESIZE_GRIP
        grips = self._grip_widgets
        if not grips:
            return
        s = self._surface.geometry()
        sx, sy, sw, sh = s.x(), s.y(), max(1, s.width()), max(1, s.height())
        grips["tl"].setGeometry(sx, sy, g, g)
        grips["tr"].setGeometry(sx + sw - g, sy, g, g)
        grips["bl"].setGeometry(sx, sy + sh - g, g, g)
        grips["br"].setGeometry(sx + sw - g, sy + sh - g, g, g)
        grips["top"].setGeometry(sx + g, sy, max(1, sw - 2 * g), g)
        grips["left"].setGeometry(sx, sy + g, g, max(1, sh - 2 * g))
        grips["right"].setGeometry(sx + sw - g, sy + g, g, max(1, sh - 2 * g))
        grips["bottom"].setGeometry(sx + g, sy + sh - g, max(1, sw - 2 * g), g)
        self._surface.lower()
        for grip in grips.values():
            grip.raise_()

    def _geometry_tuple(self) -> tuple[int, int, int, int]:
        if not self._config or not self._geometry_slot:
            return 0, 0, -1, -1
        c = self._config
        if self._geometry_slot == "settings":
            return c.settings_width, c.settings_height, c.settings_x, c.settings_y
        if self._geometry_slot == "preview":
            return c.preview_width, c.preview_height, c.preview_x, c.preview_y
        return 0, 0, -1, -1

    def restore_geometry(self):
        w, h, x, y = self._geometry_tuple()
        if w > 0 and h > 0:
            self.resize(max(self.minimumWidth(), w), max(self.minimumHeight(), h))
        if x >= 0 and y >= 0:
            self.move(x, y)

    def _persist_geometry(self):
        if not self._config or not self._geometry_slot:
            return
        w, h = self.width(), self.height()
        x, y = self.x(), self.y()
        c = self._config
        if self._geometry_slot == "settings":
            c.settings_width, c.settings_height = w, h
            c.settings_x, c.settings_y = x, y
        elif self._geometry_slot == "preview":
            c.preview_width, c.preview_height = w, h
            c.preview_x, c.preview_y = x, y
        c.save()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_resize_grips()
        if self._geometry_slot:
            self._geom_timer.start()

    def moveEvent(self, event):
        super().moveEvent(event)
        if self._geometry_slot:
            self._geom_timer.start()

    def closeEvent(self, event):
        self._clear_resize_override()
        self._persist_geometry()
        super().closeEvent(event)

    def reject(self):
        self._persist_geometry()
        super().reject()

    def _apply_surface_cursor_at(self, global_pos: QPoint):
        edge = self._hit_surface_resize_edge(self.mapFromGlobal(global_pos))
        if edge is not None:
            self._set_resize_override(edge)
            return
        self._clear_resize_override()

    def eventFilter(self, obj, event):
        et = event.type()
        if et in (QEvent.Type.MouseMove, QEvent.Type.HoverMove):
            if hasattr(event, "globalPosition"):
                self._apply_surface_cursor_at(event.globalPosition().toPoint())
        elif et == QEvent.Type.MouseButtonPress:
            if (
                event.button() == Qt.MouseButton.LeftButton
                and self._hit_surface_resize_edge(
                    self.mapFromGlobal(event.globalPosition().toPoint())
                )
                is not None
            ):
                edge = self._hit_surface_resize_edge(
                    self.mapFromGlobal(event.globalPosition().toPoint())
                )
                wh = self.windowHandle()
                if wh is not None and edge is not None:
                    wh.startSystemResize(edge)
                    return True
        elif et in (QEvent.Type.Leave, QEvent.Type.HoverLeave):
            if obj is self:
                self._clear_resize_override()
        if obj is self._content and et == QEvent.Type.Resize:
            self._crt.setGeometry(self._content.rect())
        return super().eventFilter(obj, event)

    def hideEvent(self, event):
        self._clear_resize_override()
        super().hideEvent(event)

    def content_layout(self) -> QVBoxLayout:
        return self._content_layout

    def set_title(self, title: str, subtitle: str = ""):
        self._title_bar.set_title(title, subtitle)

    def surface(self) -> PinkcoreSurface:
        return self._surface

    def showEvent(self, event):
        super().showEvent(event)
        self._crt.setGeometry(self._content.rect())
        self._crt.raise_()
        self._position_resize_grips()
