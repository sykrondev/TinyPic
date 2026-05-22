import sys
import os
import faulthandler
import traceback
from pathlib import Path

if getattr(sys, "frozen", False):
    sys.path.insert(0, os.path.dirname(sys.executable))
else:
    sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from config import Config
from theme_apply import load_fonts, apply_theme

_CRASH_LOG_FILE = None


def _crash_log_path() -> Path:
    appdata = Path(os.environ.get("APPDATA", Path.home())).expanduser()
    path = appdata / "TinyPic" / "crash.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _install_crash_logging():
    global _CRASH_LOG_FILE
    log = open(_crash_log_path(), "a", encoding="utf-8")
    _CRASH_LOG_FILE = log
    faulthandler.enable(log)

    def _excepthook(exc_type, exc, tb):
        log.write("\n[unhandled exception]\n")
        traceback.print_exception(exc_type, exc, tb, file=log)
        log.flush()
        sys.__excepthook__(exc_type, exc, tb)

    sys.excepthook = _excepthook


def _mlog(msg: str):
    try:
        import os, datetime
        from pathlib import Path
        path = Path(os.environ.get("APPDATA", Path.home())) / "TinyPic" / "startup.log"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now().strftime('%H:%M:%S.%f')}] {msg}\n")
    except Exception:
        pass


def main():
    _mlog("main() start")
    _install_crash_logging()

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    _mlog("QApplication creating")
    app = QApplication(sys.argv)
    app.setApplicationName("TinyPic")
    app.setApplicationVersion("1.0.0")
    app.setQuitOnLastWindowClosed(False)
    _mlog("QApplication created")

    try:
        import ctypes
        ctypes.windll.kernel32.CreateMutexW(None, False, "TinyPicMutex_v1")
        if ctypes.windll.kernel32.GetLastError() == 183:
            _mlog("mutex: already running, exiting")
            QMessageBox.information(None, "TinyPic", "TinyPic is already running.")
            sys.exit(0)
        _mlog("mutex: acquired OK")
    except Exception as e:
        _mlog(f"mutex: exception {e}")

    load_fonts()
    config = Config.load()
    import i18n
    i18n.set_language(config.language or "en")
    apply_theme(app, config.theme_id or "pinkcore", config.ui_effects)
    _mlog("theme applied")

    from app import TinyPicApp
    _mlog("creating TinyPicApp")
    _instance = TinyPicApp(app)
    _mlog("TinyPicApp created, entering event loop")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
