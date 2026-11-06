"""Window capture and reversible opacity/focus changes, without game injection."""
import ctypes as C
from ctypes import wintypes as W
import queue
import threading
import time
import numpy as np
from focus import WinApi, find_game


class WindowUnavailable(RuntimeError):
    pass


class CaptureRetry(WindowUnavailable):
    """Temporary capture failure; keep inputs paused until a fresh frame arrives."""
    pass


class NativeWindow(WinApi):
    def __init__(self):
        super().__init__()
        self.g = C.windll.gdi32
        signatures = {
            'GetForegroundWindow': ([], W.HWND),
            'GetDC': ([W.HWND], W.HDC),
            'ReleaseDC': ([W.HWND, W.HDC], C.c_int),
            'PrintWindow': ([W.HWND, W.HDC, W.UINT], W.BOOL),
            'GetWindowLongW': ([W.HWND, C.c_int], W.LONG),
            'SetWindowLongW': ([W.HWND, C.c_int, W.LONG], W.LONG),
            'SetLayeredWindowAttributes': ([W.HWND, W.DWORD, W.BYTE, W.DWORD], W.BOOL),
            'GetLayeredWindowAttributes': ([W.HWND, C.POINTER(W.DWORD), C.POINTER(W.BYTE), C.POINTER(W.DWORD)], W.BOOL),
            'GetClientRect': ([W.HWND, C.POINTER(W.RECT)], W.BOOL),
            'ClientToScreen': ([W.HWND, C.POINTER(W.POINT)], W.BOOL),
            'IsWindow': ([W.HWND], W.BOOL),
            'IsIconic': ([W.HWND], W.BOOL),
            'SetForegroundWindow': ([W.HWND], W.BOOL),
            'GetWindowThreadProcessId': ([W.HWND, C.POINTER(W.DWORD)], W.DWORD),
        }
        for name, (args, result) in signatures.items():
            fn = getattr(self.u, name)
            fn.argtypes, fn.restype = args, result
        for name, args, result in (
            ('CreateCompatibleDC', [W.HDC], W.HDC),
            ('CreateCompatibleBitmap', [W.HDC, C.c_int, C.c_int], W.HBITMAP),
            ('SelectObject', [W.HDC, W.HANDLE], W.HANDLE),
            ('DeleteObject', [W.HANDLE], W.BOOL),
            ('DeleteDC', [W.HDC], W.BOOL),
            ('GetDIBits', [W.HDC, W.HBITMAP, W.UINT, W.UINT, C.c_void_p, C.c_void_p, W.UINT], C.c_int),
        ):
            fn = getattr(self.g, name)
            fn.argtypes, fn.restype = args, result

    def valid(self, h):
        return bool(h and self.u.IsWindow(h) and not self.is_minimized(h))

    def geometry(self, h):
        rect, origin = W.RECT(), W.POINT()
        if not self.valid(h) or not self.u.GetClientRect(h, C.byref(rect)) or not self.u.ClientToScreen(h, C.byref(origin)):
            raise WindowUnavailable('Game window unavailable / janela do jogo indisponível')
        return origin.x, origin.y, rect.right, rect.bottom

    def appearance(self, h):
        style = self.u.GetWindowLongW(h, -20)
        color, alpha, flags = W.DWORD(), W.BYTE(), W.DWORD()
        layered = None
        if style & 0x80000:
            if not self.u.GetLayeredWindowAttributes(h, C.byref(color), C.byref(alpha), C.byref(flags)):
                raise WindowUnavailable('Cannot preserve window transparency')
            layered = color.value, alpha.value, flags.value
        return style, layered

    def restore(self, h, appearance):
        if not self.u.IsWindow(h):
            return
        style, layered = appearance
        self.u.SetLayeredWindowAttributes(h, 0, 255, 2)
        self.u.SetWindowLongW(h, -20, style)
        if layered:
            self.u.SetLayeredWindowAttributes(h, *layered)

    def ghost(self, h, appearance, interactive=False):
        # Keep window styles stable throughout the session. Alpha zero makes
        # the idle window click-through; alpha one accepts our brief click.
        style = (appearance[0] | 0x80000) & ~0x20
        if self.u.GetWindowLongW(h, -20) != style:
            self.u.SetWindowLongW(h, -20, style)
        if not self.u.SetLayeredWindowAttributes(h, 0, 1 if interactive else 0, 2):
            raise WindowUnavailable('Ghost unavailable / Ghost indisponível')

    def cursor(self):
        point = W.POINT()
        self.u.GetCursorPos(C.byref(point))
        return point.x, point.y

    def move_cursor(self, point):
        self.u.SetCursorPos(*point)

    def capture(self, h):
        x, y, width, height = self.geometry(h)
        if not (0 < width <= 16384 and 0 < height <= 16384):
            raise CaptureRetry('capture_size')
        dc = self.u.GetDC(h)
        mem = self.g.CreateCompatibleDC(dc)
        bitmap = self.g.CreateCompatibleBitmap(dc, width, height)
        old = self.g.SelectObject(mem, bitmap)
        try:
            if not (dc and mem and bitmap) or not self.u.PrintWindow(h, mem, 3):
                raise CaptureRetry('capture_failed')
            self.g.SelectObject(mem, old)
            class Header(C.Structure):
                _fields_ = [('size', W.DWORD), ('width', W.LONG), ('height', W.LONG),
                            ('planes', W.WORD), ('bits', W.WORD), ('compression', W.DWORD),
                            ('image_size', W.DWORD), ('xppm', W.LONG), ('yppm', W.LONG),
                            ('used', W.DWORD), ('important', W.DWORD)]
            header = Header(C.sizeof(Header), width, -height, 1, 32, 0, 0, 0, 0, 0, 0)
            pixels = np.empty((height, width, 4), dtype=np.uint8)
            if self.g.GetDIBits(mem, bitmap, 0, height, pixels.ctypes.data, C.byref(header), 0) != height:
                raise CaptureRetry('capture_failed')
            frame = np.ascontiguousarray(pixels[:, :, :3])
            if frame.std() < 1:
                raise CaptureRetry('capture_blank')
            return frame, x, y
        finally:
            self.g.SelectObject(mem, old)
            self.g.DeleteObject(bitmap)
            self.g.DeleteDC(mem)
            self.u.ReleaseDC(h, dc)


