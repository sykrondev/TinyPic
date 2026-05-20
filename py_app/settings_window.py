from pathlib import Path

from typing import Optional



from PyQt6.QtWidgets import (

    QVBoxLayout, QHBoxLayout, QGridLayout,

    QLabel, QPushButton, QLineEdit, QCheckBox, QComboBox,

    QGroupBox, QFileDialog, QWidget, QScrollArea,

)

from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from PyQt6.QtGui import QKeyEvent



from config import Config, is_startup_enabled, set_startup_enabled

from styles import MAIN_STYLE

from frameless import FramelessWindow, soft_shadow









class HotkeyButton(QPushButton):

    hotkey_changed = pyqtSignal(str)



    def __init__(self, current: str = "", parent=None):

        super().__init__(parent)

        self.setObjectName("btn_hotkey")

        self._hotkey   = current

        self._recording = False

        self._recorded: set = set()

        self._update_text()



    @property

    def hotkey(self) -> str:

        return self._hotkey



    def mouseReleaseEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self._start()

        super().mouseReleaseEvent(event)



    def _start(self):

        self._recording = True

        self._recorded.clear()

        self.setProperty("recording", "true")

        self._refresh_style()

        self.setText("press a combo...   esc to cancel")

        self.setFocus()



    def _stop(self, apply: bool = True):

        self._recording = False

        self.setProperty("recording", "false")

        self._refresh_style()

        if apply and self._recorded:

            self._hotkey = self._build()

            self.hotkey_changed.emit(self._hotkey)

        self._update_text()



    def _refresh_style(self):

        self.style().unpolish(self)

        self.style().polish(self)



    def _build(self) -> str:

        mods, key = [], ""

        for k in sorted(self._recorded):

            kl = k.lower()

            if kl in ("ctrl", "control"): mods.append("ctrl")

            elif kl == "alt":             mods.append("alt")

            elif kl == "shift":           mods.append("shift")

            elif kl == "win":             mods.append("win")

            else:                         key = k

        return "+".join(mods + ([key] if key else []))



    def _update_text(self):

        self.setText(self._hotkey if self._hotkey else "(unset)")



    def keyPressEvent(self, event: QKeyEvent):

        if not self._recording:

            return super().keyPressEvent(event)

        if event.key() == Qt.Key.Key_Escape:

            return self._stop(apply=False)

        mods = event.modifiers()

        if mods & Qt.KeyboardModifier.ControlModifier: self._recorded.add("ctrl")

        if mods & Qt.KeyboardModifier.AltModifier:     self._recorded.add("alt")

        if mods & Qt.KeyboardModifier.ShiftModifier:   self._recorded.add("shift")

        if mods & Qt.KeyboardModifier.MetaModifier:    self._recorded.add("win")

        name = self._qt_key_name(event.key())

        if name and name.lower() not in ("ctrl", "alt", "shift", "win"):

            self._recorded.add(name)

            QTimer.singleShot(60, lambda: self._stop(apply=True))



    @staticmethod

    def _qt_key_name(key: int) -> Optional[str]:

        m = {

            Qt.Key.Key_Print: "print screen",

            Qt.Key.Key_F1: "f1",  Qt.Key.Key_F2: "f2",  Qt.Key.Key_F3: "f3",

            Qt.Key.Key_F4: "f4",  Qt.Key.Key_F5: "f5",  Qt.Key.Key_F6: "f6",

            Qt.Key.Key_F7: "f7",  Qt.Key.Key_F8: "f8",  Qt.Key.Key_F9: "f9",

            Qt.Key.Key_F10: "f10", Qt.Key.Key_F11: "f11", Qt.Key.Key_F12: "f12",

            Qt.Key.Key_Tab: "tab", Qt.Key.Key_Space: "space",

            Qt.Key.Key_Return: "enter", Qt.Key.Key_Enter: "enter",

            Qt.Key.Key_Backspace: "backspace", Qt.Key.Key_Delete: "delete",

            Qt.Key.Key_Insert: "insert", Qt.Key.Key_Home: "home",

            Qt.Key.Key_End: "end", Qt.Key.Key_PageUp: "page up",

            Qt.Key.Key_PageDown: "page down",

            Qt.Key.Key_Left: "left",  Qt.Key.Key_Right: "right",

            Qt.Key.Key_Up: "up",      Qt.Key.Key_Down: "down",

        }

        if key in m: return m[key]

        if Qt.Key.Key_A <= key <= Qt.Key.Key_Z: return chr(key).lower()

        if Qt.Key.Key_0 <= key <= Qt.Key.Key_9: return chr(key)

        return None









