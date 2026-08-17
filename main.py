"""
main.py

AI Rock Paper Scissors Using Hand Gestures
--------------------------------------------
Entry point for the application. Opens the webcam, runs real-time
MediaPipe hand detection, classifies the player's gesture as Rock,
Paper, or Scissors, plays rounds against a randomized computer
opponent, and renders a modern dark-themed OpenCV interface showing
scores, results, and hand-tracking status.

Author: Zafir Khan
Email:  2008zafirkhan@gmail.com
LinkedIn: https://www.linkedin.com/in/zafir-khan-0b2098423/

Run with:
    python main.py

Controls:
    Q  -  Quit the application
    R  -  Reset the score / start a new game

All processing (video capture, hand tracking, gesture recognition,
and game logic) happens locally on this machine. No video is
recorded or uploaded, and no cloud services are used.
"""

import sys

import cv2
import numpy as np

import config
from hand_detector import HandDetector
from gesture_recognizer import classify_gesture
from game_logic import GameLogic


class RockPaperScissorsApp:
    """Top-level application: owns the webcam capture, the hand
    detector, the game logic, and the on-screen UI rendering.
    """

    def __init__(self):
        self.hand_detector = HandDetector()
        self.game = GameLogic()
        self.capture = None
        self.window_name = config.APP_TITLE

    # ------------------------------------------------------------------
    # Setup / teardown
    # ------------------------------------------------------------------
    def _open_camera(self):
        capture = cv2.VideoCapture(config.CAMERA_INDEX, cv2.CAP_DSHOW) \
            if sys.platform.startswith("win") else cv2.VideoCapture(config.CAMERA_INDEX)

        if not capture.isOpened():
            # Fallback attempt without the Windows-specific backend flag,
            # in case CAP_DSHOW is unavailable on this system.
            capture = cv2.VideoCapture(config.CAMERA_INDEX)

        if not capture.isOpened():
            return None

        capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
        capture.set(cv2.CAP_PROP_FPS, config.CAMERA_FPS)
        return capture

    def _show_camera_error_screen(self):
        """Displays a persistent error screen when the webcam cannot
        be opened at all, and waits for the user to quit.
        """
        error_frame = np.full(
            (config.CAMERA_HEIGHT, config.CAMERA_WIDTH, 3),
            config.COLOR_BACKGROUND,
            dtype=np.uint8,
        )
        self._draw_centered_text(
            error_frame,
            config.TEXT_CAMERA_ERROR,
            y=config.CAMERA_HEIGHT // 2,
            color=config.COLOR_LOSE,
            font_scale=0.9,
            thickness=2,
            max_width=config.CAMERA_WIDTH - 120,
        )
        self._draw_centered_text(
            error_frame,
            "Press Q to quit",
            y=config.CAMERA_HEIGHT // 2 + 60,
            color=config.COLOR_TEXT_SECONDARY,
            font_scale=0.7,
            thickness=1,
        )

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        while True:
            cv2.imshow(self.window_name, error_frame)
            key = cv2.waitKey(50) & 0xFF
            if key == ord("q") or key == ord("Q"):
                break
            if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1:
                break

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _draw_centered_text(frame, text, y, color, font_scale, thickness, max_width=None):
        font = cv2.FONT_HERSHEY_SIMPLEX
        frame_width = frame.shape[1]

        if max_width and cv2.getTextSize(text, font, font_scale, thickness)[0][0] > max_width:
            # Simple word-wrap for the long camera-error message.
            words = text.split(" ")
            lines, current = [], ""
            for word in words:
                trial = (current + " " + word).strip()
                if cv2.getTextSize(trial, font, font_scale, thickness)[0][0] <= max_width:
                    current = trial
                else:
                    lines.append(current)
                    current = word
            if current:
                lines.append(current)

            line_height = int(35 * font_scale / 0.9) + 10
            start_y = y - (len(lines) - 1) * line_height // 2
            for i, line in enumerate(lines):
                size = cv2.getTextSize(line, font, font_scale, thickness)[0]
                x = (frame_width - size[0]) // 2
                cv2.putText(frame, line, (x, start_y + i * line_height), font, font_scale, color, thickness, cv2.LINE_AA)
            return

        size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        x = (frame_width - size[0]) // 2
        cv2.putText(frame, text, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)

    @staticmethod
    def _draw_panel(frame, x, y, w, h, alpha=0.75):
        """Draws a semi-transparent rounded-look panel by blending a
        filled rectangle with the existing frame, plus a thin border.
        """
        overlay = frame.copy()
        cv2.rectangle(overlay, (x, y), (x + w, y + h), config.COLOR_PANEL, -1)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        cv2.rectangle(frame, (x, y), (x + w, y + h), config.COLOR_PANEL_BORDER, 1, cv2.LINE_AA)

    def _draw_header(self, frame):
        width = frame.shape[1]
        self._draw_panel(frame, 0, 0, width, 70, alpha=0.85)
        cv2.putText(
            frame, config.APP_TITLE, (24, 32),
            cv2.FONT_HERSHEY_SIMPLEX, 0.85, config.COLOR_ACCENT, 2, cv2.LINE_AA,
        )
        cv2.putText(
            frame, config.APP_SUBTITLE, (24, 56),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, config.COLOR_TEXT_SECONDARY, 1, cv2.LINE_AA,
        )

    def _draw_scoreboard(self, frame):
        width = frame.shape[1]
        height = frame.shape[0]
        panel_w = 340
        panel_h = 110
        x = width - panel_w - 20
        y = 82
        self._draw_panel(frame, x, y, panel_w, panel_h, alpha=0.8)

        col_w = panel_w // 3
        labels = ["PLAYER", "COMPUTER", "DRAWS"]
        values = [str(self.game.player_score), str(self.game.computer_score), str(self.game.draw_count)]
        colors = [config.COLOR_WIN, config.COLOR_LOSE, config.COLOR_DRAW]

        for i in range(3):
            col_x = x + i * col_w
            label_size = cv2.getTextSize(labels[i], cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)[0]
            value_size = cv2.getTextSize(values[i], cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]

            label_x = col_x + (col_w - label_size[0]) // 2
            value_x = col_x + (col_w - value_size[0]) // 2

            cv2.putText(frame, labels[i], (label_x, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.42, config.COLOR_TEXT_SECONDARY, 1, cv2.LINE_AA)
            cv2.putText(frame, values[i], (value_x, y + 78), cv2.FONT_HERSHEY_SIMPLEX, 1.0, colors[i], 2, cv2.LINE_AA)

            if i < 2:
                divider_x = col_x + col_w
                cv2.line(frame, (divider_x, y + 15), (divider_x, y + panel_h - 15), config.COLOR_PANEL_BORDER, 1)

    def _draw_moves_panel(self, frame, hand_present, current_gesture):
        width = frame.shape[1]
        panel_w = 460
        panel_h = 130
        x = (width - panel_w) // 2
        y = 82
        self._draw_panel(frame, x, y, panel_w, panel_h, alpha=0.8)

        half = panel_w // 2
        player_label = config.GESTURE_LABELS.get(self.game.player_move, "?") if self.game.player_move else (
            config.GESTURE_LABELS.get(current_gesture, "...") if hand_present else "..."
        )
        computer_label = config.GESTURE_LABELS.get(self.game.computer_move, "?") if self.game.computer_move else "..."

        cv2.putText(frame, "YOU", (x + 30, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.45, config.COLOR_TEXT_SECONDARY, 1, cv2.LINE_AA)
        cv2.putText(frame, "COMPUTER", (x + half + 20, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.45, config.COLOR_TEXT_SECONDARY, 1, cv2.LINE_AA)

        cv2.putText(frame, player_label, (x + 30, y + 78), cv2.FONT_HERSHEY_SIMPLEX, 0.9, config.COLOR_ACCENT, 2, cv2.LINE_AA)
        cv2.putText(frame, computer_label, (x + half + 20, y + 78), cv2.FONT_HERSHEY_SIMPLEX, 0.9, config.COLOR_ACCENT, 2, cv2.LINE_AA)

        cv2.line(frame, (x + half, y + 15), (x + half, y + panel_h - 15), config.COLOR_PANEL_BORDER, 1)

        if self.game.result_text:
            result_color = {
                "WIN": config.COLOR_WIN,
                "LOSE": config.COLOR_LOSE,
                "DRAW": config.COLOR_DRAW,
            }.get(self.game.result_state, config.COLOR_TEXT_PRIMARY)
            size = cv2.getTextSize(self.game.result_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            text_x = x + (panel_w - size[0]) // 2
            cv2.putText(frame, self.game.result_text, (text_x, y + 112), cv2.FONT_HERSHEY_SIMPLEX, 0.7, result_color, 2, cv2.LINE_AA)

    def _draw_status_bar(self, frame, hand_present, camera_ok=True):
        height, width = frame.shape[:2]
        bar_h = 64
        y = height - bar_h
        self._draw_panel(frame, 0, y, width, bar_h, alpha=0.85)

        if not camera_ok:
            status_text = config.TEXT_CAMERA_ERROR
            status_color = config.COLOR_LOSE
        elif not hand_present:
            status_text = config.TEXT_NO_HAND
            status_color = config.COLOR_TEXT_SECONDARY
        else:
            status_text = config.TEXT_WAITING
            status_color = config.COLOR_TEXT_PRIMARY

        cv2.putText(frame, status_text, (24, y + 26), cv2.FONT_HERSHEY_SIMPLEX, 0.55, status_color, 1, cv2.LINE_AA)
        cv2.putText(frame, config.TEXT_INSTRUCTIONS, (24, y + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.45, config.COLOR_TEXT_SECONDARY, 1, cv2.LINE_AA)

        tracking_text = "HAND TRACKED" if hand_present else "NO HAND"
        tracking_color = config.COLOR_WIN if hand_present else config.COLOR_TEXT_SECONDARY
        text_size = cv2.getTextSize(tracking_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
        cv2.circle(frame, (width - text_size[0] - 40, y + 26), 5, tracking_color, -1)
        cv2.putText(frame, tracking_text, (width - text_size[0] - 24, y + 32), cv2.FONT_HERSHEY_SIMPLEX, 0.5, tracking_color, 1, cv2.LINE_AA)

    def _draw_finger_state_indicators(self, frame, finger_states):
        """Small optional row of dots showing which fingers are
        currently read as extended, to make gesture recognition
        visually transparent to the player.
        """
        if finger_states is None:
            return

        order = ["thumb", "index", "middle", "ring", "pinky"]
        x = 24
        y = 90
        spacing = 68

        for i, name in enumerate(order):
            extended = finger_states.get(name, False)
            color = config.COLOR_ACCENT if extended else config.COLOR_PANEL_BORDER
            cx = x + i * spacing
            cv2.circle(frame, (cx, y), 10, color, -1 if extended else 2, cv2.LINE_AA)
            cv2.putText(frame, name[:3].upper(), (cx - 14, y + 26), cv2.FONT_HERSHEY_SIMPLEX, 0.35, config.COLOR_TEXT_SECONDARY, 1, cv2.LINE_AA)

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def run(self):
        self.capture = self._open_camera()

        if self.capture is None:
            self._show_camera_error_screen()
            self._shutdown()
            return

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)

        try:
            while True:
                success, frame = self.capture.read()
                if not success or frame is None:
                    # The camera was available at startup but stopped
                    # returning frames (e.g. unplugged mid-session).
                    blank = np.full((config.CAMERA_HEIGHT, config.CAMERA_WIDTH, 3), config.COLOR_BACKGROUND, dtype=np.uint8)
                    self._draw_centered_text(
                        blank, config.TEXT_CAMERA_ERROR, config.CAMERA_HEIGHT // 2,
                        config.COLOR_LOSE, 0.8, 2, max_width=config.CAMERA_WIDTH - 120,
                    )
                    cv2.imshow(self.window_name, blank)
                    if (cv2.waitKey(30) & 0xFF) in (ord("q"), ord("Q")):
                        break
                    continue

                frame = cv2.flip(frame, 1)  # mirror for a natural "selfie" view

                hand_data = self.hand_detector.find_hand(frame)
                hand_present = hand_data is not None
                current_gesture = "UNKNOWN"
                finger_states = None

                if hand_present:
                    self.hand_detector.draw_landmarks(frame, hand_data["raw"])
                    current_gesture, finger_states = classify_gesture(hand_data["landmarks_px"])
                    self.game.update(current_gesture)
                else:
                    self.game.update(None)

                self._draw_header(frame)
                self._draw_moves_panel(frame, hand_present, current_gesture)
                self._draw_scoreboard(frame)
                self._draw_finger_state_indicators(frame, finger_states)
                self._draw_status_bar(frame, hand_present, camera_ok=True)

                cv2.imshow(self.window_name, frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q") or key == ord("Q"):
                    break
                if key == ord("r") or key == ord("R"):
                    self.game.reset()

                # Allow closing via the window's [X] button too.
                if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1:
                    break
        finally:
            self._shutdown()

    def _shutdown(self):
        if self.capture is not None:
            self.capture.release()
        self.hand_detector.close()
        cv2.destroyAllWindows()


def main():
    app = RockPaperScissorsApp()
    app.run()


if __name__ == "__main__":
    main()
