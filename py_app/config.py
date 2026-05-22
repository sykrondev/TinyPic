import json

import os

import sys

from pathlib import Path

from dataclasses import dataclass, asdict





APP_NAME = "TinyPic"

STARTUP_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"





def _user_config_dir() -> Path:

    appdata = Path(os.environ.get("APPDATA", Path.home())).expanduser()

    return appdata / APP_NAME





def _legacy_config_paths() -> list[Path]:

    if getattr(sys, "frozen", False):

        app_dir = Path(sys.executable).parent

    else:

        app_dir = Path(__file__).parent.parent

    return [app_dir / "tinypic.json"]





def _get_config_path() -> Path:

    config_dir = _user_config_dir()

    config_dir.mkdir(parents=True, exist_ok=True)

    config_path = config_dir / "config.json"



    if not config_path.exists():

        for legacy_path in _legacy_config_paths():

            if legacy_path.exists():

                try:

                    config_path.write_text(

                        legacy_path.read_text(encoding="utf-8"),

                        encoding="utf-8",

                    )

                    break

                except OSError:

                    pass



    return config_path





CONFIG_PATH = _get_config_path()

DEFAULT_SAVE_PATH = str(Path.home() / "Pictures" / "Screenshots")





def _startup_command() -> str:

    if getattr(sys, "frozen", False):

        return f'"{sys.executable}"'



    exe = Path(sys.executable)

    pythonw = exe.with_name("pythonw.exe")

    runner = pythonw if pythonw.exists() else exe

    script = Path(__file__).with_name("main.py")

    return f'"{runner}" "{script}"'





def is_startup_enabled() -> bool:

    if os.name != "nt":

        return False

    try:

        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_RUN_KEY) as key:

            value, _ = winreg.QueryValueEx(key, APP_NAME)

        return value == _startup_command()

    except FileNotFoundError:

        return False

    except OSError:

        return False





def set_startup_enabled(enabled: bool) -> bool:

    if os.name != "nt":

        return False

    try:

        import winreg

        with winreg.OpenKey(

            winreg.HKEY_CURRENT_USER, STARTUP_RUN_KEY, 0, winreg.KEY_SET_VALUE

        ) as key:

            if enabled:

                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, _startup_command())

            else:

                try:

                    winreg.DeleteValue(key, APP_NAME)

                except FileNotFoundError:

                    pass

        return True

    except OSError:

        return False





@dataclass

class Config:

    save_path: str = DEFAULT_SAVE_PATH

    image_format: str = "PNG"

    filename_template: str = "screenshot_{datetime}"

    copy_to_clipboard: bool = True

    show_preview: bool = True

    include_cursor: bool = False

    start_with_windows: bool = False

    delay_seconds: int = 0



    hotkey_fullscreen: str = "ctrl+print screen"

    hotkey_region: str = "alt+print screen"

    hotkey_window: str = "shift+print screen"

    theme_id: str = "pinkcore"

    ui_effects: str = "calm"

    window_x: int = -1

    window_y: int = -1

    settings_width: int = 0

    settings_height: int = 0

    settings_x: int = -1

    settings_y: int = -1

    preview_width: int = 0

    preview_height: int = 0

    preview_x: int = -1

    preview_y: int = -1

    def __post_init__(self):
        if self.settings_x < 0 and self.window_x >= 0:
            self.settings_x = self.window_x
            self.settings_y = self.window_y

    def save(self):

        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:

            json.dump(asdict(self), f, indent=2)



    @classmethod

    def load(cls) -> "Config":

        if not CONFIG_PATH.exists():

            return cls()

        try:

            with open(CONFIG_PATH, "r", encoding="utf-8") as f:

                data = json.load(f)

            valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}

            return cls(**valid)

        except Exception:

            return cls()



    def ensure_save_path(self):

        Path(self.save_path).mkdir(parents=True, exist_ok=True)
