from PyQt6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor

import theme
import ui_effects


class GlowButton(QPushButton):
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self._glow_dir = 1
        self._glow_alpha = 80
        self._fx = QGraphicsDropShadowEffect(self)
        self._fx.setBlurRadius(14)
        self._fx.setOffset(0, 2)
        self._fx.setColor(QColor(theme.active.primary))
        self.setGraphicsEffect(self._fx)
        self._timer = QTimer(self)
        self._timer.setInterval(60)
        self._timer.timeout.connect(self._pulse)
        self._apply_glow_mode()

    def refresh_theme(self):
        self._apply_glow_mode()

    def _apply_glow_mode(self):
        if ui_effects.active().glow_pulse:
            self._static_glow(80)
            if not self._timer.isActive():
                self._timer.start()
        else:
            self._timer.stop()
            self._static_glow(70)

    def _static_glow(self, alpha: int):
        c = QColor(theme.active.primary)
        c.setAlpha(alpha)
        self._fx.setColor(c)

    def enterEvent(self, event):
        if not ui_effects.active().glow_pulse:
            self._static_glow(130)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not ui_effects.active().glow_pulse:
            self._static_glow(70)
        super().leaveEvent(event)

    def _pulse(self):
        if not ui_effects.active().glow_pulse:
            return
        self._glow_alpha += self._glow_dir * 8
        if self._glow_alpha >= 160:
            self._glow_dir = -1
        elif self._glow_alpha <= 50:
            self._glow_dir = 1
        c = QColor(theme.active.primary)
        c.setAlpha(self._glow_alpha)
        self._fx.setColor(c)
