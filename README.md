# AI Rock Paper Scissors Using Hand Gestures

A real-time computer vision game that lets you play Rock Paper Scissors against the computer using nothing but your webcam and your hand. Built with Python, OpenCV, and MediaPipe, and rendered in a clean, modern dark-themed interface.

---

## 1. Project Overview

This project is a desktop application that uses a standard webcam to detect and track a human hand, classify the hand shape as Rock, Paper, or Scissors, and play a full round of the classic game against a randomized computer opponent — entirely offline, in real time.

## 2. Problem Statement

Rock Paper Scissors is traditionally a two-player game — it normally requires another person to play against. This project demonstrates how computer vision and hand-tracking can replace the second player, allowing a single user to play the game against a computer opponent using only hand gestures captured through a webcam.

## 3. Objective

The objective of this project is to develop a real-time computer-vision game that detects Rock, Paper, and Scissors hand gestures through a webcam feed and allows the user to play a scored game against a computer opponent, using only local processing.

## 4. Features

- Real-time webcam video capture
- Real-time hand detection and landmark tracking using MediaPipe
- Finger-state (extended/folded) detection for all five fingers
- Rock, Paper, and Scissors gesture classification
- Randomized computer move generation
- Automatic winner determination per round
- Player score, computer score, and draw count tracking
- Gesture stability and round cooldown logic (prevents one held gesture from being counted as multiple rounds)
- Clear on-screen messaging when no hand is visible
- Clear on-screen error messaging if the webcam cannot be accessed
- Game reset (new game) support
- Clean exit via keyboard
- Modern dark-themed, uncluttered UI with a single accent color

## 5. How the System Works

1. The application opens the default webcam using OpenCV.
2. Each frame is passed to MediaPipe Hands, which detects a hand (if present) and returns 21 hand landmarks.
3. The landmark coordinates are analyzed to determine which fingers are extended and which are folded.
4. The finger-state pattern is matched against known Rock, Paper, and Scissors patterns.
5. If a gesture is held steadily for a short number of frames and enough time has passed since the last round, a round is triggered automatically.
6. The computer randomly selects Rock, Paper, or Scissors.
7. The winner is calculated using standard Rock-Paper-Scissors rules.
8. Scores are updated and the result is displayed on screen for a short period before the game returns to waiting for the next gesture.

## 6. Gesture Recognition

Gesture recognition is landmark-based (geometric), not a trained deep-learning classifier. For each finger, the app compares the distance from the wrist to the fingertip against the distance from the wrist to that finger's middle joint — if the tip is meaningfully farther away, the finger is considered extended. The thumb uses a slightly different comparison based on its distance from the index finger's base, since the thumb moves sideways rather than up and down.

This approach is reasonably tolerant of different hand angles and some tilt, but it is a heuristic, not a certified computer-vision model. **It is not claimed to be 100% accurate** — recognition quality can vary with lighting, camera quality, hand angle, distance from the camera, and partial occlusion of the fingers.

Recognized gestures:

| Gesture  | Finger Pattern                                             |
|----------|--------------------------------------------------------------|
| Rock     | All fingers folded (closed fist)                            |
| Paper    | All fingers extended (open hand)                             |
| Scissors | Index and middle fingers extended; ring and pinky folded     |

## 7. Game Rules

- Rock beats Scissors
- Scissors beats Paper
- Paper beats Rock
- Identical gestures result in a Draw

After every valid, stable round, the player score, computer score, or draw count is updated accordingly.

## 8. Technologies Used

- **Python 3** — application language
- **OpenCV** — webcam capture, image processing, and UI rendering
- **MediaPipe** — real-time hand detection and landmark tracking
- **NumPy** — array/image buffer handling

No paid APIs, cloud services, or external processing are used. All computation runs locally on your machine.

## 9. Project Structure

```
Zafir-AI-Rock-Paper-Scissors/
├── main.py                # Application loop, webcam handling, and UI rendering
├── hand_detector.py        # MediaPipe hand tracking and landmark extraction
├── gesture_recognizer.py   # Rock / Paper / Scissors gesture classification
├── game_logic.py           # Computer move generation, winner logic, scoring, cooldown
├── config.py                # Camera, recognition, cooldown, UI, and author settings
├── requirements.txt         # Python dependencies
├── README.md                 # Project documentation (this file)
├── LICENSE                    # MIT License
├── .gitignore
├── assets/                    # Reserved for optional icons/images
└── screenshots/                # Reserved for gameplay screenshots
```

