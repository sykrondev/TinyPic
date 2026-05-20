import threading

from typing import Callable, Dict, Optional

from PyQt6.QtCore import QObject, pyqtSignal





class _HotkeySignaler(QObject):

    triggered = pyqtSignal(str)





class HotkeyManager:








    def __init__(self):

        self._signaler = _HotkeySignaler()

        self._hooks: Dict[str, object] = {}

        self._lock = threading.Lock()



    @property

    def on_trigger(self) -> pyqtSignal:

        return self._signaler.triggered



    def register(self, name: str, hotkey: str, callback: Callable):



        import keyboard



        with self._lock:

            self._unregister_locked(name)

            if not hotkey or hotkey.strip() == "":

                return





        self._signaler.triggered.connect(

            lambda n, cb=callback, nm=name: cb() if n == nm else None

        )



        def _fire():

            self._signaler.triggered.emit(name)



        try:

            hook = keyboard.add_hotkey(hotkey.lower(), _fire, suppress=False)

            with self._lock:

                self._hooks[name] = hook

        except Exception as e:

            print(f"[hotkeys] Could not register '{hotkey}': {e}")



    def unregister(self, name: str):

        with self._lock:

            self._unregister_locked(name)



    def _unregister_locked(self, name: str):

        import keyboard

        if name in self._hooks:

            try:

                keyboard.remove_hotkey(self._hooks[name])

            except Exception:

                pass

            del self._hooks[name]



    def unregister_all(self):

        import keyboard

        with self._lock:

            for hook in self._hooks.values():

                try:

                    keyboard.remove_hotkey(hook)

                except Exception:

                    pass

            self._hooks.clear()
