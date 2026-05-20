MAIN_STYLE = """
QWidget {
    font-family: 'Segoe UI', 'Tahoma', sans-serif;
    font-size: 12px;
    color: #FFF7FD;
    background-color: transparent;
}
QDialog { background: transparent; }

QPushButton {
    background-color: rgba(255, 143, 214, 0.72);
    color: #FFFFFF;
    border: 1px solid rgba(255, 235, 249, 0.74);
    border-radius: 8px;
    padding: 7px 18px;
    font-size: 12px;
    font-weight: 700;
    min-width: 78px;
}
QPushButton:hover {
    background-color: rgba(255, 179, 230, 0.88);
    border-color: #FFFFFF;
}
QPushButton:pressed {
    background-color: #D86DFF;
    color: #FFFFFF;
    padding-top: 8px;
    padding-left: 19px;
}
QPushButton:disabled {
    background-color: rgba(255, 199, 232, 0.45);
    color: #A873B7;
}

QPushButton#btn_secondary {
    background-color: rgba(255, 244, 252, 0.32);
    color: #FFFFFF;
    border: 1px solid rgba(255, 214, 241, 0.48);
}
QPushButton#btn_secondary:hover {
    background-color: rgba(255, 244, 252, 0.72);
    color: #7C2D92;
}

QPushButton#btn_sky {
    background-color: #C77DFF;
    color: #FFFFFF;
    border-color: #E0AAFF;
}
QPushButton#btn_sky:hover { background-color: #E0AAFF; }

QPushButton#btn_discard {
    background-color: rgba(255, 244, 252, 0.18);
    color: #FFE5F8;
    border: 1px solid transparent;
}
QPushButton#btn_discard:hover {
    background-color: #FFD6E8;
    border-color: #FF8FD6;
}

QPushButton#btn_round {
    background-color: rgba(255, 244, 252, 0.38);
    color: #FFFFFF;
    border: 1px solid rgba(244, 184, 255, 0.55);
    border-radius: 7px;
    padding: 4px 8px;
    min-width: 0;
    font-weight: 800;
}

QPushButton#btn_hotkey {
    background-color: rgba(255, 244, 252, 0.42);
    color: #FFFFFF;
    border: 1px solid rgba(244, 184, 255, 0.55);
    border-radius: 8px;
    padding: 6px 9px;
    font-family: 'Cascadia Mono', 'Consolas', monospace;
    font-size: 12px;
    font-weight: 700;
    text-align: left;
    min-width: 190px;
}
QPushButton#btn_hotkey:hover {
    background-color: #FFFFFF;
    border-color: #FF8FD6;
}
QPushButton#btn_hotkey[recording="true"] {
    background-color: #FFE0F0;
    color: #C1126B;
    border-color: #FF5FAF;
}

QPushButton#btn_close {
    background-color: rgba(255, 255, 255, 0.18);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.42);
    border-radius: 8px;
    font-size: 12px;
    font-weight: 800;
    padding: 0;
}
QPushButton#btn_close:hover {
    background-color: #FF5FAF;
    color: #FFFFFF;
}

QLineEdit {
    background-color: rgba(255, 244, 252, 0.5);
    color: #FFFFFF;
    border: 1px solid rgba(244, 184, 255, 0.55);
    border-radius: 8px;
    padding: 7px 10px;
    font-size: 12px;
    selection-background-color: #D86DFF;
    selection-color: #FFFFFF;
}
QLineEdit:focus {
    background-color: rgba(255, 244, 252, 0.76);
    color: #3B124A;
    border-color: #FF8FD6;
}
QLineEdit:disabled {
    background-color: rgba(255, 244, 252, 0.35);
    color: #A873B7;
}

QComboBox {
    background-color: rgba(255, 244, 252, 0.5);
    color: #FFFFFF;
    border: 1px solid rgba(244, 184, 255, 0.55);
    border-radius: 8px;
    padding: 6px 10px;
    min-width: 100px;
}
QComboBox:hover,
QComboBox:focus {
    background-color: rgba(255, 244, 252, 0.76);
    color: #3B124A;
    border-color: #FF8FD6;
}
QComboBox::drop-down {
    border: none;
    width: 22px;
}
QComboBox::down-arrow {
    image: none;
    width: 0;
    height: 0;
}
QComboBox QAbstractItemView {
    background-color: #FFF4FC;
    color: #3B124A;
    border: 1px solid #F4B8FF;
    border-radius: 8px;
    selection-background-color: #FFB3E6;
    selection-color: #3B124A;
    padding: 4px;
    outline: 0;
}

QCheckBox {
    color: #FFFFFF;
    spacing: 9px;
    font-weight: 600;
}
QCheckBox:hover { color: #FFD6F1; }
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #F4B8FF;
    border-radius: 5px;
    background-color: rgba(255, 244, 252, 0.45);
}
QCheckBox::indicator:checked {
    background-color: #FF8FD6;
    border-color: #FFFFFF;
}

QGroupBox {
    background-color: rgba(255, 236, 250, 0.16);
    color: #FFFFFF;
    border: 1px solid rgba(255, 235, 249, 0.24);
    border-radius: 8px;
    margin-top: 19px;
    padding: 17px 13px 12px 13px;
    font-size: 11px;
    font-weight: 800;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    top: 1px;
    padding: 2px 9px;
    background-color: rgba(181, 23, 158, 0.32);
    color: #FFFFFF;
    border-radius: 6px;
}

QLabel {
    background-color: transparent;
    color: #FFFFFF;
}
QLabel#lbl_field {
    font-size: 12px;
    color: #FFFFFF;
    font-weight: 800;
}
QLabel#lbl_hint {
    font-size: 11px;
    color: #FFE5F8;
}
QLabel#lbl_info {
    font-size: 12px;
    color: #FFFFFF;
    font-weight: 800;
}

QScrollArea {
    border: 1px solid rgba(255, 235, 249, 0.24);
    border-radius: 8px;
    background-color: rgba(255, 236, 250, 0.16);
}
QScrollBar:vertical {
    background: rgba(255, 244, 252, 0.35);
    width: 10px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: #FF8FD6;
    border-radius: 5px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover { background: #D86DFF; }
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical { background: transparent; }

QMenu {
    background-color: #FFF4FC;
    color: #3B124A;
    border: 1px solid #F4B8FF;
    border-radius: 9px;
    padding: 5px;
}
QMenu::item {
    padding: 7px 28px 7px 14px;
    border-radius: 7px;
}
QMenu::item:selected {
    background-color: #FFB3E6;
    color: #3B124A;
}
QMenu::separator {
    height: 1px;
    background: #F4B8FF;
    margin: 5px 4px;
}

QToolTip {
    background-color: #FFF4FC;
    color: #3B124A;
    border: 1px solid #F4B8FF;
    border-radius: 7px;
    padding: 4px 7px;
    font-size: 11px;
}
"""



PREVIEW_STYLE = MAIN_STYLE + """
QLabel#lbl_image {
    background-color: rgba(255, 244, 252, 0.9);
    border: 1px solid #F4B8FF;
    border-radius: 9px;
}
"""
