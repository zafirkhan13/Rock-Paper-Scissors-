"""
gesture_recognizer.py

Converts raw MediaPipe hand landmark pixel coordinates into a
Rock / Paper / Scissors classification.

Approach
--------
For each of the five fingers we estimate whether it is "extended" or
"folded" by comparing distances from the wrist landmark (0) to the
fingertip versus the wrist to that finger's middle joint. This
distance-ratio approach is more tolerant of hand rotation/tilt than a
naive "tip.y < pip.y" check, because it does not assume the hand is
perfectly upright in the frame.

This is a heuristic, geometry-based classifier, not a trained machine
learning model. It works well for a hand held reasonably flat and
facing the camera, but like any landmark-based heuristic it is not
100% accurate for every possible hand angle, lighting condition, or
partial occlusion.
"""

import math

import config

# MediaPipe Hands landmark indices used for finger-state detection.
WRIST = 0

THUMB_CMC = 1
THUMB_MCP = 2
THUMB_IP = 3
THUMB_TIP = 4

INDEX_MCP = 5
INDEX_PIP = 6
INDEX_TIP = 8

MIDDLE_MCP = 9
MIDDLE_PIP = 10
MIDDLE_TIP = 12

RING_MCP = 13
RING_PIP = 14
RING_TIP = 16

PINKY_MCP = 17
PINKY_PIP = 18
PINKY_TIP = 20


def _distance(point_a, point_b):
    """Euclidean distance between two (x, y) pixel points."""
    return math.hypot(point_a[0] - point_b[0], point_a[1] - point_b[1])


def _finger_extended(landmarks, mcp_idx, pip_idx, tip_idx, wrist_idx=WRIST, margin=1.08):
    """Returns True if a finger appears extended.

    A finger is considered extended when the fingertip is meaningfully
    farther from the wrist than that finger's PIP (middle) joint is.
    The `margin` multiplier avoids flip-flopping on borderline/near-
    straight fingers.
    """
    wrist = landmarks[wrist_idx]
    tip_dist = _distance(wrist, landmarks[tip_idx])
    pip_dist = _distance(wrist, landmarks[pip_idx])
    return tip_dist > pip_dist * margin


def _thumb_extended(landmarks):
    """Thumb extension is estimated differently from the other
    fingers because the thumb moves mostly sideways rather than
    up/down. We compare the distance from the thumb tip to the
    index finger's base (MCP) against the distance from the thumb's
    own base (CMC) to the index MCP. When the thumb is folded across
    the palm (as in a fist), the tip sits close to the palm/index
    base; when extended, it moves away from it.
    """
    index_mcp = landmarks[INDEX_MCP]
    thumb_tip = landmarks[THUMB_TIP]
    thumb_cmc = landmarks[THUMB_CMC]

    tip_to_index = _distance(thumb_tip, index_mcp)
    cmc_to_index = _distance(thumb_cmc, index_mcp)

    # Also require the thumb tip to be reasonably far from the wrist
    # relative to the thumb MCP, to reduce false positives.
    wrist = landmarks[WRIST]
    thumb_mcp = landmarks[THUMB_MCP]
    tip_to_wrist = _distance(thumb_tip, wrist)
    mcp_to_wrist = _distance(thumb_mcp, wrist)

    return (tip_to_index > cmc_to_index * 1.15) and (tip_to_wrist > mcp_to_wrist * 1.05)


def get_finger_states(landmarks_px):
    """Returns a dict of booleans describing which fingers are
    extended: {"thumb", "index", "middle", "ring", "pinky"}.
    """
    return {
        "thumb": _thumb_extended(landmarks_px),
        "index": _finger_extended(landmarks_px, INDEX_MCP, INDEX_PIP, INDEX_TIP),
        "middle": _finger_extended(landmarks_px, MIDDLE_MCP, MIDDLE_PIP, MIDDLE_TIP),
        "ring": _finger_extended(landmarks_px, RING_MCP, RING_PIP, RING_TIP),
        "pinky": _finger_extended(landmarks_px, PINKY_MCP, PINKY_PIP, PINKY_TIP),
    }


def classify_gesture(landmarks_px):
    """Classifies a hand's landmarks as ROCK, PAPER, SCISSORS, or
    UNKNOWN if the finger pattern does not clearly match any of the
    three supported gestures.
    """
    states = get_finger_states(landmarks_px)
    extended_count = sum(states.values())

    # PAPER: every finger extended (thumb included).
    if states["index"] and states["middle"] and states["ring"] and states["pinky"]:
        return "PAPER", states

    # SCISSORS: index and middle extended, ring and pinky folded.
    # Thumb state is ignored since players commonly rest it in
    # either position while making a scissors sign.
    if (
        states["index"]
        and states["middle"]
        and not states["ring"]
        and not states["pinky"]
    ):
        return "SCISSORS", states

    # ROCK: a closed fist -- at most one finger (typically the thumb)
    # reads as ambiguously extended, and index/middle/ring/pinky are
    # all folded.
    if not states["index"] and not states["middle"] and not states["ring"] and not states["pinky"]:
        return "ROCK", states

    # Anything else (transitional hand shapes, partial gestures) is
    # reported as UNKNOWN so the game does not register a false round.
    return "UNKNOWN", states
