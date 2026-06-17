import time
import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision
import config


class HandTracker:
    def __init__(self):
        base_options = mp.tasks.BaseOptions(model_asset_path=config.MODEL_PATH)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._landmarker = vision.HandLandmarker.create_from_options(options)
        self._last_ts_ms = 0

    def detect(self, bgr_frame):
        rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        ts = int(time.time() * 1000)
        timestamp_ms = max(ts, self._last_ts_ms + 1)
        self._last_ts_ms = timestamp_ms
        result = self._landmarker.detect_for_video(mp_image, timestamp_ms)
        if result.hand_landmarks:
            return result.hand_landmarks[0]
        return None

    def close(self):
        self._landmarker.close()
