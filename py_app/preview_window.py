import random
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QScrollArea, QWidget,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QImage, QKeySequence, QShortcut

from PIL import Image, ImageEnhance

from styles import build_stylesheet
import theme
import ui_effects
from config import Config
from frameless import FramelessWindow
from widgets.glow_button import GlowButton
from i18n import t


def _pil_to_qpixmap(img: Image.Image) -> QPixmap:
    img_rgba = img.convert("RGBA")
    data = img_rgba.tobytes()
    qimg = QImage(data, img_rgba.width, img_rgba.height,
                  img_rgba.width * 4, QImage.Format.Format_RGBA8888)
    return QPixmap.fromImage(qimg)


def _apply_vhs(img: Image.Image) -> Image.Image:
    fx = ui_effects.active()
    t = theme.active
    if not fx.vhs_on_preview or t.surface_mode != "aether":
        return img.convert("RGB")
    img = img.convert("RGB")
    if t.surface_mode == "aether":
        img = ImageEnhance.Color(img).enhance(0.75)
        img = ImageEnhance.Contrast(img).enhance(1.05)
        overlay = Image.new("RGB", img.size, (40, 40, 40))
        img = Image.blend(img, overlay, 0.12)
    else:
        img = ImageEnhance.Color(img).enhance(0.82)
        img = ImageEnhance.Contrast(img).enhance(0.9)
        overlay = Image.new("RGB", img.size, (255, 77, 203))
        img = Image.blend(img, overlay, 0.07)
    px = img.load()
    w, h = img.size
    rng = random.Random(99)
    step = max(1, min(w, h) // 180)
    for y in range(0, h, step):
        for x in range(0, w, step):
            if rng.random() < 0.12:
                r, g, b = px[x, y]
                n = rng.randint(-20, 20)
                px[x, y] = (
                    max(0, min(255, r + n)),
                    max(0, min(255, g + n)),
                    max(0, min(255, b + n)),
                )
    return img


class PreviewWindow(FramelessWindow):
    def __init__(self, image: Image.Image, config: Config, parent=None):
        w, h = image.size
        super().__init__(
            t("preview.title"),
            f"{w} × {h}  ·  {config.image_format}",
            parent,
            glitch_title=(config.theme_id == "webcore"),
            geometry_slot="preview",
            config=config,
        )
        self._image = image
        self._config = config
        self._source_px: QPixmap | None = None
        self.setStyleSheet(build_stylesheet(theme.active))
        self.setMinimumSize(400, 300)
        self._build()
        self._setup_shortcuts()
        self._apply_initial_geometry()
        self._refresh_display()
        if config.copy_to_clipboard:
            QTimer.singleShot(80, self._auto_copy)

    def _build(self):
        root = self.content_layout()
        root.setSpacing(6)
        root.setContentsMargins(8, 4, 8, 6)

        self._scroll = QScrollArea()
        self._scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self._canvas = QWidget()
        self._canvas.setObjectName("preview_canvas")
        canvas_lay = QVBoxLayout(self._canvas)
        canvas_lay.setContentsMargins(8, 8, 8, 8)
        canvas_lay.setSpacing(0)

        self._lbl_image = QLabel()
        self._lbl_image.setObjectName("lbl_preview_image")
        self._lbl_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        canvas_lay.addWidget(self._lbl_image, 0, Qt.AlignmentFlag.AlignCenter)

        self._scroll.setWidget(self._canvas)
        root.addWidget(self._scroll, 1)

        bar = QHBoxLayout()
        bar.setSpacing(6)
        bar.setContentsMargins(0, 4, 0, 0)

        self._btn_copy = GlowButton(t("preview.copy"))
        self._btn_copy.setObjectName("btn_sky")
        self._btn_copy.setToolTip(t("preview.copy_tip"))
        self._btn_copy.clicked.connect(self._copy)
        self._btn_save = GlowButton(t("preview.save"))
        self._btn_save.setToolTip(t("preview.save_tip"))
        self._btn_save.clicked.connect(self._save_default)
        self._btn_save_as = QPushButton(t("preview.save_as"))
        self._btn_save_as.setObjectName("btn_secondary")
        self._btn_save_as.clicked.connect(self._save_as)
        self._btn_discard = QPushButton(t("preview.discard"))
        self._btn_discard.setObjectName("btn_discard")
        self._btn_discard.clicked.connect(self.reject)

        bar.addWidget(self._btn_copy)
        bar.addWidget(self._btn_save)
        bar.addWidget(self._btn_save_as)
        bar.addStretch()
        bar.addWidget(self._btn_discard)

        self._lbl_status = QLabel("")
        self._lbl_status.setStyleSheet(self._status_style(theme.active.cyan_hud))
        bar.addWidget(self._lbl_status)

        bar_wrap = QWidget()
        bar_wrap.setFixedHeight(44)
        bar_wrap.setLayout(bar)
        root.addWidget(bar_wrap)

    def _apply_initial_geometry(self):
        c = self._config
        if c.preview_width > 0 and c.preview_height > 0:
            self.restore_geometry()
            return
        screen = self.screen()
        if not screen:
            self.resize(720, 560)
            return
        avail = screen.availableGeometry()
        iw, ih = self._image.size
        win_w = min(iw + 80, avail.width() - 80)
        win_h = min(ih + 140, avail.height() - 60)
        self.resize(max(520, win_w), max(420, win_h))
        self.move(
            avail.x() + (avail.width() - self.width()) // 2,
            avail.y() + (avail.height() - self.height()) // 2,
        )

    def _setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+C"), self, activated=self._copy)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._save_default)
        QShortcut(QKeySequence("Escape"), self, activated=self.reject)

    def _refresh_display(self):
        display_img = _apply_vhs(self._image.copy())
        self._source_px = _pil_to_qpixmap(display_img)
        self._scale_to_viewport()

    def _scale_to_viewport(self):
        if self._source_px is None or self._source_px.isNull():
            return
        vp = self._scroll.viewport().size()
        if vp.width() < 4 or vp.height() < 4:
            return
        scaled = self._source_px.scaled(
            vp,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._lbl_image.setPixmap(scaled)
        self._lbl_image.setFixedSize(scaled.size())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self._scale_to_viewport)

    @staticmethod
    def _status_style(color: str) -> str:
        return (
            f"color:{color}; font-family:'Space Mono',monospace; "
            "font-size:11px; background:transparent;"
        )

    def retranslate(self):
        w, h = self._image.size
        self.set_title(t("preview.title"), f"{w} × {h}  ·  {self._config.image_format}")
        self._btn_copy.setText(t("preview.copy"))
        self._btn_copy.setToolTip(t("preview.copy_tip"))
        self._btn_save.setText(t("preview.save"))
        self._btn_save.setToolTip(t("preview.save_tip"))
        self._btn_save_as.setText(t("preview.save_as"))
        self._btn_discard.setText(t("preview.discard"))

    def refresh_theme(self):
        tk = theme.active
        w, h = self._image.size
        self.set_title(t("preview.title"), f"{w} × {h}  ·  {self._config.image_format}")
        self.setStyleSheet(build_stylesheet(tk))
        self._title_bar.refresh_theme()
        self._surface.refresh_theme()
        for child in self._content.findChildren(GlowButton):
            child.refresh_theme()
        self._lbl_status.setStyleSheet(self._status_style(tk.cyan_hud))
        self._refresh_display()
        for child in self._content.findChildren(QWidget):
            child.style().unpolish(child)
            child.style().polish(child)

    def _set_status(self, msg: str, color: str | None = None):
        color = color or theme.active.cyan_hud
        self._lbl_status.setStyleSheet(self._status_style(color))
        self._lbl_status.setText(msg)
        QTimer.singleShot(2800, lambda: self._lbl_status.setText(""))

    def _copy(self):
        try:
            from capture import image_to_clipboard
            image_to_clipboard(self._image)
            self._set_status(t("preview.copied"))
        except Exception as e:
            self._set_status(f"✗ {e}", theme.active.glitch_magenta)

    def _auto_copy(self):
        try:
            from capture import image_to_clipboard
            image_to_clipboard(self._image)
            self._set_status(t("preview.auto_copied"))
        except Exception:
            pass

    def _build_filename(self) -> str:
        now = datetime.now()
        name = self._config.filename_template
        name = name.replace("{datetime}", now.strftime("%Y-%m-%d_%H-%M-%S"))
        name = name.replace("{date}", now.strftime("%Y-%m-%d"))
        name = name.replace("{time}", now.strftime("%H-%M-%S"))
        ext = "jpg" if self._config.image_format == "JPEG" else self._config.image_format.lower()
        return f"{name}.{ext}"

    def _save_default(self):
        try:
            self._config.ensure_save_path()
            base = Path(self._config.save_path) / self._build_filename()
            n = 1
            while base.exists():
                base = base.parent / f"{base.stem}_{n}{base.suffix}"
                n += 1
            from capture import save_image
            save_image(self._image, str(base), self._config.image_format)
            self._set_status(t("preview.saved", name=base.name))
        except Exception as e:
            self._set_status(f"✗ {e}", theme.active.glitch_magenta)

    def _save_as(self):
        fmt = self._config.image_format
        filters = {
            "PNG": "PNG (*.png)",
            "JPEG": "JPEG (*.jpg *.jpeg)",
            "BMP": "BMP (*.bmp)",
            "TIFF": "TIFF (*.tiff *.tif)",
        }
        filt = ";;".join(filters.values())
        path, _ = QFileDialog.getSaveFileName(
            self, t("preview.save_dialog"),
            str(Path(self._config.save_path) / self._build_filename()),
            filt, filters.get(fmt, filters["PNG"]),
        )
        if path:
            try:
                ext = Path(path).suffix.lstrip(".").upper()
                ext = "JPEG" if ext in ("JPG", "JPEG") else (ext if ext in ("PNG", "BMP", "TIFF") else fmt)
                from capture import save_image
                save_image(self._image, path, ext)
                self._set_status(t("preview.saved", name=Path(path).name))
            except Exception as e:
                self._set_status(f"✗ {e}", theme.active.glitch_magenta)