## 10. Requirements

- Python 3.9 – 3.11 (recommended, for best MediaPipe compatibility)
- A working webcam
- Windows, macOS, or Linux (primary target: Windows)

## 11. Installation

Open a terminal in the project folder and install the dependencies:

```bash
pip install -r requirements.txt
```

## 12. How to Run

```bash
python main.py
```

A window titled **"AI ROCK PAPER SCISSORS"** will open showing your live webcam feed.

## 13. How to Play

1. Sit facing your webcam with your hand clearly visible.
2. Make a **Rock** (closed fist), **Paper** (open hand), or **Scissors** (index + middle finger "V") gesture.
3. Hold the gesture steady for a moment — the app needs a few consistent frames before it counts a round, to avoid accidental triggers.
4. The computer's move and the round result appear on screen automatically, along with updated scores.
5. Wait for the short cooldown, then show your next gesture to play again.
6. Press **R** at any time to reset the score and start a new game.
7. Press **Q** at any time to quit the application.

## 14. Troubleshooting

- **"Unable to access webcam" message appears:** Make sure no other application is currently using the camera, check that your camera is properly connected, and confirm the app has camera permission in your operating system's privacy settings.
- **Gestures are not recognized reliably:** Make sure your whole hand is visible in the frame, keep it reasonably close to the camera, ensure good lighting, and try holding the gesture flatter and more directly facing the camera.
- **The app feels laggy:** Lower `CAMERA_WIDTH` / `CAMERA_HEIGHT` in `config.py`, close other applications using the camera or GPU, or ensure you are not running the app inside a resource-constrained virtual machine.
- **Rounds trigger too fast or too slow:** Adjust `GESTURE_STABILITY_FRAMES` and `ROUND_COOLDOWN_SECONDS` in `config.py`.
- **`ModuleNotFoundError` when running:** Re-run `pip install -r requirements.txt` and confirm you are using the same Python environment/interpreter you installed the packages into.

## 15. Windows Compatibility

This project is designed to run on Windows out of the box. On Windows, the app attempts to open the webcam using the DirectShow backend (`cv2.CAP_DSHOW`) for more reliable camera initialization, and automatically falls back to the default backend if that is unavailable. It also runs on macOS and Linux, since it relies only on cross-platform OpenCV and MediaPipe APIs.

## 16. Privacy Information

- All webcam processing happens **locally** on your device.
- **No webcam video or images are recorded or saved** to disk by this application.
- **No images or video are uploaded** anywhere.
- **No cloud APIs or external servers** are used for hand detection or game logic.
- **No personal information is collected, transmitted, or stored** by this application.

## 17. Configuration / Editing Guide

All adjustable settings live in `config.py`:

- `CAMERA_INDEX`, `CAMERA_WIDTH`, `CAMERA_HEIGHT`, `CAMERA_FPS` — camera setup
- `MIN_DETECTION_CONFIDENCE`, `MIN_TRACKING_CONFIDENCE`, `MAX_NUM_HANDS` — MediaPipe hand-tracking sensitivity
- `GESTURE_STABILITY_FRAMES` — how many consistent frames are needed before a gesture counts
- `ROUND_COOLDOWN_SECONDS`, `RESULT_DISPLAY_SECONDS` — pacing between rounds
- `COLOR_*` values — UI color theme (BGR format, as used by OpenCV)
- `APP_TITLE`, `APP_SUBTITLE`, `TEXT_*`, `GESTURE_LABELS` — on-screen text
- `AUTHOR_NAME`, `AUTHOR_EMAIL`, `AUTHOR_LINKEDIN` — author information shown in project metadata

To change gesture-recognition behavior, edit `gesture_recognizer.py`. To change scoring or round rules, edit `game_logic.py`. To change the on-screen layout, edit the drawing methods in `main.py`.

## 18. License

This project is licensed under the MIT License — see the `LICENSE` file for the full text.

## 19. Author Information

**Zafir Khan**
Email: 2008zafirkhan@gmail.com
LinkedIn: https://www.linkedin.com/in/zafir-khan-0b2098423/
