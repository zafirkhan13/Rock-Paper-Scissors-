"""
game_logic.py

Contains all non-visual game rules for Rock Paper Scissors:
- generating a random computer move
- determining the winner of a round
- tracking player score, computer score, and draws
- enforcing gesture-stability and round-cooldown timing so a single
  held gesture is not counted as multiple rounds

This module has no dependency on OpenCV or MediaPipe; it only deals
with game state, so it can be tested or reused independently of the
UI/camera code in main.py.
"""

import random
import time

import config

VALID_MOVES = ("ROCK", "PAPER", "SCISSORS")

# Maps a move to the move it defeats.
BEATS = {
    "ROCK": "SCISSORS",
    "SCISSORS": "PAPER",
    "PAPER": "ROCK",
}


class GameLogic:
    """Tracks scores and controls when a detected gesture is allowed
    to count as a new round, using stability + cooldown rules.
    """

    def __init__(self):
        self.player_score = 0
        self.computer_score = 0
        self.draw_count = 0

        self.player_move = None
        self.computer_move = None
        self.result_text = None
        self.result_state = None  # "WIN", "LOSE", "DRAW", or None

        self._last_round_time = 0.0
        self._stable_gesture = None
        self._stable_count = 0
        self._round_in_progress_display_until = 0.0

    def reset(self):
        """Resets scores and the current round display, without
        affecting the webcam/hand-tracking state.
        """
        self.player_score = 0
        self.computer_score = 0
        self.draw_count = 0
        self.player_move = None
        self.computer_move = None
        self.result_text = None
        self.result_state = None
        self._last_round_time = 0.0
        self._stable_gesture = None
        self._stable_count = 0
        self._round_in_progress_display_until = 0.0

    @staticmethod
    def generate_computer_move():
        """Returns a uniformly random move for the computer player."""
        return random.choice(VALID_MOVES)

    @staticmethod
    def determine_winner(player_move, computer_move):
        """Returns "WIN", "LOSE", or "DRAW" from the player's
        perspective, given two valid moves.
        """
        if player_move == computer_move:
            return "DRAW"
        if BEATS[player_move] == computer_move:
            return "WIN"
        return "LOSE"

    def _is_result_currently_displayed(self):
        return time.time() < self._round_in_progress_display_until

    def update(self, detected_gesture):
        """Feeds the current frame's detected gesture ("ROCK",
        "PAPER", "SCISSORS", or "UNKNOWN"/None) into the stability
        and cooldown state machine. When a gesture has been held
        steadily for enough frames and the cooldown has elapsed,
        this triggers a new round automatically.

        Returns True if a new round was just played this call.
        """
        # While a result is still being shown on screen, do not
        # evaluate new rounds -- this gives the player a clear pause
        # between rounds instead of instant back-to-back scoring.
        if self._is_result_currently_displayed():
            return False

        if detected_gesture not in VALID_MOVES:
            self._stable_gesture = None
            self._stable_count = 0
            return False

        if detected_gesture == self._stable_gesture:
            self._stable_count += 1
        else:
            self._stable_gesture = detected_gesture
            self._stable_count = 1

        enough_stability = self._stable_count >= config.GESTURE_STABILITY_FRAMES
        cooldown_elapsed = (time.time() - self._last_round_time) >= config.ROUND_COOLDOWN_SECONDS

        if enough_stability and cooldown_elapsed:
            self._play_round(detected_gesture)
            return True

        return False

    def _play_round(self, player_move):
        computer_move = self.generate_computer_move()
        outcome = self.determine_winner(player_move, computer_move)

        self.player_move = player_move
        self.computer_move = computer_move
        self.result_state = outcome

        if outcome == "WIN":
            self.player_score += 1
            self.result_text = "YOU WIN!"
        elif outcome == "LOSE":
            self.computer_score += 1
            self.result_text = "COMPUTER WINS!"
        else:
            self.draw_count += 1
            self.result_text = "DRAW!"

        self._last_round_time = time.time()
        self._round_in_progress_display_until = time.time() + config.RESULT_DISPLAY_SECONDS

        # Reset stability tracking so the player must clearly change
        # or re-show their gesture before the next round can trigger.
        self._stable_gesture = None
        self._stable_count = 0
