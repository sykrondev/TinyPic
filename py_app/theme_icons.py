from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter, QPolygonF, QPen

from theme import ThemeTokens, active


def _scale_pts(points, size: int):
    return QPolygonF([QPointF(x * size / 64, y * size / 64) for x, y in points])


def make_tray_icon_pinkcore(size: int = 64) -> QIcon:
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    pts = lambda points: _scale_pts(points, size)

    def poly(points, color):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(color))
        p.drawPolygon(pts(points))

    poly([(7, 25), (16, 18), (24, 18), (29, 12), (42, 12), (48, 18), (56, 18), (60, 25),
          (58, 49), (48, 56), (16, 56), (6, 49)], "#1a0530")
    poly([(9, 27), (17, 20), (25, 20), (30, 14), (41, 14), (47, 20), (54, 20), (57, 27),
          (55, 47), (47, 53), (17, 53), (9, 47)], "#ff4dcb")
    poly([(12, 28), (18, 22), (52, 22), (55, 29), (52, 47), (45, 51), (18, 51), (12, 46)], "#ffb3e6")
    poly([(12, 28), (18, 22), (31, 22), (27, 35), (12, 46)], "#ffffff")
    poly([(31, 22), (52, 22), (55, 29), (43, 36), (27, 35)], "#c44bff")
    poly([(12, 46), (27, 35), (32, 51), (18, 51)], "#aaffff")
    poly([(43, 36), (55, 29), (52, 47), (45, 51), (32, 51)], "#c44bff")
    poly([(25, 20), (30, 14), (41, 14), (47, 20)], "#ffb3e6")
    poly([(30, 14), (41, 14), (37, 20), (25, 20)], "#ff4dcb")
    poly([(45, 26), (52, 26), (52, 32), (45, 31)], "#aaffff")
    poly([(47, 27), (50, 27), (50, 30), (47, 30)], "#ffffff")
    p.setBrush(QColor("#1a0530"))
    p.drawEllipse(int(22 * size / 64), int(27 * size / 64), int(21 * size / 64), int(21 * size / 64))
    p.setBrush(QColor("#4466ff"))
    p.drawEllipse(int(25 * size / 64), int(30 * size / 64), int(15 * size / 64), int(15 * size / 64))
    p.setBrush(QColor("#c44bff"))
    p.drawPolygon(pts([(28, 31), (38, 34), (35, 42), (27, 40)]))
    p.setBrush(QColor("#ff4dcb"))
    p.drawPolygon(pts([(31, 33), (37, 35), (34, 39), (30, 38)]))
    p.setBrush(QColor("#aaffff"))
    p.drawPolygon(pts([(33, 32), (37, 34), (34, 35)]))
    p.end()
    return QIcon(px)


def make_tray_icon_aether(size: int = 64) -> QIcon:
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    pts = lambda points: _scale_pts(points, size)

    def poly(points, color):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(color))
        p.drawPolygon(pts(points))

    poly([(7, 25), (16, 18), (24, 18), (29, 12), (42, 12), (48, 18), (56, 18), (60, 25),
          (58, 49), (48, 56), (16, 56), (6, 49)], "#0a0a0a")
    poly([(9, 27), (17, 20), (25, 20), (30, 14), (41, 14), (47, 20), (54, 20), (57, 27),
          (55, 47), (47, 53), (17, 53), (9, 47)], "#2a2a2a")
    poly([(12, 28), (18, 22), (52, 22), (55, 29), (52, 47), (45, 51), (18, 51), (12, 46)], "#888888")
    poly([(12, 28), (18, 22), (31, 22), (27, 35), (12, 46)], "#cccccc")
    poly([(31, 22), (52, 22), (55, 29), (43, 36), (27, 35)], "#666666")
    poly([(12, 46), (27, 35), (32, 51), (18, 51)], "#aaaaaa")
    poly([(43, 36), (55, 29), (52, 47), (45, 51), (32, 51)], "#555555")
    poly([(25, 20), (30, 14), (41, 14), (47, 20)], "#bbbbbb")
    poly([(30, 14), (41, 14), (37, 20), (25, 20)], "#dddddd")
    p.setPen(QPen(QColor("#ffffff"), 2))
    p.drawLine(int(50 * size / 64), int(10 * size / 64), int(50 * size / 64), int(18 * size / 64))
    p.drawLine(int(46 * size / 64), int(14 * size / 64), int(54 * size / 64), int(14 * size / 64))
    p.setBrush(QColor("#000000"))
    p.drawEllipse(int(22 * size / 64), int(27 * size / 64), int(21 * size / 64), int(21 * size / 64))
    p.setBrush(QColor("#333333"))
    p.drawEllipse(int(25 * size / 64), int(30 * size / 64), int(15 * size / 64), int(15 * size / 64))
    p.setBrush(QColor("#888888"))
    p.drawPolygon(pts([(28, 31), (38, 34), (35, 42), (27, 40)]))
    p.setBrush(QColor("#cccccc"))
    p.drawPolygon(pts([(31, 33), (37, 35), (34, 39), (30, 38)]))
    p.setBrush(QColor("#ffffff"))
    p.drawPolygon(pts([(33, 32), (37, 34), (34, 35)]))
    p.end()
    return QIcon(px)