class SettingsWindow(FramelessWindow):

    settings_saved = pyqtSignal(Config)



    def __init__(self, config: Config, parent=None):

        super().__init__("TinyPic", "settings", parent)

        self._config = config

        self.setStyleSheet(MAIN_STYLE)

        self.setMinimumWidth(540)

        self.setMaximumWidth(640)

        self.setMinimumHeight(560)

        self.setModal(True)

        self._build()

        self._load_values()







    def _build(self):

        root = self.content_layout()

        root.setSpacing(14)





        hk_box = QGroupBox("SHORTCUTS")

        hk_grid = QGridLayout(hk_box)

        hk_grid.setColumnStretch(1, 1)

        hk_grid.setSpacing(12)

        hk_grid.setContentsMargins(14, 18, 14, 14)



        self._hk_full   = self._hk_row(hk_grid, 0, "Full screen")

        self._hk_region = self._hk_row(hk_grid, 1, "Select region")

        self._hk_window = self._hk_row(hk_grid, 2, "Active window")



        root.addWidget(hk_box)





        out_box = QGroupBox("OUTPUT")

        out_grid = QGridLayout(out_box)

        out_grid.setColumnStretch(1, 1)

        out_grid.setSpacing(12)

        out_grid.setContentsMargins(14, 18, 14, 14)



        out_grid.addWidget(self._field_label("Save to"), 0, 0)

        path_row = QWidget()

        path_row.setStyleSheet("background: transparent;")

        pr = QHBoxLayout(path_row)

        pr.setContentsMargins(0, 0, 0, 0)

        pr.setSpacing(6)

        self._inp_path = QLineEdit()

        self._inp_path.setPlaceholderText("pick a folder...")

        browse = QPushButton("...")

        browse.setObjectName("btn_round")

        browse.setFixedWidth(38)

        browse.setToolTip("Browse")

        browse.clicked.connect(self._browse)

        pr.addWidget(self._inp_path)

        pr.addWidget(browse)

        out_grid.addWidget(path_row, 0, 1)



        out_grid.addWidget(self._field_label("Format"), 1, 0)

        self._cmb_fmt = QComboBox()

        self._cmb_fmt.addItems(["PNG", "JPEG", "BMP", "TIFF"])

        self._cmb_fmt.setFixedWidth(130)

        out_grid.addWidget(self._cmb_fmt, 1, 1)



        out_grid.addWidget(self._field_label("Filename"), 2, 0)

        self._inp_fname = QLineEdit()

        self._inp_fname.setPlaceholderText("screenshot_{datetime}")

        out_grid.addWidget(self._inp_fname, 2, 1)



        hint = QLabel("tokens:  {datetime}   {date}   {time}")

        hint.setObjectName("lbl_hint")

        out_grid.addWidget(hint, 3, 1)



        root.addWidget(out_box)





        beh_box = QGroupBox("BEHAVIOR")

        beh_lay = QVBoxLayout(beh_box)

        beh_lay.setContentsMargins(14, 18, 14, 14)

        beh_lay.setSpacing(12)



        self._chk_clip    = QCheckBox("Copy to clipboard after capture")

        self._chk_preview = QCheckBox("Show preview window")

        self._chk_cursor  = QCheckBox("Include mouse cursor")

        self._chk_startup = QCheckBox("Start with Windows")



        for chk in (self._chk_clip, self._chk_preview,

                    self._chk_cursor, self._chk_startup):

            beh_lay.addWidget(chk)



        delay_row = QHBoxLayout()

        delay_row.setSpacing(12)

        delay_row.addWidget(self._field_label("Delay"))

        self._cmb_delay = QComboBox()

        self._cmb_delay.addItems(["None", "1 sec", "2 sec", "3 sec", "5 sec"])

        self._cmb_delay.setFixedWidth(110)

        delay_row.addWidget(self._cmb_delay)

        delay_row.addStretch()

        beh_lay.addLayout(delay_row)



        root.addWidget(beh_box)

        root.addStretch()





        btn_row = QHBoxLayout()

        btn_row.setSpacing(10)

        btn_row.addStretch()



        cancel_btn = QPushButton("Cancel")

        cancel_btn.setObjectName("btn_secondary")

        cancel_btn.clicked.connect(self.reject)



        save_btn = QPushButton("Save")

        save_btn.clicked.connect(self._save)

        soft_shadow(save_btn, "#FF8FD6", blur=18, alpha=95, y=2)



        btn_row.addWidget(cancel_btn)

        btn_row.addWidget(save_btn)

        root.addLayout(btn_row)







    @staticmethod

    def _field_label(text: str) -> QLabel:

        lbl = QLabel(text)

        lbl.setObjectName("lbl_field")

        return lbl



    def _hk_row(self, layout: QGridLayout, row: int, label: str) -> HotkeyButton:

        layout.addWidget(self._field_label(label), row, 0)

        btn = HotkeyButton()

        layout.addWidget(btn, row, 1)

        return btn



    def _load_values(self):

        c = self._config

        self._hk_full._hotkey   = c.hotkey_fullscreen; self._hk_full._update_text()

        self._hk_region._hotkey = c.hotkey_region;     self._hk_region._update_text()

        self._hk_window._hotkey = c.hotkey_window;     self._hk_window._update_text()



        self._inp_path.setText(c.save_path)

        idx = self._cmb_fmt.findText(c.image_format)

        self._cmb_fmt.setCurrentIndex(max(0, idx))

        self._inp_fname.setText(c.filename_template)



        self._chk_clip.setChecked(c.copy_to_clipboard)

        self._chk_preview.setChecked(c.show_preview)

        self._chk_cursor.setChecked(c.include_cursor)

        self._chk_startup.setChecked(is_startup_enabled())



        dm = {0: 0, 1: 1, 2: 2, 3: 3, 5: 4}

        self._cmb_delay.setCurrentIndex(dm.get(c.delay_seconds, 0))



    def _browse(self):

        cur = self._inp_path.text() or str(Path.home())

        d = QFileDialog.getExistingDirectory(self, "Select save folder", cur)

        if d:

            self._inp_path.setText(d)



    def _save(self):

        c = self._config

        c.hotkey_fullscreen = self._hk_full.hotkey

        c.hotkey_region     = self._hk_region.hotkey

        c.hotkey_window     = self._hk_window.hotkey



        c.save_path        = self._inp_path.text().strip() or str(Path.home() / "Pictures" / "Screenshots")

        c.image_format     = self._cmb_fmt.currentText()

        c.filename_template = self._inp_fname.text().strip() or "screenshot_{datetime}"



        c.copy_to_clipboard = self._chk_clip.isChecked()

        c.show_preview      = self._chk_preview.isChecked()

        c.include_cursor    = self._chk_cursor.isChecked()

        startup_requested = self._chk_startup.isChecked()



        dv = [0, 1, 2, 3, 5]

        c.delay_seconds = dv[self._cmb_delay.currentIndex()]



        startup_ok = set_startup_enabled(startup_requested)

        c.start_with_windows = startup_requested if startup_ok else is_startup_enabled()

        c.save()

        self.settings_saved.emit(c)

        self.accept()
