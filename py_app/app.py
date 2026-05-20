import time

import threading
import traceback

from pathlib import Path

from typing import Optional



from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu

from PyQt6.QtCore import Qt, QTimer, QObject, pyqtSignal, QPointF

from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter, QPolygonF



from PIL import Image



from config import Config

from capture import capture_fullscreen, capture_region, capture_active_window

from hotkeys import HotkeyManager

from region_overlay import RegionOverlay

from preview_window import PreviewWindow

from settings_window import SettingsWindow

from styles import MAIN_STYLE


def _log_error(title: str, exc: BaseException):
    try:
        path = Path.home()
        import os
        path = Path(os.environ.get("APPDATA", path)) / "TinyPic" / "crash.log"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n[{title}]\n")
            traceback.print_exception(type(exc), exc, exc.__traceback__, file=f)
    except Exception:
        pass





def _make_icon(size: int = 64) -> QIcon:



    px = QPixmap(size, size)

    px.fill(Qt.GlobalColor.transparent)



    p = QPainter(px)

    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)



    def pts(points):

        return QPolygonF([QPointF(x * size / 64, y * size / 64) for x, y in points])



    p.setPen(Qt.PenStyle.NoPen)





    p.setBrush(QColor("#001018"))

    p.drawPolygon(pts([(7, 25), (16, 18), (24, 18), (29, 12),

                       (42, 12), (48, 18), (56, 18), (60, 25),

                       (58, 49), (48, 56), (16, 56), (6, 49)]))





    p.setBrush(QColor("#FF8FD6"))

    p.drawPolygon(pts([(9, 27), (17, 20), (25, 20), (30, 14),

                       (41, 14), (47, 20), (54, 20), (57, 27),

                       (55, 47), (47, 53), (17, 53), (9, 47)]))





    p.setBrush(QColor("#FFE6F7"))

    p.drawPolygon(pts([(12, 28), (18, 22), (52, 22), (55, 29),

                       (52, 47), (45, 51), (18, 51), (12, 46)]))

    p.setBrush(QColor("#FFF4FC"))

    p.drawPolygon(pts([(12, 28), (18, 22), (31, 22), (27, 35), (12, 46)]))

    p.setBrush(QColor("#F4B8FF"))

    p.drawPolygon(pts([(31, 22), (52, 22), (55, 29), (43, 36), (27, 35)]))

    p.setBrush(QColor("#B980C7"))

    p.drawPolygon(pts([(12, 46), (27, 35), (32, 51), (18, 51)]))

    p.setBrush(QColor("#D89BE5"))

    p.drawPolygon(pts([(43, 36), (55, 29), (52, 47), (45, 51), (32, 51)]))





    p.setBrush(QColor("#FFD6F1"))

    p.drawPolygon(pts([(25, 20), (30, 14), (41, 14), (47, 20)]))

    p.setBrush(QColor("#E0AAFF"))

    p.drawPolygon(pts([(30, 14), (41, 14), (37, 20), (25, 20)]))





    p.setBrush(QColor("#B5179E"))

    p.drawPolygon(pts([(45, 26), (52, 26), (52, 32), (45, 31)]))

    p.setBrush(QColor("#FFFFFF"))

    p.drawPolygon(pts([(47, 27), (50, 27), (50, 30), (47, 30)]))





    p.setBrush(QColor("#001018"))

    p.drawEllipse(int(22 * size / 64), int(27 * size / 64),

                  int(21 * size / 64), int(21 * size / 64))

    p.setBrush(QColor("#06105A"))

    p.drawEllipse(int(25 * size / 64), int(30 * size / 64),

                  int(15 * size / 64), int(15 * size / 64))

    p.setBrush(QColor("#B5179E"))

    p.drawPolygon(pts([(28, 31), (38, 34), (35, 42), (27, 40)]))

    p.setBrush(QColor("#FF8FD6"))

    p.drawPolygon(pts([(31, 33), (37, 35), (34, 39), (30, 38)]))

    p.setBrush(QColor("#FFFFFF"))

    p.drawPolygon(pts([(33, 32), (37, 34), (34, 35)]))



    p.end()

    return QIcon(px)



class _Sig(QObject):

    capture_done = pyqtSignal(object)