class GameSession:
    def __init__(self, settings, stop, api=None):
        self.s, self.stop = settings, stop
        self.api = api or NativeWindow()
        self.lock = threading.RLock()
        self.h = None
        self.original = None
        self.hidden = False
        self.peek_until = 0
        self.peek_previous = None
        self.last_geometry = None
        self.capture_ready = False
        self.capture_job = None
        self.discard_pending = False
        self.capture_timeout = 4.0

    def _window(self):
        if self.h is not None:
            if not self.api.valid(self.h):
                raise WindowUnavailable('Game closed or minimized / jogo fechado ou minimizado')
        else:
            self.h = find_game(self.api)
            if not self.api.valid(self.h):
                raise WindowUnavailable('Open Fortnite first / abra o Fortnite primeiro')
        return self.h

    def _appearance(self):
        peeking = self.s.background_enabled and self.s.ghost_enabled and time.monotonic() < self.peek_until
        hide = self.s.background_enabled and self.s.ghost_enabled and not peeking
        if hide and not self.hidden:
            self.original = self.api.appearance(self.h)
            self.hidden = True  # restore even if setting opacity fails halfway
            self.api.ghost(self.h, self.original)
        elif not hide and self.hidden:
            self.api.restore(self.h, self.original)
            self.hidden = False
        if peeking and self.peek_previous is None:
            self.peek_previous = self.api.foreground()
            self.api.focus(self.h)
        elif not peeking:
            self._restore_peek_focus()

    def _restore_peek_focus(self):
        if self.peek_previous is not None:
            if self.peek_previous and self.api.foreground() == self.h:
                self.api.focus(self.peek_previous)
            self.peek_previous = None

    def peek(self):
        self.peek_until = time.monotonic() + 5

    def has_focus(self):
        return self.h is not None and self.api.foreground() == self.h

    def capture(self, screen_capture):
        with self.lock:
            self.capture_ready = False
            self._window()
            self._appearance()
            self.last_geometry = self.api.geometry(self.h)
            if not self.s.background_enabled:
                if self.api.foreground() != self.h:
                    self.api.focus(self.h)
                    if self.stop.wait(0.35):
                        raise WindowUnavailable('capture_cancelled')
                if self.api.foreground() != self.h:
                    raise CaptureRetry('capture_focus')
                x, y, width, height = self.api.geometry(self.h)
                self.last_geometry = (x, y, width, height)
                value = screen_capture(self.s.monitor_index, region={
                    'left': x, 'top': y, 'width': width, 'height': height})
                if self.api.foreground() != self.h or self.api.geometry(self.h) != self.last_geometry:
                    raise CaptureRetry('capture_moved')
                self.capture_ready = True
                return value
            if self.capture_job is not None and self.discard_pending and not self.capture_job.empty():
                self.capture_job = None  # Never use an image from a timed-out attempt.
                self.discard_pending = False
            if self.capture_job is None:
                result = self.capture_job = queue.Queue(maxsize=1)
                target = self.h
                def capture():
                    try:
                        result.put(self.api.capture(target))
                    except Exception as error:
                        result.put(error)
                threading.Thread(target=capture, daemon=True).start()
            result = self.capture_job
            # A hung GPU/window must not keep the game hidden indefinitely.
            deadline = time.monotonic() + self.capture_timeout
            while True:
                if self.stop.is_set():
                    raise WindowUnavailable('capture_cancelled')
                if time.monotonic() >= deadline:
                    self.discard_pending = True
                    raise CaptureRetry('capture_timeout')
                try:
                    value = result.get(timeout=0.1)
                    break
                except queue.Empty:
                    continue
            self.capture_job = None
            if self.discard_pending:
                self.discard_pending = False
                raise CaptureRetry('capture_stale')
            if isinstance(value, Exception):
                raise CaptureRetry(str(value))
            if self.api.geometry(self.h) != self.last_geometry:
                raise CaptureRetry('capture_moved')
            self.capture_ready = True
            return value

    def perform(self, action, point=None):
        with self.lock:
            if self.stop.is_set() or not self.capture_ready:
                return False
            h = self._window()
            geometry = self.api.geometry(h)
            if point:
                x, y, w, height = geometry
                if geometry != self.last_geometry or not (x <= point[0] < x+w and y <= point[1] < y+height):
                    return False
            previous, cursor = self.api.foreground(), self.api.cursor()
            try:
                if self.hidden and point is not None:
                    self.api.ghost(h, self.original, interactive=True)
                if previous != h:
                    self.api.focus(h)
                    if self.stop.wait(0.35):
                        return False
                if self.api.foreground() != h:
                    return False
                if point is not None and self.api.geometry(h) != geometry:
                    self.capture_ready = False
                    return False
                action()
                if point is not None:
                    # Let the game consume mouse-up before restoring another app.
                    self.stop.wait(0.3)
                return True
            finally:
                try:
                    if self.hidden and point is not None:
                        self.api.ghost(h, self.original)
                finally:
                    if self.s.background_enabled:
                        if point is not None:
                            self.api.move_cursor(cursor)
                        if previous and previous != h and self.api.foreground() == h:
                            self.api.focus(previous)

    def close(self):
        with self.lock:
            try:
                if self.hidden:
                    self.api.restore(self.h, self.original)
                    self.hidden = False
            finally:
                self._restore_peek_focus()
