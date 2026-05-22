from typing import Callable

_current_lang = "en"
_listeners: list[Callable[[], None]] = []

LANGUAGES = {
    "en": "English",
    "es": "Español",
}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        # Tray menu
        "tray.select_region": "[+] Select region",
        "tray.full_screen": "[ ] Full screen",
        "tray.active_window": "[/] Active window",
        "tray.settings": "[*] Settings...",
        "tray.quit": "[x] Quit",
        "tray.tooltip": "TinyPic | click to capture region",

        # Tray notifications
        "notify.running.title": "TinyPic running",
        "notify.running.body": "Running in system tray. Right-click icon for options.",
        "notify.saved": "saved {name}",
        "notify.error": "error: {err}",
        "notify.capture_error": "capture error: {err}",
        "notify.preview_error": "preview error: {err}",

        # Settings window
        "settings.title": "TinyPic",
        "settings.subtitle": "Settings · Created by Sykron",
        "settings.appearance": "Appearance",
        "settings.theme": "Theme",
        "settings.effects": "Effects",
        "settings.language": "Language",
        "settings.capture": "Capture",
        "settings.hk_full": "Full screen",
        "settings.hk_region": "Select region",
        "settings.hk_window": "Active window",
        "settings.copy_clip": "Copy to clipboard after capture",
        "settings.show_preview": "Show preview window",
        "settings.include_cursor": "Include mouse cursor in screenshot",
        "settings.delay": "Delay",
        "settings.delay_none": "None",
        "settings.delay_1": "1 sec",
        "settings.delay_2": "2 sec",
        "settings.delay_3": "3 sec",
        "settings.delay_5": "5 sec",
        "settings.save": "Save",
        "settings.folder": "Folder",
        "settings.folder_placeholder": "pick a folder...",
        "settings.browse_tip": "Browse",
        "settings.format": "Format",
        "settings.filename": "Filename",
        "settings.filename_placeholder": "screenshot_{datetime}",
        "settings.filename_tip": "Tokens: {datetime}  {date}  {time}",
        "settings.advanced": "Advanced",
        "settings.start_with_windows": "Start with Windows",
        "settings.cancel": "Cancel",
        "settings.save_btn": "Save",
        "settings.select_folder": "Select save folder",
        "settings.hotkey_unset": "(unset)",
        "settings.hotkey_recording": "press a combo...   esc to cancel",

        # Preview window
        "preview.title": "Preview",
        "preview.copy": "Copy",
        "preview.copy_tip": "Copy to clipboard | Ctrl+C",
        "preview.save": "Save",
        "preview.save_tip": "Save to default folder | Ctrl+S",
        "preview.save_as": "Save as...",
        "preview.discard": "Discard",
        "preview.save_dialog": "Save screenshot",
        "preview.copied": "copied!",
        "preview.auto_copied": "auto-copied",
        "preview.saved": "saved {name}",
    },
    "es": {
        # Tray menu
        "tray.select_region": "[+] Seleccionar región",
        "tray.full_screen": "[ ] Pantalla completa",
        "tray.active_window": "[/] Ventana activa",
        "tray.settings": "[*] Ajustes...",
        "tray.quit": "[x] Salir",
        "tray.tooltip": "TinyPic | clic para capturar región",

        # Tray notifications
        "notify.running.title": "TinyPic en ejecución",
        "notify.running.body": "Corriendo en la bandeja del sistema. Clic derecho en el icono para opciones.",
        "notify.saved": "guardado {name}",
        "notify.error": "error: {err}",
        "notify.capture_error": "error de captura: {err}",
        "notify.preview_error": "error de vista previa: {err}",

        # Settings window
        "settings.title": "TinyPic",
        "settings.subtitle": "Ajustes · Creado por Sykron",
        "settings.appearance": "Apariencia",
        "settings.theme": "Tema",
        "settings.effects": "Efectos",
        "settings.language": "Idioma",
        "settings.capture": "Captura",
        "settings.hk_full": "Pantalla completa",
        "settings.hk_region": "Seleccionar región",
        "settings.hk_window": "Ventana activa",
        "settings.copy_clip": "Copiar al portapapeles tras capturar",
        "settings.show_preview": "Mostrar ventana de vista previa",
        "settings.include_cursor": "Incluir cursor del ratón en la captura",
        "settings.delay": "Retraso",
        "settings.delay_none": "Ninguno",
        "settings.delay_1": "1 seg",
        "settings.delay_2": "2 seg",
        "settings.delay_3": "3 seg",
        "settings.delay_5": "5 seg",
        "settings.save": "Guardar",
        "settings.folder": "Carpeta",
        "settings.folder_placeholder": "elige una carpeta...",
        "settings.browse_tip": "Examinar",
        "settings.format": "Formato",
        "settings.filename": "Nombre de archivo",
        "settings.filename_placeholder": "captura_{datetime}",
        "settings.filename_tip": "Tokens: {datetime}  {date}  {time}",
        "settings.advanced": "Avanzado",
        "settings.start_with_windows": "Iniciar con Windows",
        "settings.cancel": "Cancelar",
        "settings.save_btn": "Guardar",
        "settings.select_folder": "Selecciona carpeta de guardado",
        "settings.hotkey_unset": "(sin asignar)",
        "settings.hotkey_recording": "pulsa una combinación...   esc para cancelar",

        # Preview window
        "preview.title": "Vista previa",
        "preview.copy": "Copiar",
        "preview.copy_tip": "Copiar al portapapeles | Ctrl+C",
        "preview.save": "Guardar",
        "preview.save_tip": "Guardar en carpeta por defecto | Ctrl+S",
        "preview.save_as": "Guardar como...",
        "preview.discard": "Descartar",
        "preview.save_dialog": "Guardar captura",
        "preview.copied": "¡copiado!",
        "preview.auto_copied": "auto-copiado",
        "preview.saved": "guardado {name}",
    },
}


def set_language(lang: str) -> None:
    global _current_lang
    if lang not in TRANSLATIONS:
        lang = "en"
    if lang == _current_lang:
        return
    _current_lang = lang
    for cb in list(_listeners):
        try:
            cb()
        except Exception:
            pass


def current_language() -> str:
    return _current_lang


def t(key: str, **kwargs) -> str:
    table = TRANSLATIONS.get(_current_lang) or TRANSLATIONS["en"]
    s = table.get(key) or TRANSLATIONS["en"].get(key) or key
    if kwargs:
        try:
            return s.format(**kwargs)
        except Exception:
            return s
    return s


def on_change(cb: Callable[[], None]) -> None:
    if cb not in _listeners:
        _listeners.append(cb)
