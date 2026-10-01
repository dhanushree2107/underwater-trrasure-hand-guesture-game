"""
Unit tests verifying dual-hand tracking, cooperative gestures,
and dual-hand swimming mechanics.
"""

import time
from hand_tracking.gesture_detector import GestureDetector, GestureType, PinchState
from game.player import Player

def _make_palm_landmarks():
    """Generates synthetic 21 landmarks for an open palm."""
    wrist = (0.5, 0.9, 0.0)
    landmarks = [wrist]
    landmarks.extend([(0.4, 0.8, 0.0), (0.35, 0.7, 0.0), (0.3, 0.6, 0.0), (0.2, 0.4, 0.0)])
    landmarks.extend([(0.45, 0.6, 0.0), (0.45, 0.5, 0.0), (0.45, 0.4, 0.0), (0.45, 0.2, 0.0)])
    landmarks.extend([(0.5, 0.6, 0.0), (0.5, 0.5, 0.0), (0.5, 0.4, 0.0), (0.5, 0.18, 0.0)])
    landmarks.extend([(0.55, 0.6, 0.0), (0.55, 0.5, 0.0), (0.55, 0.4, 0.0), (0.55, 0.2, 0.0)])
    landmarks.extend([(0.6, 0.65, 0.0), (0.6, 0.55, 0.0), (0.6, 0.45, 0.0), (0.6, 0.25, 0.0)])
    return landmarks

def _make_fist_landmarks():
    """Generates synthetic 21 landmarks for a closed fist (shield)."""
    wrist = (0.5, 0.9, 0.0)
    landmarks = [wrist]
    # Thumb (1-4) curled in across palm
    landmarks.extend([(0.48, 0.85, 0.0), (0.50, 0.82, 0.0), (0.52, 0.80, 0.0), (0.53, 0.80, 0.0)])
    # Index, Middle, Ring, Pinky curled down
    for x_offset in [0.47, 0.50, 0.53, 0.56]:
        landmarks.extend([(x_offset, 0.78, 0.0), (x_offset, 0.76, 0.0), (x_offset, 0.80, 0.0), (x_offset, 0.83, 0.0)])
    return landmarks

def _make_pinch_landmarks():
    """Generates synthetic 21 landmarks for an index-thumb pinch."""
    wrist = (0.5, 0.9, 0.0)
    landmarks = [wrist]
    # Thumb tip at (0.45, 0.35, 0.0)
    landmarks.extend([(0.48, 0.7, 0.0), (0.47, 0.55, 0.0), (0.46, 0.45, 0.0), (0.45, 0.35, 0.0)])
    # Index tip touching thumb tip at (0.45, 0.35, 0.0)
    landmarks.extend([(0.47, 0.7, 0.0), (0.46, 0.55, 0.0), (0.45, 0.45, 0.0), (0.45, 0.35, 0.0)])
    # Middle, Ring, Pinky curled
    landmarks.extend([(0.5, 0.75, 0.0), (0.5, 0.72, 0.0), (0.5, 0.70, 0.0), (0.5, 0.68, 0.0)])
    landmarks.extend([(0.52, 0.75, 0.0), (0.52, 0.72, 0.0), (0.52, 0.70, 0.0), (0.52, 0.68, 0.0)])
    landmarks.extend([(0.54, 0.75, 0.0), (0.54, 0.72, 0.0), (0.54, 0.70, 0.0), (0.54, 0.68, 0.0)])
    return landmarks

def test_dual_hand_independent_pinch():
    """Tests that either hand can pinch independently without blocking the other."""
    gd = GestureDetector()
    h1 = _make_pinch_landmarks()
    h2 = _make_palm_landmarks()

    res = gd.process_dual_landmarks(
        hand1_landmarks=h1,
        hand1_x=700.0,
        hand1_y=350.0,
        hand1_label="Right",
        hand2_landmarks=h2,
        hand2_x=300.0,
        hand2_y=350.0,
        hand2_label="Left"
    )
    assert res["has_dual_hands"] is True
    assert res["is_dual_hand_swimming"] is True
    assert res["pinch_triggered"] is True
    assert res["first_gesture"] == GestureType.PINCH

def test_dual_hand_tactical_fist_and_grab():
    """Tests cooperative two-handed play: Left Hand holds Fist (Shield) while Right Hand pinches (Grab)."""
    gd = GestureDetector()
    right_hand = _make_pinch_landmarks()
    left_hand = _make_fist_landmarks()

    res = gd.process_dual_landmarks(
        hand1_landmarks=right_hand,
        hand1_x=750.0,
        hand1_y=400.0,
        hand1_label="Right",
        hand2_landmarks=left_hand,
        hand2_x=250.0,
        hand2_y=400.0,
        hand2_label="Left"
    )
    assert res["shield_active"] is True
    assert res["pinch_triggered"] is True

def test_dual_hand_mega_palm_current():
    """Tests that opening both hands simultaneously triggers a Mega Tidal Current."""
    gd = GestureDetector()
    h1 = _make_palm_landmarks()
    h2 = _make_palm_landmarks()

    res = gd.process_dual_landmarks(
        hand1_landmarks=h1,
        hand1_x=650.0,
        hand1_y=350.0,
        hand2_landmarks=h2,
        hand2_x=350.0,
        hand2_y=350.0
    )
    assert res["is_mega_palm"] is True
    assert res["palm_triggered"] is True

def test_swimmer_dual_hand_propulsion_boost():
    """Tests that swimmer travels significantly faster when dual-hand swimming is active."""
    player_single = Player()
    player_dual = Player()

    dt = 0.016
    target_x = 1200.0
    target_y = 360.0

    # Simulate 5 frames of single-hand navigation
    for _ in range(5):
        player_single.update(dt, target_x, target_y, is_pinching=False, shield_active=False, is_dual_hand_swimming=False, paddle_boost=1.0)

    # Simulate 5 frames of dual-hand swimming with paddle boost
    for _ in range(5):
        player_dual.update(dt, target_x, target_y, is_pinching=False, shield_active=False, is_dual_hand_swimming=True, paddle_boost=1.75)

    assert player_dual.vx > player_single.vx
    assert player_dual.x > player_single.x
