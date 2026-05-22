# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

_spec_dir = os.path.dirname(os.path.abspath(SPEC))
_py_app = os.path.join(_spec_dir, "py_app")
_local_modules = [
    f[:-3] for f in os.listdir(_py_app)
    if f.endswith(".py") and f != "main.py"
]
_widget_modules = [
    "widgets",
    "widgets.marquee_label",
    "widgets.glitch_label",
    "widgets.glow_button",
]

_hiddenimports = [
    "PyQt6.QtCore",
    "PyQt6.QtGui",
    "PyQt6.QtWidgets",
    "PIL._tkinter_finder",
    "win32api",
    "win32con",
    "win32clipboard",
    "win32gui",
    "keyboard",
    "mss",
    "mss.windows",
] + sorted(set(_local_modules + _widget_modules))

a = Analysis(
    ["py_app/main.py"],
    pathex=["py_app"],
    binaries=[],
    datas=[
        ("py_app/assets/fonts", "assets/fonts"),
        ("py_app/assets/cursors", "assets/cursors"),
    ],
    hiddenimports=_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "numpy",
        "scipy",
        "pandas",
        "IPython",
        "jupyter",
        "PyQt6.QtWebEngineWidgets",
        "PyQt6.QtWebEngineCore",
        "PyQt6.Qt3DCore",
        "PyQt6.Qt3DRender",
        "PyQt6.QtDataVisualization",
        "PyQt6.QtCharts",
        "PyQt6.QtMultimedia",
        "PyQt6.QtBluetooth",
        "PyQt6.QtNfc",
        "PyQt6.QtSerialPort",
        "PyQt6.QtSql",
        "PyQt6.QtTest",
        "PyQt6.QtXml",
        "PyQt6.QtOpenGL",
        "PyQt6.QtOpenGLWidgets",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="TinyPic",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="py_app/pink_camera_icon.ico",
    version_info=None,
    uac_admin=False,
    uac_uiaccess=False,
)
