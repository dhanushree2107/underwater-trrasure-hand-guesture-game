"""
Unit tests for gesture recognition and state machine transitions.
"""

import time
from hand_tracking.gesture_detector import GestureDetector, GestureType, PinchState
from config import PINCH_THRESHOLD, PINCH_RELEASE_THRESHOLD

def test_initial_state():
    detector = GestureDetector()
    assert detector.pinch_state == PinchState.IDLE
    assert detector.current_gesture == GestureType.NONE
    assert detector.is_fist is False

def test_fallback_mouse_pinch():
    detector = GestureDetector()
    # 1. Click LMB -> should trigger pinch once
    res1 = detector.update_fallback_mouse(100, 100, lmb=True, rmb=False, space=False, key_s=False)
    assert res1["pinch_triggered"] is True
    assert res1["current_gesture"] == GestureType.PINCH

    # 2. Hold LMB -> state is PINCHED, but pinch_triggered should be False (one trigger per pinch!)
    res2 = detector.update_fallback_mouse(100, 100, lmb=True, rmb=False, space=False, key_s=False)
    assert res2["pinch_triggered"] is False
    assert detector.pinch_state == PinchState.PINCHED

    # 3. Release LMB -> resets to IDLE
    res3 = detector.update_fallback_mouse(100, 100, lmb=False, rmb=False, space=False, key_s=False)
    assert res3["pinch_triggered"] is False
    assert detector.pinch_state == PinchState.IDLE

def test_fallback_mouse_sonar():
    detector = GestureDetector()
    res = detector.update_fallback_mouse(200, 200, lmb=False, rmb=True, space=False, key_s=False)
    assert res["sonar_triggered"] is True
    assert res["current_gesture"] == GestureType.TWO_FINGERS

    # Spamming RMB immediately without cooldown should not trigger again
    res2 = detector.update_fallback_mouse(200, 200, lmb=False, rmb=True, space=False, key_s=False)
    assert res2["sonar_triggered"] is False

def test_fallback_shield_fist():
    detector = GestureDetector()
    res = detector.update_fallback_mouse(150, 150, lmb=False, rmb=False, space=False, key_s=True)
    assert res["shield_active"] is True
    assert res["current_gesture"] == GestureType.FIST

def test_synthetic_open_palm():
    detector = GestureDetector()
    # Create synthetic 21 landmarks for open palm: all finger tips extended far from wrist
    wrist = (0.5, 0.9, 0.0)
    landmarks = [wrist]
    # Thumb (1-4)
    landmarks.extend([(0.4, 0.8, 0.0), (0.35, 0.7, 0.0), (0.3, 0.6, 0.0), (0.2, 0.4, 0.0)])
    # Index (5-8)
    landmarks.extend([(0.45, 0.6, 0.0), (0.45, 0.5, 0.0), (0.45, 0.4, 0.0), (0.45, 0.2, 0.0)])
    # Middle (9-12)
    landmarks.extend([(0.5, 0.6, 0.0), (0.5, 0.5, 0.0), (0.5, 0.4, 0.0), (0.5, 0.18, 0.0)])
    # Ring (13-16)
    landmarks.extend([(0.55, 0.6, 0.0), (0.55, 0.5, 0.0), (0.55, 0.4, 0.0), (0.55, 0.2, 0.0)])
    # Pinky (17-20)
    landmarks.extend([(0.6, 0.65, 0.0), (0.6, 0.55, 0.0), (0.6, 0.45, 0.0), (0.6, 0.25, 0.0)])

    res = detector.process_landmarks(landmarks, raw_x=640, raw_y=360)
    assert res["current_gesture"] == GestureType.OPEN_PALM
    assert res["palm_triggered"] is True

def test_maintain_position():
    detector = GestureDetector()
    detector.cursor_x = 750.0
    detector.cursor_y = 420.0
    res = detector.maintain_position(lmb=False, rmb=False, space=False, key_s=False)
    # Cursor coordinates must stay intact without snapping to mouse
    assert res["cursor_pos"] == (750, 420)

def test_click_release_no_sticky():
    detector = GestureDetector()
    # 1. Trigger pinch
    res1 = detector.update_fallback_mouse(200, 200, lmb=True, rmb=False, space=False, key_s=False)
    assert res1["pinch_triggered"] is True
    assert detector.pinch_state == PinchState.TRIGGERED or detector.pinch_state == PinchState.PINCHED

    # 2. Release pinch immediately resets to IDLE
    res2 = detector.update_fallback_mouse(200, 200, lmb=False, rmb=False, space=False, key_s=False)
    assert detector.pinch_state == PinchState.IDLE

    # 3. Can click again after cooldown without sticking
    time.sleep(0.3)
    res3 = detector.update_fallback_mouse(200, 200, lmb=True, rmb=False, space=False, key_s=False)
    assert res3["pinch_triggered"] is True
