from pathlib import Path
from typing import Callable, Optional

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QCheckBox, QComboBox,
    QGroupBox, QFileDialog, QWidget, QScrollArea, QApplication,
    QFrame,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QKeyEvent

from config import Config, is_startup_enabled, set_startup_enabled

from theme import THEMES
from theme_apply import apply_theme
from styles import build_stylesheet
import theme
import ui_effects

from frameless import FramelessWindow
from widgets.marquee_label import MarqueeLabel
from widgets.glow_button import GlowButton









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



    def __init__(
        self,
        config: Config,
        parent=None,
        on_theme_changed: Optional[Callable[..., None]] = None,
    ):

        super().__init__(
            "TinyPic",
            "Settings · Created by Sykron",
            parent,
            glitch_title=(config.theme_id == "webcore"),
            geometry_slot="settings",
            config=config,
        )

        self._config = config
        self._on_theme_changed = on_theme_changed
        self._marquees: list[MarqueeLabel] = []

        ui_effects.set_level(config.ui_effects)
        self.setStyleSheet(build_stylesheet(theme.active))

        self.setMinimumWidth(540)
        self.setMinimumHeight(540)
        self.setMaximumSize(1200, 900)

        self.setModal(False)

        self._build()

        self._load_values()

        self._cmb_theme.currentIndexChanged.connect(self._on_theme_combo)
        self._cmb_effects.currentIndexChanged.connect(self._on_effects_combo)

        if config.settings_width <= 0 or config.settings_height <= 0:
            self.resize(680, 720)
        self.restore_geometry()
        if config.settings_x < 0 or config.settings_y < 0:
            screen = self.screen()
            if screen:
                ag = screen.availableGeometry()
                self.move(
                    ag.x() + (ag.width() - self.width()) // 2,
                    ag.y() + (ag.height() - self.height()) // 2,
                )







    def _build(self):
        outer = self.content_layout()
        outer.setSpacing(6)
        outer.setContentsMargins(8, 4, 8, 6)

        self._marquees = []
        if ui_effects.active().marquee_enabled:
            top_m = MarqueeLabel(parent=self._content)
            self._marquees.append(top_m)
            outer.addWidget(top_m)

        reading = QWidget()
        reading.setObjectName("settings_reading_panel")
        reading_lay = QVBoxLayout(reading)
        reading_lay.setContentsMargins(0, 0, 0, 0)
        reading_lay.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        body = QWidget()
        body.setObjectName("settings_body")
        root = QVBoxLayout(body)
        root.setSpacing(12)
        root.setContentsMargins(6, 6, 6, 6)

        app_box = QGroupBox("Appearance")
        app_grid = QGridLayout(app_box)
        app_grid.setColumnStretch(1, 1)
        app_grid.setSpacing(10)
        app_grid.setContentsMargins(14, 20, 14, 12)
        app_grid.addWidget(self._field_label("Theme"), 0, 0)
        self._cmb_theme = QComboBox()
        for tok in THEMES.values():
            self._cmb_theme.addItem(tok.label, tok.id)
        app_grid.addWidget(self._cmb_theme, 0, 1)
        app_grid.addWidget(self._field_label("Effects"), 1, 0)
        self._cmb_effects = QComboBox()
        for eid, elabel in ui_effects.level_labels():
            self._cmb_effects.addItem(elabel, eid)
        app_grid.addWidget(self._cmb_effects, 1, 1)
        root.addWidget(app_box)

        cap_box = QGroupBox("Capture")
        cap_lay = QVBoxLayout(cap_box)
        cap_lay.setContentsMargins(14, 20, 14, 12)
        cap_lay.setSpacing(10)

        hk_grid = QGridLayout()
        hk_grid.setColumnStretch(1, 1)
        hk_grid.setSpacing(10)
        self._hk_full = self._hk_row(hk_grid, 0, "Full screen")
        self._hk_region = self._hk_row(hk_grid, 1, "Select region")
        self._hk_window = self._hk_row(hk_grid, 2, "Active window")
        cap_lay.addLayout(hk_grid)

        self._chk_clip = QCheckBox("Copy to clipboard after capture")
        self._chk_preview = QCheckBox("Show preview window")
        self._chk_cursor = QCheckBox("Include mouse cursor in screenshot")
        for chk in (self._chk_clip, self._chk_preview, self._chk_cursor):
            cap_lay.addWidget(chk)

        delay_row = QHBoxLayout()
        delay_row.setSpacing(10)
        delay_row.addWidget(self._field_label("Delay"))
        self._cmb_delay = QComboBox()
        self._cmb_delay.addItems(["None", "1 sec", "2 sec", "3 sec", "5 sec"])
        self._cmb_delay.setFixedWidth(110)
        delay_row.addWidget(self._cmb_delay)
        delay_row.addStretch()
        cap_lay.addLayout(delay_row)
        root.addWidget(cap_box)

        save_box = QGroupBox("Save")
        out_grid = QGridLayout(save_box)
        out_grid.setColumnStretch(1, 1)
        out_grid.setSpacing(10)
        out_grid.setContentsMargins(14, 20, 14, 12)

        out_grid.addWidget(self._field_label("Folder"), 0, 0)
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
        self._inp_fname.setToolTip("Tokens: {datetime}  {date}  {time}")
        out_grid.addWidget(self._inp_fname, 2, 1)
        root.addWidget(save_box)

        adv_box = QGroupBox("Advanced")
        adv_lay = QVBoxLayout(adv_box)
        adv_lay.setContentsMargins(14, 20, 14, 12)
        self._chk_startup = QCheckBox("Start with Windows")
        adv_lay.addWidget(self._chk_startup)
        root.addWidget(adv_box)

        root.addStretch()
        scroll.setWidget(body)
        reading_lay.addWidget(scroll, 1)
        outer.addWidget(reading, 1)

        footer = QWidget()
        footer.setObjectName("settings_footer")
        foot_lay = QHBoxLayout(footer)
        foot_lay.setContentsMargins(12, 10, 12, 10)
        foot_lay.setSpacing(10)
        foot_lay.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("btn_secondary")
        cancel_btn.clicked.connect(self.reject)
        save_btn = GlowButton("Save")
        save_btn.clicked.connect(self._save)
        foot_lay.addWidget(cancel_btn)
        foot_lay.addWidget(save_btn)
        outer.addWidget(footer)

    def _on_theme_combo(self, _index: int):
        theme_id = self._cmb_theme.currentData()
        if not theme_id:
            return
        self._config.theme_id = theme_id
        self._apply_live_theme()

    def _on_effects_combo(self, _index: int):
        level = self._cmb_effects.currentData()
        if not level:
            return
        self._config.ui_effects = level
        self._apply_live_theme()

    def _apply_live_theme(self):
        if self._on_theme_changed:
            self._on_theme_changed()
            return
        app = QApplication.instance()
        if app:
            apply_theme(
                app,
                self._config.theme_id or "pinkcore",
                self._config.ui_effects,
            )
        self.refresh_theme()

    def refresh_theme(self):
        super().refresh_theme()
        for m in self._marquees:
            m.refresh_theme()
        for btn in self._content.findChildren(GlowButton):
            btn.refresh_theme()

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

        tid = c.theme_id or "pinkcore"
        idx = self._cmb_theme.findData(tid)
        self._cmb_theme.blockSignals(True)
        self._cmb_theme.setCurrentIndex(max(0, idx))
        self._cmb_theme.blockSignals(False)

        eid = ui_effects.normalize_level(c.ui_effects)
        eidx = self._cmb_effects.findData(eid)
        self._cmb_effects.blockSignals(True)
        self._cmb_effects.setCurrentIndex(max(0, eidx))
        self._cmb_effects.blockSignals(False)



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

        c.theme_id = self._cmb_theme.currentData() or "pinkcore"
        c.ui_effects = self._cmb_effects.currentData() or "calm"

        startup_ok = set_startup_enabled(startup_requested)

        c.start_with_windows = startup_requested if startup_ok else is_startup_enabled()

        c.save()

        self.settings_saved.emit(c)

        self.accept()
