"""
hand_detector.py

Wraps Google's MediaPipe Hands solution to provide simple, reusable
hand-tracking functionality: detecting a hand in a video frame,
extracting landmark coordinates, and drawing the landmarks/connections
on top of the frame for visualization.

This module intentionally contains no game logic. Its only job is
computer-vision hand tracking.
"""

import cv2
import mediapipe as mp

import config


class HandDetector:
    """Detects a single hand in a video frame using MediaPipe Hands
    and exposes pixel-space landmark coordinates for downstream
    gesture recognition.
    """

    def __init__(self):
        self._mp_hands = mp.solutions.hands
        self._mp_drawing = mp.solutions.drawing_utils
        self._mp_styles = mp.solutions.drawing_styles

        # NOTE: static_image_mode=False enables MediaPipe's internal
        # tracking between frames, which is faster and smoother for
        # real-time webcam video than re-detecting every frame.
        self.hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=config.MAX_NUM_HANDS,
            min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
        )

        # Custom drawing specs so the hand overlay matches the app's
        # dark theme instead of MediaPipe's default bright colors.
        self._landmark_spec = self._mp_drawing.DrawingSpec(
            color=config.COLOR_LANDMARK, thickness=-1, circle_radius=4
        )
        self._connection_spec = self._mp_drawing.DrawingSpec(
            color=config.COLOR_CONNECTION, thickness=2
        )

    def find_hand(self, frame_bgr):
        """Processes a BGR frame and returns a dict describing the
        first detected hand, or None if no hand is present.

        Returned dict keys:
            landmarks_px : list of (x, y) pixel coordinates, indexed
                            the same way as MediaPipe's 21 hand
                            landmarks (0 = wrist, 4 = thumb tip, etc.)
            handedness   : "Left" or "Right" as reported by MediaPipe
            raw          : the raw MediaPipe landmark object, kept in
                            case drawing needs it later
        """
        rgb_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        results = self.hands.process(rgb_frame)

        if not results.multi_hand_landmarks:
            return None

        hand_landmarks = results.multi_hand_landmarks[0]
        height, width = frame_bgr.shape[:2]

        landmarks_px = [
            (int(lm.x * width), int(lm.y * height))
            for lm in hand_landmarks.landmark
        ]

        handedness_label = "Unknown"
        if results.multi_handedness:
            handedness_label = results.multi_handedness[0].classification[0].label

        return {
            "landmarks_px": landmarks_px,
            "handedness": handedness_label,
            "raw": hand_landmarks,
        }

    def draw_landmarks(self, frame_bgr, raw_hand_landmarks):
        """Draws the hand skeleton (landmarks + connections) directly
        onto the given frame using the app's accent color scheme.
        """
        self._mp_drawing.draw_landmarks(
            frame_bgr,
            raw_hand_landmarks,
            self._mp_hands.HAND_CONNECTIONS,
            landmark_drawing_spec=self._landmark_spec,
            connection_drawing_spec=self._connection_spec,
        )

    def close(self):
        """Releases MediaPipe resources. Call this once when the
        application is shutting down.
        """
        self.hands.close()
