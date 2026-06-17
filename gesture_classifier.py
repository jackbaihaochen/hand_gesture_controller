from enum import Enum, auto
import config

# tip_idx, pip_idx for index/middle/ring/pinky (thumb excluded)
_FINGER_PAIRS = [(8, 6), (12, 10), (16, 14), (20, 18)]
_WRIST = 0


class GestureState(Enum):
    DISENGAGED = auto()
    ENGAGED = auto()


def _dist(a, b):
    return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5


def count_extended_fingers(landmarks) -> int:
    wrist = landmarks[_WRIST]
    count = 0
    for tip_idx, pip_idx in _FINGER_PAIRS:
        if _dist(landmarks[tip_idx], wrist) > _dist(landmarks[pip_idx], wrist):
            count += 1
    return count


class GestureClassifier:
    def __init__(self):
        self._state = GestureState.DISENGAGED
        self._candidate = None
        self._candidate_count = 0

    @property
    def state(self):
        return self._state

    def update(self, landmarks) -> GestureState:
        n = 0 if landmarks is None else count_extended_fingers(landmarks)

        if n >= config.OPEN_PALM_MIN_FINGERS:
            candidate = GestureState.ENGAGED
        elif n <= config.FIST_MAX_FINGERS:
            candidate = GestureState.DISENGAGED
        else:
            # Dead zone — hold current state, reset debounce
            self._candidate = None
            self._candidate_count = 0
            return self._state

        if candidate == self._candidate:
            self._candidate_count += 1
        else:
            self._candidate = candidate
            self._candidate_count = 1

        if self._candidate_count >= config.DEBOUNCE_FRAMES:
            self._commit(candidate)

        return self._state

    def _commit(self, new_state: GestureState):
        self._state = new_state
        self._candidate = None
        self._candidate_count = 0
