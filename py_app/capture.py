import time

from typing import Optional, Tuple

from PIL import Image

from PyQt6.QtGui import QPixmap, QImage

import mss

import mss.tools





def capture_fullscreen(monitor_index: int = 1) -> Image.Image:



    with mss.mss() as sct:

        monitors = sct.monitors

        if monitor_index >= len(monitors):

            monitor_index = 1

        mon = monitors[monitor_index]

        shot = sct.grab(mon)

        return _shot_to_pil(shot)





def capture_all_monitors() -> Image.Image:



    with mss.mss() as sct:

        mon = sct.monitors[0]

        shot = sct.grab(mon)

        return _shot_to_pil(shot)





def qpixmap_to_pil(pix: QPixmap) -> Optional[Image.Image]:
    if pix.isNull() or pix.width() <= 0 or pix.height() <= 0:
        return None
    qimg = pix.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
    w, h = qimg.width(), qimg.height()
    stride = qimg.bytesPerLine()
    buf = qimg.bits()
    buf.setsize(stride * h)
    return Image.frombytes("RGBA", (w, h), bytes(buf), "raw", "RGBA").convert("RGB")


def capture_region(x: int, y: int, width: int, height: int) -> Optional[Image.Image]:



    if width <= 0 or height <= 0:

        return None

    with mss.mss() as sct:

        region = {"top": y, "left": x, "width": width, "height": height}

        shot = sct.grab(region)

        return _shot_to_pil(shot)





def capture_active_window() -> Image.Image:



    try:

        import ctypes

        import ctypes.wintypes



        hwnd = ctypes.windll.user32.GetForegroundWindow()

        rect = ctypes.wintypes.RECT()

        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))



        x = rect.left

        y = rect.top

        w = rect.right - rect.left

        h = rect.bottom - rect.top



        if w > 0 and h > 0:

            return capture_region(x, y, w, h)

    except Exception:

        pass

    return capture_fullscreen()





def _shot_to_pil(shot) -> Image.Image:



    return Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")





def save_image(image: Image.Image, path: str, fmt: str = "PNG", quality: int = 95):



    save_kwargs = {}

    if fmt.upper() == "JPEG":

        save_kwargs["quality"] = quality

        save_kwargs["optimize"] = True

    elif fmt.upper() == "PNG":

        save_kwargs["optimize"] = True



    image.save(path, format=fmt, **save_kwargs)





def image_to_clipboard(image: Image.Image):



    import io

    import win32clipboard

    import win32con



    output = io.BytesIO()

    image.convert("RGB").save(output, format="BMP")

    bmp_data = output.getvalue()[14:]



    win32clipboard.OpenClipboard()

    try:

        win32clipboard.EmptyClipboard()

        win32clipboard.SetClipboardData(win32con.CF_DIB, bmp_data)

    finally:

        win32clipboard.CloseClipboard()