class TinyPicApp:

    def __init__(self, qt_app: QApplication):

        self._qt_app = qt_app

        self._config = Config.load()

        self._hotkeys = HotkeyManager()

        self._region_overlay: Optional[RegionOverlay] = None

        self._preview: Optional[PreviewWindow] = None
        self._settings: Optional[SettingsWindow] = None
        self._region_pending = False

        self._sig = _Sig()

        self._sig.capture_done.connect(self._show_preview)





        self._tray_click_timer = QTimer()

        self._tray_click_timer.setSingleShot(True)

        self._tray_click_timer.setInterval(0)

        self._tray_click_timer.timeout.connect(lambda: self._trigger("region"))



        self._setup_tray()

        self._setup_region_overlay()

        self._register_hotkeys()







    def _setup_tray(self):

        self._tray = QSystemTrayIcon(_make_icon())

        self._tray.setToolTip("TinyPic | click to capture region")



        menu = QMenu()

        menu.setStyleSheet(MAIN_STYLE)



        for label, mode in [

            ("[+] Select region",  "region"),

            ("[ ] Full screen",    "fullscreen"),

            ("[/] Active window",  "window"),

        ]:

            a = menu.addAction(label)

            a.triggered.connect(lambda _, m=mode: self._trigger(m))



        menu.addSeparator()

        menu.addAction("[*] Settings...").triggered.connect(self._open_settings)

        menu.addSeparator()

        menu.addAction("[x] Quit").triggered.connect(self._quit)



        self._tray.setContextMenu(menu)

        self._tray.activated.connect(self._on_tray_activated)

        self._tray.show()



    def _on_tray_activated(self, reason):





        if reason in (QSystemTrayIcon.ActivationReason.Trigger,

                       QSystemTrayIcon.ActivationReason.DoubleClick):

            self._trigger("region")







    def _setup_region_overlay(self):

        self._region_overlay = RegionOverlay()

        self._region_overlay.region_selected.connect(self._on_region)

        self._region_overlay.cancelled.connect(self._on_region_cancelled)







    def _register_hotkeys(self):

        self._hotkeys.unregister_all()

        c = self._config

        if c.hotkey_fullscreen:

            self._hotkeys.register("fullscreen", c.hotkey_fullscreen,

                                   lambda: self._trigger("fullscreen"))

        if c.hotkey_region:

            self._hotkeys.register("region", c.hotkey_region,

                                   lambda: self._trigger("region"))

        if c.hotkey_window:

            self._hotkeys.register("window", c.hotkey_window,

                                   lambda: self._trigger("window"))







    def _trigger(self, mode: str):

        if mode == "region":



            if self._region_pending or self._region_overlay.isVisible():

                return

            self._region_pending = True

            def _start_region():
                self._region_pending = False
                if not self._region_overlay.isVisible():
                    self._region_overlay.start()

            QTimer.singleShot(120, _start_region)

            return



        delay = self._config.delay_seconds



        def _do():

            if delay:

                time.sleep(delay)

            try:

                img = (capture_active_window() if mode == "window"

                       else capture_fullscreen())

                self._sig.capture_done.emit(img)

            except Exception as e:

                print(f"[capture] {e}")



        threading.Thread(target=_do, daemon=True).start()



    def _on_region(self, x: int, y: int, w: int, h: int):
        self._region_pending = False

        delay = self._config.delay_seconds

        def _do_capture():
            try:
                img = capture_region(x, y, w, h)
                if img:
                    self._show_preview(img)
            except Exception as e:
                _log_error("region capture", e)
                self._tray.showMessage(
                    "TinyPic", f"capture error: {e}",
                    QSystemTrayIcon.MessageIcon.Critical, 3000
                )

        QTimer.singleShot(max(1, int(delay * 1000)), _do_capture)

    def _on_region_cancelled(self):
        self._region_pending = False



    def _show_preview(self, image: Image.Image):
        try:
            self._show_preview_inner(image)
        except Exception as e:
            _log_error("show preview", e)
            self._tray.showMessage(
                "TinyPic", f"preview error: {e}",
                QSystemTrayIcon.MessageIcon.Critical, 3000
            )

    def _show_preview_inner(self, image: Image.Image):

        if self._config.show_preview:

            if self._preview and self._preview.isVisible():

                self._preview.close()

            self._preview = PreviewWindow(image, self._config)

            self._preview.show()

            self._preview.raise_()

            self._preview.activateWindow()

        else:

            self._silent_save(image)



    def _silent_save(self, image: Image.Image):

        try:

            self._config.ensure_save_path()

            from datetime import datetime

            from capture import save_image

            now  = datetime.now()

            name = self._config.filename_template

            name = name.replace("{datetime}", now.strftime("%Y-%m-%d_%H-%M-%S"))

            name = name.replace("{date}",     now.strftime("%Y-%m-%d"))

            name = name.replace("{time}",     now.strftime("%H-%M-%S"))

            ext  = "jpg" if self._config.image_format == "JPEG" else self._config.image_format.lower()

            path = str(Path(self._config.save_path) / f"{name}.{ext}")

            save_image(image, path, self._config.image_format)

            self._tray.showMessage("TinyPic", f"saved {Path(path).name}",

                                   QSystemTrayIcon.MessageIcon.NoIcon, 2000)

        except Exception as e:

            self._tray.showMessage("TinyPic", f"error: {e}",

                                   QSystemTrayIcon.MessageIcon.Critical, 3000)

        if self._config.copy_to_clipboard:

            try:

                from capture import image_to_clipboard

                image_to_clipboard(image)

            except Exception:

                pass







    def _open_settings(self):

        if not self._settings:
            self._settings = SettingsWindow(self._config)

            self._settings.settings_saved.connect(self._on_settings_saved)
            self._settings.destroyed.connect(lambda: setattr(self, "_settings", None))
        self._settings.show()
        self._settings.raise_()
        self._settings.activateWindow()



    def _on_settings_saved(self, cfg: Config):

        self._config = cfg

        self._register_hotkeys()







    def _quit(self):

        self._hotkeys.unregister_all()

        QApplication.quit()
