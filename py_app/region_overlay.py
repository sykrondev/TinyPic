from typing import Optional

from PIL import Image

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal, QTimer
from PyQt6.QtGui import (
    QPainter, QColor, QPixmap, QImage, QPen, QFont, QBrush, QGuiApplication,
    QCursor,
)

import mss

import theme
from theme import FONT_DISPLAY
from capture import qpixmap_to_pil


def _shot_to_pixmap(shot) -> QPixmap:
    qimg = QImage(
        shot.bgra, shot.width, shot.height,
        shot.width * 4, QImage.Format.Format_ARGB32,
    ).copy()
    return QPixmap.fromImage(qimg)


def _dim_color() -> QColor:
    t = theme.active
    base = QColor(t.bg_base)
    base.setAlpha(t.overlay_dim_alpha)
    return base


def _qt_virtual_desktop() -> QRect:
    """Union of all screens — includes negative x/y for monitors left/above primary."""
    area = QRect()
    for scr in QGuiApplication.screens():
        area = area.united(scr.geometry())
    if area.width() > 1 and area.height() > 1:
        return area
    screen = QGuiApplication.primaryScreen()
    if screen is not None:
        return screen.virtualGeometry()
    return QRect(0, 0, 1, 1)


def _align_overlay_to_capture(mon: dict, qt_rect: QRect) -> QRect:
    """Match overlay origin to mss virtual desktop (fixes dual-monitor top-left dead zone)."""
    if qt_rect.isNull() or qt_rect.width() <= 1 or qt_rect.height() <= 1:
        return QRect(mon["left"], mon["top"], mon["width"], mon["height"])
    x, y = qt_rect.x(), qt_rect.y()
    w, h = qt_rect.width(), qt_rect.height()
    if mon["left"] < x:
        w += x - mon["left"]
        x = mon["left"]
    if mon["top"] < y:
        h += y - mon["top"]
        y = mon["top"]
    return QRect(x, y, max(1, w), max(1, h))


