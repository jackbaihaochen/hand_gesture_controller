# Hand Gesture Controller

A macOS webcam-based hand gesture controller. Show an open palm to scroll — move your hand up/down to scroll any window without touching the trackpad.

## How it works

1. Webcam frames are processed by [MediaPipe HandLandmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker) to get 21 hand landmarks per frame.
2. A gesture classifier watches finger extension count to decide state: open palm (≥4 fingers extended) → **ENGAGED**, fist (≤1 finger) → **DISENGAGED**, anything in between is a dead zone that holds the current state.
3. While ENGAGED, the vertical movement of landmark #9 (middle finger MCP) is tracked frame-to-frame, smoothed via a One-Euro filter, and converted to a scroll delta.
4. The delta is posted to macOS as a native `CGScrollWheelEvent` via the Quartz framework — works in any app.

## Requirements

- macOS (Quartz dependency)
- Python 3.10+
- A webcam

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Accessibility permission** — the Quartz event tap requires it. Go to:

> System Settings → Privacy & Security → Accessibility

Add your terminal app (Terminal, iTerm2, etc.) and enable it.

The MediaPipe model (`hand_landmarker.task`) is downloaded automatically on first run.

## Usage

```bash
source .venv/bin/activate
python main.py
```

A camera window opens with a debug overlay:

| Overlay element | Meaning |
|---|---|
| `SCROLLING` (green) | Open palm detected, scrolling active |
| `idle` (grey) | Fist or no hand detected |
| `delta: +Npx` | Scroll delta being emitted this frame |
| Green dots + white lines | 21 hand landmarks |

Press **Q** in the camera window to quit.

## File structure

```
main.py               # Entry point: camera loop, debug overlay
hand_tracker.py       # MediaPipe HandLandmarker wrapper (VIDEO mode)
gesture_classifier.py # State machine: ENGAGED / DISENGAGED with debounce
scroll_controller.py  # Frame-delta → scroll pixels + One-Euro smoothing filter
quartz_emitter.py     # Posts CGScrollWheelEvent to macOS via pyobjc
config.py             # All tunable parameters
```

## Configuration (`config.py`)

| Parameter | Default | Effect |
|---|---|---|
| `CAMERA_INDEX` | `0` | Which camera to use |
| `FRAME_WIDTH/HEIGHT` | `640×480` | Capture resolution |
| `OPEN_PALM_MIN_FINGERS` | `4` | Fingers extended to engage scrolling |
| `FIST_MAX_FINGERS` | `1` | Fingers extended to disengage |
| `DEBOUNCE_FRAMES` | `3` | Frames a gesture must hold before committing |
| `SCROLL_GAIN` | `2.5` | Scroll speed multiplier |
| `INVERT_SCROLL` | `False` | Flip scroll direction |
| `ONE_EURO_MIN_CUTOFF` | `1.0` | One-Euro filter: low-speed smoothing |
| `ONE_EURO_BETA` | `0.007` | One-Euro filter: high-speed lag reduction |

## Development progress

- [x] Hand tracking via MediaPipe HandLandmarker (VIDEO mode, single hand)
- [x] Gesture classifier: open-palm / fist detection with debounce dead zone
- [x] Frame-delta scroll controller — tracks middle finger MCP (landmark #9)
- [x] One-Euro filter for jitter-free, responsive scrolling
- [x] macOS native scroll event emitter via Quartz CGEvent API
- [x] Auto model download on first run
- [x] Accessibility permission check with actionable error message
- [x] Measured FPS for accurate filter calibration
- [x] Debug overlay: state label, scroll delta, landmark skeleton

## TODO

- [x] Add `opencv-contrib-python` to `requirements.txt`
- [ ] **More gestures**: pinch (zoom), two-finger swipe (back/forward), point (cursor move)
- [ ] **Mouse cursor control**: map hand position to screen coordinates
- [ ] **Click emulation**: tap gesture → left/right click via CGEvent
- [ ] **Media / shortcut gestures**: swipe left/right for next track, thumbs up/down, etc.
- [ ] **Multi-hand support**: second hand for independent gesture layer
- [ ] **Background mode**: run as a menu-bar app (no camera window)
- [ ] **Hotkey toggle**: pause/resume without quitting
- [ ] **Cross-platform**: replace Quartz emitter with `pynput` for Windows/Linux support
- [ ] **Smarter classifier**: replace finger-count heuristic with a trained gesture model for richer vocabulary
