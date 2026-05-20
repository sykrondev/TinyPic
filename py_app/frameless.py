import random

from typing import Optional



from PyQt6.QtWidgets import (

    QDialog, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,

    QGraphicsDropShadowEffect, QSizePolicy,

)

from PyQt6.QtCore import Qt, QPoint, QPointF, QRectF, QTimer, pyqtSignal

from PyQt6.QtGui import (

    QPainter, QColor, QPen, QBrush, QLinearGradient, QPainterPath,

    QMouseEvent, QFont,

)









def soft_shadow(widget: QWidget, color: str = "#FF8FD6",

                blur: int = 24, alpha: int = 60, y: int = 4):

    fx = QGraphicsDropShadowEffect()

    fx.setBlurRadius(blur)

    c = QColor(color)

    c.setAlpha(alpha)

    fx.setColor(c)

    fx.setOffset(0, y)

    widget.setGraphicsEffect(fx)

    return fx









class StarrySurface(QWidget):






    RADIUS = 8

    STAR_COUNT = 220



    GRADIENT_TOP    = QColor("#17001F")

    GRADIENT_BOTTOM = QColor("#3A0A55")

    BORDER          = QColor("#FF8FD6")



    def __init__(self, parent=None):

        super().__init__(parent)

        self._stars: list = []

        self._tick = 0.0

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

        self.setAutoFillBackground(False)

        self._timer = QTimer(self)

        self._timer.setInterval(33)

        self._timer.timeout.connect(self._animate)

        self._timer.start()





    def resizeEvent(self, event):

        super().resizeEvent(event)

        self._regen_stars()



    def _regen_stars(self):

        rng = random.Random(7)

        w, h = self.width(), self.height()

        self._stars.clear()

        for _ in range(self.STAR_COUNT):

            x = rng.uniform(8, max(9, w - 8))

            y = rng.uniform(8, max(9, h - 8))

            size = rng.choice([1, 1, 2, 2, 3, 3, 4])

            opacity = rng.randint(120, 245)

            kind = rng.choice(['dot', 'dot', 'plus', 'sparkle', 'sparkle'])

            color = rng.choice(["#FFFFFF", "#FFD6F1", "#E0AAFF", "#FF8FD6"])

            speed = rng.uniform(0.18, 0.75)

            drift = rng.uniform(-0.22, 0.22)

            phase = rng.uniform(0, 6.28)

            self._stars.append([x, y, size, opacity, kind, color, speed, drift, phase])



    def _animate(self):

        if not self._stars:

            return

        self._tick += 0.033

        w, h = max(1, self.width()), max(1, self.height())

        for s in self._stars:

            s[0] += s[7]

            s[1] += s[6]

            if s[1] > h + 8:

                s[1] = -8

            if s[0] < -8:

                s[0] = w + 8

            elif s[0] > w + 8:

                s[0] = -8

        self.update()





    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)





        path = QPainterPath()

        rect = QRectF(0.5, 0.5, self.width() - 1, self.height() - 1)

        path.addRoundedRect(rect, self.RADIUS, self.RADIUS)



        grad = QLinearGradient(0, 0, 0, self.height())

        grad.setColorAt(0.0, self.GRADIENT_TOP)

        grad.setColorAt(0.45, QColor("#4A0D68"))

        grad.setColorAt(0.72, QColor("#9D2FAE"))

        grad.setColorAt(1.0, self.GRADIENT_BOTTOM)

        painter.fillPath(path, QBrush(grad))





        painter.setPen(QPen(self.BORDER, 1))

        painter.setBrush(Qt.BrushStyle.NoBrush)

        painter.drawPath(path)



        painter.setClipPath(path)





        for x, y, size, opacity, kind, color, speed, drift, phase in self._stars:

            xi, yi = int(x), int(y)

            col = QColor(color)

            col.setAlpha(opacity)

            pen = QPen(col, 1)

            painter.setPen(pen)

            painter.setBrush(QBrush(col))



            if kind == 'dot':

                painter.drawEllipse(QPointF(x, y), size / 2, size / 2)

            elif kind == 'plus':

                painter.drawLine(xi - size, yi, xi + size, yi)

                painter.drawLine(xi, yi - size, xi, yi + size)

            else:

                painter.drawLine(xi - size, yi, xi + size, yi)

                painter.drawLine(xi, yi - size, xi, yi + size)

                painter.drawLine(xi - size + 1, yi - size + 1, xi + size - 1, yi + size - 1)

                painter.drawLine(xi - size + 1, yi + size - 1, xi + size - 1, yi - size + 1)









