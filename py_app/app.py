import time

import threading
import traceback

from pathlib import Path

from typing import Optional



from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu

from PyQt6.QtCore import Qt, QTimer, QObject, pyqtSignal, QPointF

from PyQt6.QtGui import QIcon



from PIL import Image



from config import Config

from capture import capture_fullscreen, capture_region, capture_active_window

from hotkeys import HotkeyManager

from region_overlay import RegionOverlay

from preview_window import PreviewWindow

from settings_window import SettingsWindow

from styles import build_stylesheet
import theme
from theme_apply import apply_theme
from theme_icons import make_tray_icon


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


def _dbg(msg: str):
    try:
        import os
        path = Path(os.environ.get("APPDATA", Path.home())) / "TinyPic" / "startup.log"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            import datetime
            f.write(f"[{datetime.datetime.now().strftime('%H:%M:%S.%f')}] {msg}\n")
    except Exception:
        pass





class _Sig(QObject):

    capture_done = pyqtSignal(object)
    theme_changed = pyqtSignal()





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



        _dbg("__init__: before _setup_tray")
        try:
            self._setup_tray()
            _dbg("__init__: _setup_tray OK")
        except Exception as e:
            _log_error("setup_tray", e)
            _dbg(f"__init__: _setup_tray FAILED: {e}")

        _dbg("__init__: before _setup_region_overlay")
        self._setup_region_overlay()
        _dbg("__init__: before _register_hotkeys")
        self._register_hotkeys()

        QTimer.singleShot(300, self._open_settings)
        _dbg("__init__: done")







    def _setup_tray(self):
        _dbg(f"_setup_tray: isSystemTrayAvailable={QSystemTrayIcon.isSystemTrayAvailable()}")
        icon = make_tray_icon(theme.active)
        _dbg(f"_setup_tray: icon.isNull={icon.isNull()}")
        if icon.isNull():
            from PyQt6.QtWidgets import QStyle
            icon = self._qt_app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
            _dbg("_setup_tray: using fallback system icon")

        self._tray = QSystemTrayIcon(icon)
        self._tray.setToolTip("TinyPic | click to capture region")



        self._tray_menu = QMenu()

        self._tray_menu.setStyleSheet(build_stylesheet(theme.active))



        for label, mode in [

            ("[+] Select region",  "region"),

            ("[ ] Full screen",    "fullscreen"),

            ("[/] Active window",  "window"),

        ]:

            a = self._tray_menu.addAction(label)

            a.triggered.connect(lambda _, m=mode: self._trigger(m))



        self._tray_menu.addSeparator()

        self._tray_menu.addAction("[*] Settings...").triggered.connect(self._open_settings)

        self._tray_menu.addSeparator()

        self._tray_menu.addAction("[x] Quit").triggered.connect(self._quit)



        self._tray.setContextMenu(self._tray_menu)

        self._tray.activated.connect(self._on_tray_activated)

        self._tray.show()
        _dbg(f"_setup_tray: tray.show() called, isVisible={self._tray.isVisible()}")



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



    def _on_region(self, image):
        self._region_pending = False

        delay = self._config.delay_seconds

        def _do_show():
            try:
                if image:
                    self._show_preview(image)
            except Exception as e:
                _log_error("region capture", e)
                self._tray.showMessage(
                    "TinyPic", f"capture error: {e}",
                    QSystemTrayIcon.MessageIcon.Critical, 3000
                )

        QTimer.singleShot(max(0, int(delay * 1000)), _do_show)

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







    def refresh_theme(self):
        apply_theme(
            self._qt_app,
            self._config.theme_id or "pinkcore",
            self._config.ui_effects,
        )
        self._tray.setIcon(make_tray_icon(theme.active))
        self._tray_menu.setStyleSheet(build_stylesheet(theme.active))
        if self._settings and self._settings.isVisible():
            self._settings.refresh_theme()
        if self._preview and self._preview.isVisible():
            self._preview.refresh_theme()
        if self._region_overlay:
            self._region_overlay.refresh_theme()
        self._sig.theme_changed.emit()

    def _open_settings(self):
        if self._settings:
            self._settings.close()
            self._settings.deleteLater()
            self._settings = None

        self._settings = SettingsWindow(
            self._config,
            on_theme_changed=self.refresh_theme,
        )
        self._settings.settings_saved.connect(self._on_settings_saved)
        self._settings.destroyed.connect(lambda: setattr(self, "_settings", None))
        self._settings.show()
        self._settings.raise_()
        self._settings.activateWindow()



    def _on_settings_saved(self, cfg: Config):

        self._config = cfg

        self.refresh_theme()

        self._register_hotkeys()







    def _quit(self):

        self._hotkeys.unregister_all()

        QApplication.quit()
