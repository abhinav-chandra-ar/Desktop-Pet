from __future__ import annotations
import ctypes
import ctypes.wintypes
import time

from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QPainter, QPixmap, QImage, QAction
from PySide6.QtWidgets import QWidget, QApplication, QMenu

from animation import AnimationController
from movement import MovementController, STATE_TO_ANIM
from settings import Settings, SettingsDialog
import startup

# ── Win32 constants ───────────────────────────────────────────────────────────
GWL_EXSTYLE      = -20
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_NOACTIVATE = 0x08000000
WM_NCHITTEST     = 0x0084
HTTRANSPARENT    = -1
HTCLIENT         = 1

_user32 = ctypes.windll.user32

# Set argtypes so ctypes handles HWND/BOOL correctly
_user32.GetWindowLongW.argtypes  = [ctypes.wintypes.HWND, ctypes.c_int]
_user32.GetWindowLongW.restype   = ctypes.c_long
_user32.SetWindowLongW.argtypes  = [ctypes.wintypes.HWND, ctypes.c_int, ctypes.c_long]
_user32.SetWindowLongW.restype   = ctypes.c_long
_user32.GetWindowRect.argtypes   = [ctypes.wintypes.HWND, ctypes.POINTER(ctypes.wintypes.RECT)]
_user32.GetWindowRect.restype    = ctypes.wintypes.BOOL


def _hwnd(widget: QWidget) -> int:
    return int(widget.winId())


def _apply_extended_styles(hwnd: int):
    style = _user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    _user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE)


class LionWindow(QWidget):
    FRAME_MS = 16   # ~60 fps

    def __init__(self, settings: Settings):
        super().__init__(None)
        self._settings = settings
        self._paused = False
        self._last_frame_time = time.monotonic()
        self._pet_size = settings.pet_size

        self._anim = AnimationController(fps=settings.animation_fps)
        self._move = MovementController(
            walk_speed=settings.walk_speed,
            inactivity_sleep=15.0,
        )

        self._current_pixmap: QPixmap | None = None

        self._build_window()
        self._setup_timer()

    # ── Window setup ──────────────────────────────────────────────────────────

    def _build_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setWindowTitle("PixelLion")

        # Set geometry BEFORE show() so Qt does NOT apply its default centering
        self.setGeometry(self._move.x, 0, self._pet_size, self._pet_size)
        self.show()

        # Apply additional Win32 styles after the HWND exists
        _apply_extended_styles(_hwnd(self))

    # ── Timer / game loop ─────────────────────────────────────────────────────

    def _setup_timer(self):
        self._timer = QTimer(self)
        self._timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._timer.timeout.connect(self._tick)
        self._timer.start(self.FRAME_MS)

    def _tick(self):
        now = time.monotonic()
        delta = now - self._last_frame_time
        self._last_frame_time = now

        if self._paused:
            return

        self._move.update(delta)

        anim_name = STATE_TO_ANIM.get(self._move.state, "idle")
        self._anim.set_state(anim_name)

        # Qt tracks position correctly when we use move()
        new_x = self._move.x
        if self.x() != new_x:
            self.move(new_x, 0)

        self.update()

    # ── Painting ──────────────────────────────────────────────────────────────

    def paintEvent(self, event):
        raw: QPixmap = self._anim.tick()
        size = self._pet_size
        if raw.width() != size or raw.height() != size:
            raw = raw.scaled(
                size, size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )
        self._current_pixmap = raw

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        painter.drawPixmap(0, 0, raw)
        painter.end()

    # ── Click-through via WM_NCHITTEST ────────────────────────────────────────

    def nativeEvent(self, event_type: bytes, message) -> tuple:
        if event_type == b"windows_generic_MSG":
            msg = ctypes.cast(
                int(message),
                ctypes.POINTER(ctypes.wintypes.MSG)
            ).contents
            if msg.message == WM_NCHITTEST:
                lp = msg.lParam
                sx = ctypes.c_int16(lp & 0xFFFF).value
                sy = ctypes.c_int16((lp >> 16) & 0xFFFF).value
                rect = ctypes.wintypes.RECT()
                _user32.GetWindowRect(_hwnd(self), ctypes.byref(rect))
                lx = sx - rect.left
                ly = sy - rect.top
                if self._is_opaque(lx, ly):
                    return True, HTCLIENT
                return True, HTTRANSPARENT
        return super().nativeEvent(event_type, message)

    def _is_opaque(self, lx: int, ly: int) -> bool:
        if self._current_pixmap is None:
            return False
        size = self._pet_size
        if lx < 0 or ly < 0 or lx >= size or ly >= size:
            return False
        img = self._current_pixmap.toImage().convertToFormat(
            QImage.Format.Format_ARGB32
        )
        alpha = (img.pixel(lx, ly) >> 24) & 0xFF
        return alpha > 30

    # ── Mouse events ──────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._move.trigger_happy()
            self._anim.set_state("happy")
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._move.trigger_roar()
            self._anim.set_state("roar")

    # ── Context menu ──────────────────────────────────────────────────────────

    def _show_context_menu(self, pos: QPoint):
        menu = QMenu()
        menu.setWindowFlags(menu.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        pause_action = QAction("Pause", self)
        pause_action.setCheckable(True)
        pause_action.setChecked(self._paused)
        pause_action.toggled.connect(self._toggle_pause)
        menu.addAction(pause_action)

        menu.addSeparator()

        settings_action = QAction("Settings…", self)
        settings_action.triggered.connect(self._open_settings)
        menu.addAction(settings_action)

        menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.quit)
        menu.addAction(exit_action)

        menu.exec(pos)

    def _toggle_pause(self, checked: bool):
        self._paused = checked
        if checked:
            self._move.pause()
        else:
            self._move.resume()

    def _open_settings(self):
        dlg = SettingsDialog(self._settings, parent=None)
        dlg.settings_changed.connect(self._apply_settings)
        dlg.exec()

    def _apply_settings(self, s: Settings):
        self._anim.set_fps(s.animation_fps)
        self._move.walk_speed = s.walk_speed
        self._pet_size = s.pet_size
        self.resize(s.pet_size, s.pet_size)
        startup.sync_startup(s.start_with_windows)

    # ── Cleanup ───────────────────────────────────────────────────────────────

    def closeEvent(self, event):
        self._timer.stop()
        event.accept()
