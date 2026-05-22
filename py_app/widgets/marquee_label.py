from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QFont, QColor, QFontMetrics

import theme
import ui_effects
from theme import FONT_DISPLAY


class MarqueeLabel(QWidget):
    def __init__(self, text: str | None = None, parent=None):
        super().__init__(parent)
        self._segment = text if text is not None else theme.active.marquee_text
        self._offset = 0.0
        self._segment_w = 0
        self.setFixedHeight(18)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._timer = QTimer(self)
        self._timer.setInterval(24)
        self._timer.timeout.connect(self._tick)
        self._update_metrics()
        self._apply_mode()

    def refresh_theme(self):
        self._segment = theme.active.marquee_text
        self._update_metrics()
        self._apply_mode()
        self.update()

    def _apply_mode(self):
        fx = ui_effects.active()
        if fx.marquee_enabled and fx.marquee_speed > 0:
            if not self._timer.isActive():
                self._timer.start()
            self.setVisible(True)
        else:
            self._timer.stop()
            self.setVisible(fx.marquee_enabled)

    def _update_metrics(self):
        fm = QFontMetrics(QFont(FONT_DISPLAY, 14))
        self._segment_w = max(1, fm.horizontalAdvance(self._segment))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_metrics()

    def _tick(self):
        fx = ui_effects.active()
        self._offset += fx.marquee_speed
        self.update()

    def paintEvent(self, event):
        fx = ui_effects.active()
        if not fx.marquee_enabled:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        col = QColor(theme.active.accent)
        col.setAlpha(fx.marquee_opacity)
        p.setPen(col)
        p.setFont(QFont(FONT_DISPLAY, 14))
        if self._segment_w <= 0:
            self._update_metrics()
        sw = self._segment_w
        y = (self.height() + p.fontMetrics().ascent() - p.fontMetrics().descent()) // 2
        x = -(self._offset % sw)
        limit = self.width() + sw
        while x < limit:
            p.drawText(int(x), y, self._segment)
            x += sw