def make_tray_icon_webcore(size: int = 64) -> QIcon:
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    pts = lambda points: _scale_pts(points, size)

    def poly(points, color):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(color))
        p.drawPolygon(pts(points))

    poly([(7, 25), (16, 18), (24, 18), (29, 12), (42, 12), (48, 18), (56, 18), (60, 25),
          (58, 49), (48, 56), (16, 56), (6, 49)], "#020018")
    poly([(9, 27), (17, 20), (25, 20), (30, 14), (41, 14), (47, 20), (54, 20), (57, 27),
          (55, 47), (47, 53), (17, 53), (9, 47)], "#00d4ff")
    poly([(12, 28), (18, 22), (52, 22), (55, 29), (52, 47), (45, 51), (18, 51), (12, 46)], "#7b5cff")
    poly([(12, 28), (18, 22), (31, 22), (27, 35), (12, 46)], "#e8f4ff")
    poly([(31, 22), (52, 22), (55, 29), (43, 36), (27, 35)], "#1a3a6e")
    poly([(12, 46), (27, 35), (32, 51), (18, 51)], "#00ffff")
    poly([(43, 36), (55, 29), (52, 47), (45, 51), (32, 51)], "#4466ff")
    poly([(25, 20), (30, 14), (41, 14), (47, 20)], "#6eb8ff")
    poly([(30, 14), (41, 14), (37, 20), (25, 20)], "#00d4ff")
    poly([(45, 26), (52, 26), (52, 32), (45, 31)], "#00ffff")
    poly([(47, 27), (50, 27), (50, 30), (47, 30)], "#e8f4ff")
    p.setBrush(QColor("#020018"))
    p.drawEllipse(int(22 * size / 64), int(27 * size / 64), int(21 * size / 64), int(21 * size / 64))
    p.setBrush(QColor("#0a1848"))
    p.drawEllipse(int(25 * size / 64), int(30 * size / 64), int(15 * size / 64), int(15 * size / 64))
    p.setBrush(QColor("#00d4ff"))
    p.drawPolygon(pts([(28, 31), (38, 34), (35, 42), (27, 40)]))
    p.setBrush(QColor("#7b5cff"))
    p.drawPolygon(pts([(31, 33), (37, 35), (34, 39), (30, 38)]))
    p.setBrush(QColor("#00ffff"))
    p.drawPolygon(pts([(33, 32), (37, 34), (34, 35)]))
    p.end()
    return QIcon(px)


def make_tray_icon(t: ThemeTokens | None = None) -> QIcon:
    t = t or active
    if t.tray_icon_mode == "aether":
        return make_tray_icon_aether()
    if t.tray_icon_mode == "webcore":
        return make_tray_icon_webcore()
    return make_tray_icon_pinkcore()
