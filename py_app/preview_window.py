from pathlib import Path

from datetime import datetime



from PyQt6.QtWidgets import (

    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QScrollArea,

)

from PyQt6.QtCore import Qt, QSize, QTimer

from PyQt6.QtGui import QPixmap, QImage, QKeySequence, QShortcut



from PIL import Image



from styles import PREVIEW_STYLE

from config import Config

from frameless import FramelessWindow, soft_shadow





def _pil_to_qpixmap(img: Image.Image) -> QPixmap:

    img_rgba = img.convert("RGBA")

    data = img_rgba.tobytes()

    qimg = QImage(data, img_rgba.width, img_rgba.height,

                  img_rgba.width * 4, QImage.Format.Format_RGBA8888)

    return QPixmap.fromImage(qimg)





class PreviewWindow(FramelessWindow):

    def __init__(self, image: Image.Image, config: Config, parent=None):

        super().__init__("preview", "", parent)

        self._image  = image

        self._config = config

        self.setStyleSheet(PREVIEW_STYLE)

        self._build()

        self._setup_shortcuts()



        if config.copy_to_clipboard:

            QTimer.singleShot(80, self._auto_copy)







    def _build(self):

        root = self.content_layout()

        root.setSpacing(12)





        scroll = QScrollArea()

        scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)

        scroll.setWidgetResizable(False)

        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        scroll.setStyleSheet("background: transparent;")



        self._img_lbl = QLabel()

        self._img_lbl.setObjectName("lbl_image")

        self._img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._img_lbl.setContentsMargins(12, 12, 12, 12)

        self._refresh_display()

        scroll.setWidget(self._img_lbl)

        root.addWidget(scroll, 1)





        info_row = QHBoxLayout()

        info_row.setContentsMargins(2, 0, 2, 0)

        info_row.setSpacing(8)



        w, h = self._image.size

        self._lbl_info = QLabel(f"{w} x {h}  |  {self._config.image_format}")

        self._lbl_info.setObjectName("lbl_info")



        self._lbl_status = QLabel("")

        self._lbl_status.setStyleSheet(
            "color:#10B981; font-weight:700; font-size:12px; background:transparent;"
        )



        info_row.addWidget(self._lbl_info)

        info_row.addStretch()

        info_row.addWidget(self._lbl_status)

        root.addLayout(info_row)





        btn_row = QHBoxLayout()

        btn_row.setSpacing(8)



        self._btn_copy = QPushButton("Copy")

        self._btn_copy.setObjectName("btn_sky")

        self._btn_copy.setToolTip("Copy to clipboard | Ctrl+C")

        self._btn_copy.clicked.connect(self._copy)

        soft_shadow(self._btn_copy, "#FF8FD6", blur=18, alpha=95, y=2)



        self._btn_save = QPushButton("Save")

        self._btn_save.setToolTip("Save to default folder | Ctrl+S")

        self._btn_save.clicked.connect(self._save_default)

        soft_shadow(self._btn_save, "#FF8FD6", blur=18, alpha=95, y=2)



        self._btn_save_as = QPushButton("Save as...")

        self._btn_save_as.setObjectName("btn_secondary")

        self._btn_save_as.clicked.connect(self._save_as)



        self._btn_discard = QPushButton("Discard")

        self._btn_discard.setObjectName("btn_discard")

        self._btn_discard.clicked.connect(self.reject)



        btn_row.addWidget(self._btn_copy)

        btn_row.addWidget(self._btn_save)

        btn_row.addWidget(self._btn_save_as)

        btn_row.addStretch()

        btn_row.addWidget(self._btn_discard)



        root.addLayout(btn_row)





        screen = self.screen()

        if screen:

            avail = screen.availableGeometry()

            w2, h2 = self._image.size

            win_w  = min(w2 + 100, avail.width()  - 100)

            win_h  = min(h2 + 200, avail.height() - 80)

            self.resize(max(580, win_w), max(480, win_h))

            self.move(

                avail.x() + (avail.width()  - self.width())  // 2,

                avail.y() + (avail.height() - self.height()) // 2,

            )



    def _setup_shortcuts(self):

        QShortcut(QKeySequence("Ctrl+C"), self, activated=self._copy)

        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._save_default)

        QShortcut(QKeySequence("Escape"), self, activated=self.reject)



    def _refresh_display(self):

        px = _pil_to_qpixmap(self._image)

        screen = self.screen()

        if screen:

            avail = screen.availableGeometry()

            max_sz = QSize(avail.width() - 180, avail.height() - 260)

            if px.width() > max_sz.width() or px.height() > max_sz.height():

                px = px.scaled(

                    max_sz,

                    Qt.AspectRatioMode.KeepAspectRatio,

                    Qt.TransformationMode.SmoothTransformation,

                )

        self._img_lbl.setPixmap(px)

        self._img_lbl.adjustSize()







    def _set_status(self, msg: str, color: str = "#10B981"):

        self._lbl_status.setStyleSheet(

            f"color:{color}; font-weight:700; font-size:12px; background:transparent;"

        )

        self._lbl_status.setText(msg)

        QTimer.singleShot(2800, lambda: self._lbl_status.setText(""))



    def _copy(self):

        try:

            from capture import image_to_clipboard

            image_to_clipboard(self._image)

            self._set_status("copied!")

        except Exception as e:

            self._set_status(f"✗ {e}", "#DC2626")



    def _auto_copy(self):

        try:

            from capture import image_to_clipboard

            image_to_clipboard(self._image)

            self._set_status("auto-copied")

        except Exception:

            pass



    def _build_filename(self) -> str:

        now  = datetime.now()

        name = self._config.filename_template

        name = name.replace("{datetime}", now.strftime("%Y-%m-%d_%H-%M-%S"))

        name = name.replace("{date}",     now.strftime("%Y-%m-%d"))

        name = name.replace("{time}",     now.strftime("%H-%M-%S"))

        ext  = "jpg" if self._config.image_format == "JPEG" else self._config.image_format.lower()

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

            self._set_status(f"saved {base.name}")

        except Exception as e:

            self._set_status(f"✗ {e}", "#DC2626")



    def _save_as(self):

        fmt     = self._config.image_format

        filters = {

            "PNG":  "PNG (*.png)",

            "JPEG": "JPEG (*.jpg *.jpeg)",

            "BMP":  "BMP (*.bmp)",

            "TIFF": "TIFF (*.tiff *.tif)",

        }

        filt = ";;".join(filters.values())

        path, _ = QFileDialog.getSaveFileName(

            self, "Save screenshot",

            str(Path(self._config.save_path) / self._build_filename()),

            filt, filters.get(fmt, filters["PNG"]),

        )

        if path:

            try:

                ext = Path(path).suffix.lstrip(".").upper()

                ext = "JPEG" if ext in ("JPG", "JPEG") else (ext if ext in ("PNG", "BMP", "TIFF") else fmt)

                from capture import save_image

                save_image(self._image, path, ext)

                self._set_status(f"saved {Path(path).name}")

            except Exception as e:

                self._set_status(f"✗ {e}", "#DC2626")
