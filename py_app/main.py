import sys

import os



if getattr(sys, "frozen", False):

    sys.path.insert(0, os.path.dirname(sys.executable))

else:

    sys.path.insert(0, os.path.dirname(__file__))



from PyQt6.QtWidgets import QApplication, QMessageBox

from PyQt6.QtCore import Qt

from PyQt6.QtGui import QPalette, QColor



from styles import MAIN_STYLE





def _apply_light_theme(app: QApplication):



    app.setStyle("Fusion")

    app.setStyleSheet(MAIN_STYLE)



    C   = QColor

    pal = QPalette()

    pal.setColor(QPalette.ColorRole.Window,          C("#FFF4FC"))

    pal.setColor(QPalette.ColorRole.WindowText,      C("#3B124A"))

    pal.setColor(QPalette.ColorRole.Base,            C("#FFFFFF"))

    pal.setColor(QPalette.ColorRole.AlternateBase,   C("#FFE6F7"))

    pal.setColor(QPalette.ColorRole.ToolTipBase,     C("#FFF4FC"))

    pal.setColor(QPalette.ColorRole.ToolTipText,     C("#3B124A"))

    pal.setColor(QPalette.ColorRole.Text,            C("#3B124A"))

    pal.setColor(QPalette.ColorRole.Button,          C("#FF8FD6"))

    pal.setColor(QPalette.ColorRole.ButtonText,      C("#3B124A"))

    pal.setColor(QPalette.ColorRole.BrightText,      C("#FFFFFF"))

    pal.setColor(QPalette.ColorRole.Highlight,       C("#D86DFF"))

    pal.setColor(QPalette.ColorRole.HighlightedText, C("#FFFFFF"))

    pal.setColor(QPalette.ColorRole.Link,            C("#B5179E"))

    pal.setColor(QPalette.ColorRole.PlaceholderText, C("#A873B7"))





    pal.setColor(QPalette.ColorGroup.Disabled,

                 QPalette.ColorRole.WindowText, C("#808080"))

    pal.setColor(QPalette.ColorGroup.Disabled,

                 QPalette.ColorRole.Text,       C("#808080"))

    pal.setColor(QPalette.ColorGroup.Disabled,

                 QPalette.ColorRole.ButtonText, C("#808080"))



    app.setPalette(pal)





def main():

    QApplication.setHighDpiScaleFactorRoundingPolicy(

        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough

    )



    app = QApplication(sys.argv)

    app.setApplicationName("TinyPic")

    app.setApplicationVersion("1.0.0")

    app.setQuitOnLastWindowClosed(False)





    try:

        import ctypes

        ctypes.windll.kernel32.CreateMutexW(None, False, "TinyPicMutex_v1")

        if ctypes.windll.kernel32.GetLastError() == 183:

            QMessageBox.information(

                None, "TinyPic",



            )

            sys.exit(0)

    except Exception:

        pass



    _apply_light_theme(app)



    from app import TinyPicApp

    _instance = TinyPicApp(app)

    sys.exit(app.exec())





if __name__ == "__main__":

    main()
