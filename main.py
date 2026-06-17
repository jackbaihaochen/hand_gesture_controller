import sys
import os
import time
import urllib.request
import cv2

import config
from hand_tracker import HandTracker
from scroll_controller import ScrollController
from gesture_classifier import GestureState
import quartz_emitter

_HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (0, 9), (9, 10), (10, 11), (11, 12),
    (0, 13), (13, 14), (14, 15), (15, 16),
    (0, 17), (17, 18), (18, 19), (19, 20),
    (5, 9), (9, 13), (13, 17),
]


def _download_model():
    if os.path.exists(config.MODEL_PATH):
        return
    print(f"Downloading hand landmarker model to {config.MODEL_PATH} ...")
    urllib.request.urlretrieve(config.MODEL_URL, config.MODEL_PATH)
    print("Download complete.")


def _check_accessibility():
    try:
        from ApplicationServices import AXIsProcessTrusted
        if not AXIsProcessTrusted():
            print(
                "ERROR: Accessibility permission required.\n"
                "Go to System Settings → Privacy & Security → Accessibility\n"
                "and add your terminal app, then rerun."
            )
            sys.exit(1)
    except ImportError:
        pass


def _measure_fps(cap, n_frames=30) -> float:
    t0 = time.time()
    for _ in range(n_frames):
        cap.read()
    elapsed = time.time() - t0
    fps = n_frames / elapsed
    print(f"Measured FPS: {fps:.1f}")
    return fps


def _draw_landmarks(frame, landmarks):
    h, w = frame.shape[:2]
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
    for a, b in _HAND_CONNECTIONS:
        cv2.line(frame, pts[a], pts[b], (255, 255, 255), 1)
    for pt in pts:
        cv2.circle(frame, pt, 4, (0, 255, 0), -1)


def main():
    _download_model()
    _check_accessibility()

    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

    if not cap.isOpened():
        print("ERROR: Could not open camera.")
        sys.exit(1)

    fps = _measure_fps(cap)
    tracker = HandTracker()
    controller = ScrollController(fps=fps)

    print("Running. Show open palm to scroll. Press Q to quit.")

    while True:
        ret, bgr_frame = cap.read()
        if not ret:
            break

        bgr_frame = cv2.flip(bgr_frame, 1)  # mirror for natural interaction
        landmarks = tracker.detect(bgr_frame)
        scroll_px = controller.update(landmarks)

        if scroll_px != 0:
            quartz_emitter.post_scroll(scroll_px)

        # Debug overlay
        state = controller.gesture_state
        label = "SCROLLING" if state == GestureState.ENGAGED else "idle"
        color = (0, 255, 0) if state == GestureState.ENGAGED else (128, 128, 128)
        cv2.putText(bgr_frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
        if scroll_px != 0:
            cv2.putText(
                bgr_frame,
                f"delta: {scroll_px:+d}px",
                (10, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (200, 200, 200),
                1,
            )
        if landmarks:
            _draw_landmarks(bgr_frame, landmarks)

        cv2.imshow("Hand Gesture Controller", bgr_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    tracker.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
