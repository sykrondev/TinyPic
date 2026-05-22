from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont

import theme
from theme import FONT_DISPLAY


class GlitchLabel(QLabel):
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self._phase = 0
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self.setFont(QFont(FONT_DISPLAY, 20))
        self._timer = QTimer(self)
        self._timer.setInterval(120)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def refresh_theme(self):
        self.update()

    def _tick(self):
        self._phase = 1 - self._phase
        self.update()

    def paintEvent(self, event):
        t = theme.active
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        text = self.text()
        if not text:
            return
        r = self.rect()
        dx = 2 if self._phase else -2
        dy = 1 if self._phase else -1
        p.setFont(self.font())
        p.setPen(QColor(t.glitch_cyan))
        p.drawText(r.translated(dx, 0), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
        p.setPen(QColor(t.glitch_magenta))
        p.drawText(r.translated(-dx, dy), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
        p.setPen(QColor(t.text_main))
        p.drawText(r, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
