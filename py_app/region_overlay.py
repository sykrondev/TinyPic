from typing import Optional



from PyQt6.QtWidgets import QApplication, QWidget

from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal

from PyQt6.QtGui import (

    QPainter, QColor, QPixmap, QImage, QPen, QFont, QCursor, QBrush

)

from PIL import Image

import mss





def _pil_to_qpixmap(img: Image.Image) -> QPixmap:

    img_rgb = img.convert("RGB")

    data = img_rgb.tobytes()

    qimg = QImage(data, img_rgb.width, img_rgb.height,

                  img_rgb.width * 3, QImage.Format.Format_RGB888)

    return QPixmap.fromImage(qimg)





class RegionOverlay(QWidget):

    region_selected = pyqtSignal(int, int, int, int)

    cancelled       = pyqtSignal()



    _BLUE   = QColor("#B5179E")

    _CYAN   = QColor("#FF8FD6")

    _YELLOW = QColor("#FFD6F1")

    _DIM    = QColor(35, 0, 45, 145)



    def __init__(self):

        super().__init__()

        self._start: Optional[QPoint] = None

        self._cur:   Optional[QPoint] = None

        self._bg:    Optional[QPixmap] = None
        self._active = False

        self._setup()



    def _setup(self):

        self.setWindowFlags(

            Qt.WindowType.FramelessWindowHint

            | Qt.WindowType.WindowStaysOnTopHint

            | Qt.WindowType.Tool

        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)



    def start(self):
        if self._active:
            return

        with mss.mss() as sct:

            mon = sct.monitors[0]

            shot = sct.grab(mon)

            img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")

            self.setGeometry(mon["left"], mon["top"], mon["width"], mon["height"])



        self._bg = _pil_to_qpixmap(img)

        self._start = None

        self._cur = None
        self._active = True

        self.show()

        self.raise_()
        self.activateWindow()
        self.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        self.grabMouse(Qt.CursorShape.CrossCursor)
        self.grabKeyboard()
        QApplication.processEvents()



    def paintEvent(self, event):

        if not self._bg:

            return



        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        painter.drawPixmap(self.rect(), self._bg)

        painter.fillRect(self.rect(), self._DIM)



        if self._start and self._cur:

            sel = QRect(self._start, self._cur).normalized()



            painter.setCompositionMode(

                QPainter.CompositionMode.CompositionMode_DestinationOut

            )

            painter.fillRect(sel, QColor(0, 0, 0, 230))

            painter.setCompositionMode(

                QPainter.CompositionMode.CompositionMode_SourceOver

            )

            painter.drawPixmap(sel, self._bg, sel)



            painter.setBrush(Qt.BrushStyle.NoBrush)

            painter.setPen(QPen(QColor(255, 143, 214, 95), 6))

            painter.drawRect(sel.adjusted(-2, -2, 2, 2))

            painter.setPen(QPen(self._CYAN, 2))

            painter.drawRect(sel)



            painter.setBrush(QBrush(self._YELLOW))

            painter.setPen(Qt.PenStyle.NoPen)

            r = 4

            for c in [sel.topLeft(), sel.topRight(),

                      sel.bottomLeft(), sel.bottomRight()]:

                painter.drawRect(c.x() - r, c.y() - r, r * 2, r * 2)



            label = f"{sel.width()} x {sel.height()}"

            painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))

            fm = painter.fontMetrics()

            lw = fm.horizontalAdvance(label) + 18

            lh = fm.height() + 8

            lx = sel.x()

            ly = sel.y() - lh - 6

            if ly < 6:

                ly = sel.y() + 6



            painter.setBrush(QBrush(self._BLUE))

            painter.setPen(QPen(self._CYAN, 1))

            painter.drawRect(lx, ly, lw, lh)

            painter.setPen(QColor("#FFFFFF"))

            painter.drawText(lx + 9, ly + lh - 7, label)

            return



        pos = self.mapFromGlobal(QCursor.pos())

        painter.setPen(QPen(QColor(255, 143, 214, 130), 1))

        painter.drawLine(0, pos.y(), self.width(), pos.y())

        painter.drawLine(pos.x(), 0, pos.x(), self.height())



        painter.setBrush(QBrush(self._YELLOW))

        painter.setPen(Qt.PenStyle.NoPen)

        painter.drawRect(pos.x() - 4, pos.y() - 4, 8, 8)



        hint = "drag to capture | esc to cancel"

        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))

        fm = painter.fontMetrics()

        hw = fm.horizontalAdvance(hint) + 28

        hh = fm.height() + 16

        hx = (self.width() - hw) // 2

        hy = self.height() - hh - 48



        painter.setBrush(QBrush(QColor("#FFF4FC")))

        painter.setPen(QPen(self._CYAN, 2))

        painter.drawRect(hx, hy, hw, hh)

        painter.setPen(QColor("#7C2D92"))

        painter.drawText(hx + 14, hy + hh - 8, hint)



    def mouseMoveEvent(self, event):

        self._cur = event.pos()

        self.update()



    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self._start = event.pos()

            self._cur = event.pos()
            self.update()



    def mouseReleaseEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton and self._start:

            sel = QRect(self._start, event.pos()).normalized()

            self._finish()

            if sel.width() > 4 and sel.height() > 4:

                ox, oy = self.geometry().x(), self.geometry().y()

                self.region_selected.emit(

                    ox + sel.x(), oy + sel.y(), sel.width(), sel.height()

                )

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
        if not self._active:
            self.hide()
            return

        try:
            self.releaseMouse()
        except Exception:
            pass
        try:
            self.releaseKeyboard()
        except Exception:
            pass

        self._active = False
        self._start = None
        self._cur = None
        self.hide()