class TitleBar(QWidget):

    close_clicked = pyqtSignal()

    def __init__(self, title: str = "", subtitle: str = "", parent=None):

        super().__init__(parent)

        self._drag_offset: Optional[QPoint] = None
        self.setObjectName("title_bar")
        self.setFixedHeight(56)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            "#title_bar { background-color:rgba(181, 23, 158, 190); "
            "border-top-left-radius:8px; border-top-right-radius:8px; "
            "border-bottom:1px solid rgba(255, 214, 241, 0.55); }"
        )

        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 12, 12, 8)
        lay.setSpacing(0)

        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        title_box.setContentsMargins(0, 0, 0, 0)

        self._title = QLabel(title)
        self._title.setStyleSheet(
            "color:#FFFFFF; font-family:'Segoe UI'; font-size:14px; "
            "font-weight:700; letter-spacing:0; background:transparent;"
        )

        self._subtitle = QLabel(subtitle)
        self._subtitle.setStyleSheet(
            "color:#FFE5F8; font-family:'Segoe UI'; font-size:11px; "
            "background:transparent;"
        )

        title_box.addWidget(self._title)
        if subtitle:
            title_box.addWidget(self._subtitle)

        lay.addLayout(title_box)
        lay.addStretch()

        self._close = QPushButton("x")
        self._close.setObjectName("btn_close")
        self._close.setFixedSize(32, 32)
        self._close.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close.clicked.connect(self.close_clicked.emit)
        lay.addWidget(self._close, alignment=Qt.AlignmentFlag.AlignTop)

    def set_title(self, title: str, subtitle: str = ""):

        self._title.setText(title)

        if subtitle:

            self._subtitle.setText(subtitle)

    def mousePressEvent(self, event: QMouseEvent):

        if event.button() == Qt.MouseButton.LeftButton:

            self._drag_offset = (

                event.globalPosition().toPoint() - self.window().pos()

            )

    def mouseMoveEvent(self, event: QMouseEvent):

        if self._drag_offset and event.buttons() & Qt.MouseButton.LeftButton:

            self.window().move(event.globalPosition().toPoint() - self._drag_offset)

    def mouseReleaseEvent(self, event: QMouseEvent):

        self._drag_offset = None


class FramelessWindow(QDialog):






    SHADOW_MARGIN = 18



    def __init__(self, title: str = "", subtitle: str = "", parent=None):

        super().__init__(parent)



        self.setWindowFlags(

            Qt.WindowType.FramelessWindowHint

            | Qt.WindowType.Dialog

        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)



        outer = QVBoxLayout(self)

        m = self.SHADOW_MARGIN

        outer.setContentsMargins(m, m, m, m)

        outer.setSpacing(0)



        self._surface = StarrySurface()

        self._surface.setSizePolicy(QSizePolicy.Policy.Expanding,

                                     QSizePolicy.Policy.Expanding)

        soft_shadow(self._surface, "#FF8FD6", blur=42, alpha=135, y=8)

        outer.addWidget(self._surface)



        surface_lay = QVBoxLayout(self._surface)

        surface_lay.setContentsMargins(0, 0, 0, 0)

        surface_lay.setSpacing(0)



        self._title_bar = TitleBar(title, subtitle, parent=self._surface)

        self._title_bar.close_clicked.connect(self.reject)

        surface_lay.addWidget(self._title_bar)



        self._content = QWidget()

        self._content.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._content_layout = QVBoxLayout(self._content)

        self._content_layout.setContentsMargins(18, 12, 18, 18)

        self._content_layout.setSpacing(14)

        surface_lay.addWidget(self._content, 1)





    def content_layout(self) -> QVBoxLayout:

        return self._content_layout



    def set_title(self, title: str, subtitle: str = ""):

        self._title_bar.set_title(title, subtitle)



    def surface(self) -> StarrySurface:

        return self._surface
