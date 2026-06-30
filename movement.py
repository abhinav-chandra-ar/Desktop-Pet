from __future__ import annotations
import random
import time
from enum import Enum, auto
from dataclasses import dataclass, field

from PySide6.QtWidgets import QApplication


class LionState(Enum):
    IDLE       = auto()
    WALK_LEFT  = auto()
    WALK_RIGHT = auto()
    SIT        = auto()
    SLEEP      = auto()
    WAKING     = auto()
    BLINKING   = auto()
    HAPPY      = auto()
    ROARING    = auto()
    JUMPING    = auto()


# How long (seconds) the lion stays in each state before reconsidering
STATE_DURATION = {
    LionState.IDLE:       (1.0,  4.0),
    LionState.WALK_LEFT:  (2.0,  6.0),
    LionState.WALK_RIGHT: (2.0,  6.0),
    LionState.SIT:        (3.0,  8.0),
    LionState.SLEEP:      (8.0, 20.0),
    LionState.WAKING:     (1.5,  1.5),
    LionState.BLINKING:   (0.4,  0.4),
    LionState.HAPPY:      (1.5,  1.5),
    LionState.ROARING:    (1.2,  1.2),
    LionState.JUMPING:    (0.8,  0.8),
}

# Probability weights for autonomous transitions from IDLE
IDLE_TRANSITIONS = {
    LionState.WALK_LEFT:  30,
    LionState.WALK_RIGHT: 30,
    LionState.SIT:        20,
    LionState.BLINKING:   10,
    LionState.JUMPING:     5,
    LionState.IDLE:        5,
}

PIXELS_PER_SECOND = 60   # walking speed (pixels / sec)
PET_SIZE = 48
INACTIVITY_SLEEP = 15.0  # seconds of no user-triggered action before lion sleeps


@dataclass
class MovementController:
    walk_speed: float = PIXELS_PER_SECOND
    inactivity_sleep: float = INACTIVITY_SLEEP

    _state: LionState = field(default=LionState.IDLE, init=False)
    _x: float = field(default=0.0, init=False)
    _state_until: float = field(default=0.0, init=False)
    _last_user_action: float = field(default_factory=time.monotonic, init=False)
    _screen_width: int = field(default=1920, init=False)

    def __post_init__(self):
        self._screen_width = self._get_screen_width()
        self._x = random.randint(0, max(0, self._screen_width - PET_SIZE))
        self._schedule_next(LionState.IDLE)

    # ── public API ────────────────────────────────────────────────────────────

    @property
    def x(self) -> int:
        return int(self._x)

    @property
    def state(self) -> LionState:
        return self._state

    def trigger_happy(self):
        self._last_user_action = time.monotonic()
        self._transition(LionState.HAPPY)

    def trigger_roar(self):
        self._last_user_action = time.monotonic()
        self._transition(LionState.ROARING)

    def pause(self):
        self._transition(LionState.IDLE)
        # extend stay so autonomous ticks don't immediately move
        self._state_until = time.monotonic() + 9999.0

    def resume(self):
        self._state_until = time.monotonic()

    def update(self, delta: float):
        now = time.monotonic()

        # check inactivity → sleep
        if (self._state not in (LionState.SLEEP, LionState.WAKING) and
                now - self._last_user_action > self.inactivity_sleep):
            if self._state != LionState.SLEEP:
                self._transition(LionState.SLEEP)

        # state-machine tick
        if now >= self._state_until:
            self._advance_state()

        # position update
        if self._state == LionState.WALK_LEFT:
            self._x -= self.walk_speed * delta
        elif self._state == LionState.WALK_RIGHT:
            self._x += self.walk_speed * delta

        # clamp to screen
        self._x = max(0.0, min(self._x, self._screen_width - PET_SIZE))

        # bounce off edges
        if self._x <= 0 and self._state == LionState.WALK_LEFT:
            self._transition(LionState.WALK_RIGHT)
        elif self._x >= self._screen_width - PET_SIZE and self._state == LionState.WALK_RIGHT:
            self._transition(LionState.WALK_LEFT)

    # ── state machine ─────────────────────────────────────────────────────────

    def _advance_state(self):
        s = self._state
        if s == LionState.SLEEP:
            # wake up
            self._transition(LionState.WAKING)
            self._last_user_action = time.monotonic()
        elif s == LionState.WAKING:
            self._transition(LionState.IDLE)
        elif s in (LionState.HAPPY, LionState.ROARING, LionState.JUMPING,
                   LionState.BLINKING):
            self._transition(LionState.IDLE)
        else:
            # weighted random autonomous choice
            choices = list(IDLE_TRANSITIONS.keys())
            weights = list(IDLE_TRANSITIONS.values())
            # avoid same direction twice if already walking
            if s in (LionState.WALK_LEFT, LionState.WALK_RIGHT):
                # prefer stopping or turning
                next_s = random.choices(
                    [LionState.IDLE, LionState.SIT,
                     LionState.WALK_LEFT, LionState.WALK_RIGHT],
                    weights=[30, 20, 25, 25]
                )[0]
            else:
                next_s = random.choices(choices, weights=weights)[0]
            self._transition(next_s)

    def _transition(self, new_state: LionState):
        self._state = new_state
        self._schedule_next(new_state)

    def _schedule_next(self, state: LionState):
        lo, hi = STATE_DURATION.get(state, (2.0, 4.0))
        self._state_until = time.monotonic() + random.uniform(lo, hi)

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _get_screen_width() -> int:
        app = QApplication.instance()
        if app:
            screen = app.primaryScreen()
            if screen:
                return screen.geometry().width()
        return 1920


# Map LionState → animation name string
STATE_TO_ANIM = {
    LionState.IDLE:       "idle",
    LionState.WALK_LEFT:  "walk_left",
    LionState.WALK_RIGHT: "walk_right",
    LionState.SIT:        "sit",
    LionState.SLEEP:      "sleep",
    LionState.WAKING:     "wake",
    LionState.BLINKING:   "blink",
    LionState.HAPPY:      "happy",
    LionState.ROARING:    "roar",
    LionState.JUMPING:    "jump",
}
