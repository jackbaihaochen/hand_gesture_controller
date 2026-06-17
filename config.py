CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

MODEL_PATH = "hand_landmarker.task"
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
)

# Gesture classifier
OPEN_PALM_MIN_FINGERS = 4
FIST_MAX_FINGERS = 1
DEBOUNCE_FRAMES = 3

# Scroll
SCROLL_GAIN = 2.5
INVERT_SCROLL = False

# One-Euro filter
ONE_EURO_MIN_CUTOFF = 1.0
ONE_EURO_BETA = 0.007
ONE_EURO_D_CUTOFF = 1.0
