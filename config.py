"""
config.py

Central configuration file for the AI Rock Paper Scissors project.
Edit the values in this file to change camera behavior, gesture
recognition sensitivity, UI appearance, and author information.

Nothing in this file contains executable game logic; it only stores
constants that are imported by the other modules.
"""

# ---------------------------------------------------------------------------
# Camera settings
# ---------------------------------------------------------------------------
CAMERA_INDEX = 0            # Change to 1, 2, etc. if you have multiple cameras
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 30

# ---------------------------------------------------------------------------
# MediaPipe Hands settings
# ---------------------------------------------------------------------------
MAX_NUM_HANDS = 1
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.6

# ---------------------------------------------------------------------------
# Gesture recognition / round timing settings
# ---------------------------------------------------------------------------
# Number of consecutive frames a gesture must be detected identically
# before it is accepted as "stable" enough to play a round.
GESTURE_STABILITY_FRAMES = 8

# Minimum time (in seconds) that must pass between two counted rounds.
# This prevents a single held gesture from being counted repeatedly.
ROUND_COOLDOWN_SECONDS = 2.0

# Time (in seconds) that the round result stays on screen before the
# game returns to "waiting for gesture" mode.
RESULT_DISPLAY_SECONDS = 2.0

# ---------------------------------------------------------------------------
# UI Colors (BGR format, since OpenCV uses BGR instead of RGB)
# ---------------------------------------------------------------------------
COLOR_BACKGROUND = (24, 22, 20)          # near-black charcoal background
COLOR_PANEL = (38, 35, 32)               # slightly lighter panel background
COLOR_PANEL_BORDER = (60, 56, 52)        # subtle panel border
COLOR_ACCENT = (60, 168, 240)            # warm amber-orange accent (BGR -> orange)
COLOR_ACCENT_SOFT = (46, 120, 168)       # muted accent for secondary elements
COLOR_TEXT_PRIMARY = (235, 235, 235)     # near-white text
COLOR_TEXT_SECONDARY = (150, 150, 150)   # gray secondary text
COLOR_WIN = (110, 200, 120)              # green for player win
COLOR_LOSE = (80, 80, 220)               # red for player loss
COLOR_DRAW = (0, 190, 220)               # yellow-gold for draw
COLOR_LANDMARK = (60, 168, 240)          # hand landmark point color
COLOR_CONNECTION = (150, 150, 150)       # hand connection line color

# ---------------------------------------------------------------------------
# UI Text
# ---------------------------------------------------------------------------
APP_TITLE = "AI ROCK PAPER SCISSORS"
APP_SUBTITLE = "Hand Gesture Recognition • Local Computer Vision"
TEXT_NO_HAND = "Show your hand to the camera"
TEXT_CAMERA_ERROR = "Unable to access webcam. Please check your camera connection and permissions."
TEXT_INSTRUCTIONS = "Press R to reset  |  Press Q to quit"
TEXT_WAITING = "Show a Rock, Paper, or Scissors gesture to play"

GESTURE_LABELS = {
    "ROCK": "ROCK",
    "PAPER": "PAPER",
    "SCISSORS": "SCISSORS",
    "UNKNOWN": "..."
}

GESTURE_EMOJI = {
    "ROCK": "FIST",
    "PAPER": "OPEN",
    "SCISSORS": "PEACE",
    "UNKNOWN": "--"
}

# ---------------------------------------------------------------------------
# Author information (do not change unless you are redistributing your
# own fork of this project)
# ---------------------------------------------------------------------------
AUTHOR_NAME = "Zafir Khan"
AUTHOR_EMAIL = "2008zafirkhan@gmail.com"
AUTHOR_LINKEDIN = "https://www.linkedin.com/in/zafir-khan-0b2098423/"