class RegionOverlay(QWidget):
    region_selected = pyqtSignal(object)
    cancelled = pyqtSignal()

    _ZOOM_SCALE = 3
    _ZOOM_W = 170
    _ZOOM_H = 120
    _EDGE_BLEED = 8

    def __init__(self):
        super().__init__()
        self._start: Optional[QPoint] = None
        self._cur: Optional[QPoint] = None
        self._bg: Optional[QPixmap] = None
        self._layer_static: Optional[QPixmap] = None
        self._mss_mon: Optional[dict] = None
        self._capture_origin = QPoint(0, 0)
        self._capture_rect = QRect(0, 0, 1, 1)
        self._capture_global_rect = QRect(0, 0, 1, 1)
        self._window_rect = QRect(0, 0, 1, 1)
        self._active = False
        self._repaint_timer = QTimer(self)
        self._repaint_timer.setInterval(16)
        self._repaint_timer.timeout.connect(self._on_repaint_tick)
        self._setup()

    def refresh_theme(self):
        if self._bg and self.width() > 0:
            self._build_layer_static()
        self.update()

    def _setup(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)

    def _build_layer_static(self):
        if not self._bg:
            return
        w, h = self._capture_width(), self._capture_height()
        if w <= 0 or h <= 0:
            return
        t = theme.active
        layer = QPixmap(w, h)
        layer.fill(Qt.GlobalColor.transparent)
        p = QPainter(layer)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        p.drawPixmap(0, 0, self._bg)
        p.fillRect(0, 0, w, h, _dim_color())
        if t.surface_mode == "pinkcore":
            scan_color = QColor(0, 0, 0, 35)
            step = 5
        elif t.surface_mode == "webcore":
            scan_color = QColor(0, 212, 255, 40)
            step = 3
        else:
            scan_color = QColor(255, 255, 255, 25)
            step = 4
        p.setPen(QPen(scan_color))
        for y in range(0, h, step):
            p.drawLine(0, y, w, y)
        self._draw_hud_corners(p, QRect(0, 0, w, h))
        p.end()
        self._layer_static = layer

    def _capture_width(self) -> int:
        if self._bg and not self._bg.isNull():
            return max(1, self._bg.width())
        return max(1, self._capture_rect.width())

    def _capture_height(self) -> int:
        if self._bg and not self._bg.isNull():
            return max(1, self._bg.height())
        return max(1, self._capture_rect.height())

    def _capture_bounds(self) -> QRect:
        return QRect(0, 0, self._capture_width(), self._capture_height())

    def _clamp_point(self, pos: QPoint) -> QPoint:
        w, h = self._capture_width(), self._capture_height()
        return QPoint(max(0, min(pos.x(), w - 1)), max(0, min(pos.y(), h - 1)))

    def _global_to_capture_pos(self, pos: QPoint) -> QPoint:
        local = self.mapFromGlobal(pos)
        capture = QPoint(
            local.x() - self._capture_origin.x(),
            local.y() - self._capture_origin.y(),
        )
        return self._clamp_point(capture)

    def _local_pos(self, event) -> QPoint:
        if hasattr(event, "globalPosition"):
            return self._global_to_capture_pos(event.globalPosition().toPoint())
        pos = event.pos()
        capture = QPoint(
            pos.x() - self._capture_origin.x(),
            pos.y() - self._capture_origin.y(),
        )
        return self._clamp_point(capture)

    def _apply_overlay_geometry(self, rect: QRect, pix: QPixmap):
        bleed = self._EDGE_BLEED
        self._capture_origin = QPoint(bleed, bleed)
        self._capture_global_rect = QRect(rect)
        self._capture_rect = QRect(0, 0, max(1, rect.width()), max(1, rect.height()))
        self._window_rect = rect.adjusted(-bleed, -bleed, bleed, bleed)
        self.setGeometry(self._window_rect)
        self._sync_capture_origin()
        tw, th = max(1, rect.width()), max(1, rect.height())
        if pix.width() != tw or pix.height() != th:
            self._bg = pix.scaled(
                tw,
                th,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        else:
            self._bg = pix

    def _sync_capture_origin(self):
        geo = self.geometry()
        self._capture_origin = QPoint(
            max(0, self._capture_global_rect.x() - geo.x()),
            max(0, self._capture_global_rect.y() - geo.y()),
        )

    def _pin_overlay(self):
        if self.geometry() != self._window_rect:
            self.setGeometry(self._window_rect)
        self._sync_capture_origin()
        if not self.isVisible():
            self.show()
        self.raise_()
        try:
            import ctypes
            hwnd = int(self.winId())
            ctypes.windll.user32.SetWindowPos(
                hwnd,
                -1,  # HWND_TOPMOST
                self._window_rect.x(),
                self._window_rect.y(),
                self._window_rect.width(),
                self._window_rect.height(),
                0x0010 | 0x0040,  # SWP_NOACTIVATE | SWP_SHOWWINDOW
            )
        except Exception:
            pass
        self._sync_capture_origin()

    def start(self):
        if self._active:
            return
        qt_rect = _qt_virtual_desktop()
        with mss.mss() as sct:
            mon = dict(sct.monitors[0])
            shot = sct.grab(mon)
            pix = _shot_to_pixmap(shot)
        self._mss_mon = mon
        overlay_rect = _align_overlay_to_capture(mon, qt_rect)
        self._apply_overlay_geometry(overlay_rect, pix)
        self._build_layer_static()
        self._start = None
        self._cur = QPoint(self._capture_width() // 2, self._capture_height() // 2)
        self._active = True
        self._repaint_timer.start()
        self.show()
        QTimer.singleShot(0, self._pin_overlay)
        QTimer.singleShot(80, self._pin_overlay)
        self.raise_()
        self.activateWindow()
        self.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        QApplication.setOverrideCursor(Qt.CursorShape.BlankCursor)
        QApplication.processEvents()

    @staticmethod
    def _clamp_sel(sel: QRect, bounds: QRect) -> QRect:
        return sel.normalized().intersected(bounds)

    def _crop_selection(self, sel: QRect) -> Optional[Image.Image]:
        if not self._bg:
            return None
        bounds = self._capture_bounds()
        clipped = self._clamp_sel(sel, bounds)
        if clipped.width() < 1 or clipped.height() < 1:
            return None
        return qpixmap_to_pil(self._bg.copy(clipped))

    def _draw_hud_corners(self, painter: QPainter, r: QRect):
        t = theme.active
        painter.setPen(QPen(QColor(t.cyan_hud), 2))
        L = 20
        inset = 4
        corners = [
            (r.left() + inset, r.top() + inset, 1, 1),
            (r.right() - inset, r.top() + inset, -1, 1),
            (r.left() + inset, r.bottom() - inset, 1, -1),
            (r.right() - inset, r.bottom() - inset, -1, -1),
        ]
        for cx, cy, sx, sy in corners:
            painter.drawLine(cx, cy, cx + L * sx, cy)
            painter.drawLine(cx, cy, cx, cy + L * sy)

    def _draw_bracket_handles(self, painter: QPainter, sel: QRect):
        t = theme.active
        painter.setPen(QPen(QColor(t.cyan_hud), 2))
        L = 10
        for pt in [sel.topLeft(), sel.topRight(), sel.bottomLeft(), sel.bottomRight()]:
            cx, cy = pt.x(), pt.y()
            sx = 1 if cx == sel.left() else -1
            sy = 1 if cy == sel.top() else -1
            painter.drawLine(cx, cy, cx + L * sx, cy)
            painter.drawLine(cx, cy, cx, cy + L * sy)

    def paintEvent(self, event):
        if not self._bg or not self._layer_static:
            return
        t = theme.active
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.drawPixmap(self._capture_origin, self._layer_static)
        painter.translate(self._capture_origin)

        if self._start is not None and self._cur is not None:
            sel = self._clamp_sel(
                QRect(self._start, self._cur),
                self._capture_bounds(),
            )
            painter.drawPixmap(sel, self._bg, sel)
            accent = QColor(t.accent)
            accent.setAlpha(32)
            painter.fillRect(sel, accent)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(t.accent), 3))
            painter.drawRect(sel)
            self._draw_bracket_handles(painter, sel)
            label = f"{sel.width()} x {sel.height()}"
            painter.setFont(QFont(FONT_DISPLAY, 12))
            fm = painter.fontMetrics()
            lw = fm.horizontalAdvance(label) + 18
            lh = fm.height() + 8
            lx = sel.x()
            ly = sel.y() - lh - 6
            if ly < 6:
                ly = sel.y() + 6
            painter.setBrush(QBrush(QColor(t.secondary)))
            painter.setPen(QPen(QColor(t.cyan_hud), 2))
            painter.drawRect(lx, ly, lw, lh)
            painter.setPen(QColor(t.text_main))
            painter.drawText(lx + 9, ly + lh - 7, label)
            self._draw_pointer_marker(painter, self._cur)
            self._draw_zoom_lens(painter, self._cur)
            return

        pos = self._cur
        if pos is None:
            return
        self._draw_pointer_marker(painter, pos)

        if t.surface_mode == "pinkcore":
            hint = "✦ drag to capture | esc to cancel ✦"
        elif t.surface_mode == "webcore":
            hint = "+++ drag sector | esc abort +++"
        else:
            hint = "† drag to capture | esc to cancel †"
        painter.setFont(QFont(FONT_DISPLAY, 14))
        fm = painter.fontMetrics()
        hw = fm.horizontalAdvance(hint) + 28
        hh = fm.height() + 16
        hx = (self._capture_width() - hw) // 2
        hy = self._capture_height() - hh - 48
        painter.setBrush(QBrush(QColor(t.accent)))
        painter.setPen(QPen(QColor(t.cyan_hud), 2))
        painter.drawRect(hx, hy, hw, hh)
        hint_fg = t.text_dark if t.surface_mode == "pinkcore" else t.text_main
        painter.setPen(QColor(hint_fg))
        painter.drawText(hx + 14, hy + hh - 8, hint)
        self._draw_zoom_lens(painter, pos)

    def _draw_pointer_marker(self, painter: QPainter, pos: QPoint):
        t = theme.active
        painter.setPen(QPen(QColor(t.cyan_hud), 2))
        painter.setBrush(QBrush(QColor(t.accent)))
        painter.drawEllipse(pos, 5, 5)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawLine(pos.x() - 10, pos.y(), pos.x() + 10, pos.y())
        painter.drawLine(pos.x(), pos.y() - 10, pos.x(), pos.y() + 10)

    def _zoom_target_rect(self, pos: QPoint) -> QRect:
        zw, zh = self._ZOOM_W, self._ZOOM_H
        gap = 20
        x = pos.x() + gap
        y = pos.y() + gap
        cw, ch = self._capture_width(), self._capture_height()
        if x + zw > cw:
            x = pos.x() - zw - gap
        if y + zh > ch:
            y = pos.y() - zh - gap
        x = max(0, min(x, cw - zw))
        y = max(0, min(y, ch - zh))
        return QRect(x, y, zw, zh)

    def _zoom_source_rect(self, pos: QPoint) -> QRect:
        src_w = max(1, self._ZOOM_W // self._ZOOM_SCALE)
        src_h = max(1, self._ZOOM_H // self._ZOOM_SCALE)
        sx = pos.x() - src_w // 2
        sy = pos.y() - src_h // 2
        bounds = self._capture_bounds()
        return QRect(sx, sy, src_w, src_h).intersected(bounds)

    def _draw_zoom_lens(self, painter: QPainter, pos: QPoint):
        if not self._bg or pos is None:
            return
        t = theme.active
        target = self._zoom_target_rect(pos)
        source = self._zoom_source_rect(pos)
        if source.width() < 1 or source.height() < 1:
            return
        x, y = target.x(), target.y()
        tw, th = target.width(), target.height()
        painter.setBrush(QBrush(QColor(t.bg_base)))
        painter.setPen(QPen(QColor(t.accent), 1))
        painter.drawRect(target.adjusted(-2, -2, 2, 2))
        painter.setPen(QPen(QColor(t.cyan_hud), 2))
        painter.drawRect(target)
        painter.drawPixmap(target, self._bg, source)
        rx = (pos.x() - source.x()) / source.width()
        ry = (pos.y() - source.y()) / source.height()
        cx = x + int(rx * tw)
        cy = y + int(ry * th)
        painter.setPen(QPen(QColor(t.accent), 2))
        painter.drawLine(cx, y + 6, cx, y + th - 6)
        painter.drawLine(x + 6, cy, x + tw - 6, cy)
        painter.setBrush(QBrush(QColor(t.secondary)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(x, y - 22, 54, 20)
        painter.setPen(QColor(t.text_main))
        painter.setFont(QFont(FONT_DISPLAY, 11))
        painter.drawText(x + 8, y - 7, f"{self._ZOOM_SCALE}x")

    def _on_repaint_tick(self):
        if self._active:
            self._pin_overlay()
            self._cur = self._global_to_capture_pos(QCursor.pos())
        self.update()

    def mouseMoveEvent(self, event):
        self._cur = self._local_pos(event)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self._local_pos(event)
            self._start = pos
            self._cur = pos
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._start is not None:
            sel = self._clamp_sel(
                QRect(self._start, self._local_pos(event)),
                self._capture_bounds(),
            )
            img = self._crop_selection(sel) if sel.width() > 4 and sel.height() > 4 else None
            self._finish()
            if img is not None:
                self.region_selected.emit(img)
            else:
                self.cancelled.emit()
        elif event.button() == Qt.MouseButton.RightButton:
            self._cancel()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self._cancel()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        self._finish()
        super().closeEvent(event)

    def _cancel(self):
        self._finish()
        self.cancelled.emit()

    def _finish(self):
        self._repaint_timer.stop()
        if not self._active:
            self.hide()
            return
        self._active = False
        self._start = None
        self._cur = None
        self._layer_static = None
        self._bg = None
        self._mss_mon = None
        QApplication.restoreOverrideCursor()
        self.hide()
        self.repaint()
