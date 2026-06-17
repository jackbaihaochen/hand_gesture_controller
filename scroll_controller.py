import math
from gesture_classifier import GestureClassifier, GestureState
import config

_TRACKING_LANDMARK = 9  # MIDDLE_FINGER_MCP


class _OneEuroFilter:
    def __init__(self, freq):
        self._freq = freq
        self._x_prev = None
        self._dx_prev = 0.0

    def reset(self):
        self._x_prev = None
        self._dx_prev = 0.0

    def _alpha(self, cutoff):
        tau = 1.0 / (2 * math.pi * cutoff)
        te = 1.0 / self._freq
        return 1.0 / (1.0 + tau / te)

    def __call__(self, x):
        if self._x_prev is None:
            self._x_prev = x
            return x
        dx = (x - self._x_prev) * self._freq
        edx = self._dx_prev + self._alpha(config.ONE_EURO_D_CUTOFF) * (dx - self._dx_prev)
        cutoff = config.ONE_EURO_MIN_CUTOFF + config.ONE_EURO_BETA * abs(edx)
        result = self._x_prev + self._alpha(cutoff) * (x - self._x_prev)
        self._x_prev = result
        self._dx_prev = edx
        return result


class ScrollController:
    def __init__(self, fps: float):
        self._classifier = GestureClassifier()
        self._filter = _OneEuroFilter(freq=fps)
        self._prev_y = None
        self._prev_state = GestureState.DISENGAGED

    @property
    def gesture_state(self) -> GestureState:
        return self._classifier.state

    def update(self, landmarks) -> int:
        state = self._classifier.update(landmarks)
        just_engaged = (
            state == GestureState.ENGAGED
            and self._prev_state == GestureState.DISENGAGED
        )
        self._prev_state = state

        if state == GestureState.DISENGAGED:
            self._prev_y = None
            self._filter.reset()
            return 0

        if landmarks is None:
            # Engaged but detection dropped for this frame — skip without resetting prev_y
            return 0

        current_y = landmarks[_TRACKING_LANDMARK].y

        if just_engaged or self._prev_y is None:
            # Seed prev_y to avoid jump-scroll on re-engagement
            self._prev_y = current_y
            self._filter.reset()
            return 0

        delta_normalized = current_y - self._prev_y
        self._prev_y = current_y

        raw_pixels = delta_normalized * config.SCROLL_GAIN * config.FRAME_HEIGHT
        smoothed = self._filter(raw_pixels)
        return int(smoothed)
