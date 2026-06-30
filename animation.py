
from __future__ import annotations
from pathlib import Path
from typing import Dict, Optional
import time

from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt

SPRITE_DIR = Path(__file__).parent / "assets" / "sprites"
FRAME_SIZE = 48   # each frame is 48×48 inside the sheet (16×16 source scaled 3×)


class Animation:

    def __init__(self, name: str, fps: float = 12.0):
        self.name = name
        self.fps = fps
        self.frames: list[QPixmap] = []
        self.current_frame = 0
        self._last_tick = time.monotonic()
        self._load()

    def _load(self):
        path = SPRITE_DIR / f"{self.name}.png"
        if not path.exists():
            self.frames = [self._placeholder()]
            return
        sheet = QImage(str(path))
        if sheet.isNull():
            self.frames = [self._placeholder()]
            return
        n_frames = sheet.width() // FRAME_SIZE
        for i in range(n_frames):
            crop = sheet.copy(i * FRAME_SIZE, 0, FRAME_SIZE, FRAME_SIZE)
            self.frames.append(QPixmap.fromImage(crop))

    def _placeholder(self) -> QPixmap:
        pm = QPixmap(FRAME_SIZE, FRAME_SIZE)
        pm.fill(Qt.GlobalColor.transparent)
        return pm

    def tick(self) -> QPixmap:
        now = time.monotonic()
        elapsed = now - self._last_tick
        frame_duration = 1.0 / max(self.fps, 1.0)
        if elapsed >= frame_duration:
            steps = int(elapsed / frame_duration)
            self.current_frame = (self.current_frame + steps) % len(self.frames)
            self._last_tick = now
        return self.frames[self.current_frame]

    def reset(self):
        self.current_frame = 0
        self._last_tick = time.monotonic()

    @property
    def finished(self) -> bool:
        return self.current_frame == len(self.frames) - 1

    def set_fps(self, fps: float):
        self.fps = max(1.0, fps)


class AnimationController:
    
    ONE_SHOT = {"wake", "blink", "happy", "roar", "jump"}

    def __init__(self, fps: float = 12.0):
        self._fps = fps
        self._cache: Dict[str, Animation] = {}
        self._state = "idle"
        self._queued: Optional[str] = None   # next state after one-shot finishes
        self._load_all()

    def _load_all(self):
        names = [
            "idle", "idle_flip",
            "walk_right", "walk_left",
            "sit", "sleep", "wake",
            "blink", "happy", "roar", "jump",
        ]
        for n in names:
            self._cache[n] = Animation(n, self._fps)

    def set_state(self, state: str, queue_after: str = "idle"):
        if state not in self._cache:
            return
        if self._state == state:
            return
        self._state = state
        self._cache[state].reset()
        self._queued = queue_after if state in self.ONE_SHOT else None

    def tick(self) -> QPixmap:
        anim = self._cache[self._state]
        pixmap = anim.tick()
        if self._queued and anim.finished:
            self.set_state(self._queued)
            self._queued = None
        return pixmap

    @property
    def state(self) -> str:
        return self._state

    def set_fps(self, fps: float):
        self._fps = fps
        for a in self._cache.values():
            a.set_fps(fps)
