"""
Underwater Treasure Hunt - Gesture Detector & State Machine
Interprets hand landmarks into discrete, debounce-protected game interactions.
Features exponential smoothing, jitter suppression, and strict state transitions.
"""

import math
import time
from enum import Enum
from typing import Dict, List, Optional, Tuple

from config import (
    PINCH_THRESHOLD,
    PINCH_RELEASE_THRESHOLD,
    INDEX_TAP_BEND_RATIO,
    PINCH_COOLDOWN,
    PALM_COOLDOWN,
    TWO_FINGER_COOLDOWN,
    SMOOTHING_ALPHA,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)

class GestureType(Enum):
    NONE = "NONE"
    MOVE = "MOVE"
    PINCH = "PINCH"
    OPEN_PALM = "OPEN_PALM"
    TWO_FINGERS = "TWO_FINGERS"
    FIST = "FIST"

class PinchState(Enum):
    IDLE = 0
    PINCHED = 1
    TRIGGERED = 2
    RELEASED = 3

class GestureDetector:
    """
    Robust gesture recognition engine with integrated state machine.
    Prevents duplicate firing and jitter while maintaining rapid responsiveness.
    """

    def __init__(self):
        # Smoothing & Position
        self.cursor_x: float = SCREEN_WIDTH / 2.0
        self.cursor_y: float = SCREEN_HEIGHT / 2.0
        self.target_x: float = SCREEN_WIDTH / 2.0
        self.target_y: float = SCREEN_HEIGHT / 2.0
        self.smoothing_alpha: float = SMOOTHING_ALPHA

        # Deadzone threshold in pixels to eradicate static jitter
        self.jitter_deadzone: float = 2.5

        # Gesture State Machine
        self.pinch_state: PinchState = PinchState.IDLE
        self.last_pinch_time: float = 0.0
        self.pinch_distance: float = 1.0

        self.last_palm_time: float = 0.0
        self.palm_triggered: bool = False

        self.last_sonar_time: float = 0.0
        self.sonar_triggered: bool = False

        self.is_fist: bool = False
        self.current_gesture: GestureType = GestureType.NONE

        # Diagnostics
        self.extended_fingers: Dict[str, bool] = {
            "thumb": False,
            "index": False,
            "middle": False,
            "ring": False,
            "pinky": False
        }

    def reset(self) -> None:
        """Resets all transient gesture states."""
        self.pinch_state = PinchState.IDLE
        self.current_gesture = GestureType.NONE
        self.palm_triggered = False
        self.sonar_triggered = False
        self.is_fist = False

    def update_fallback_mouse(self, mouse_x: int, mouse_y: int, lmb: bool, rmb: bool, space: bool, key_s: bool) -> dict:
        """
        Allows seamless mouse/keyboard fallback controls.
        LMB = Pinch, RMB = Sonar, Space = Water Current, 'S' = Fist/Shield.
        """
        now = time.time()
        # Direct snappy positioning for mouse
        self.cursor_x = float(mouse_x)
        self.cursor_y = float(mouse_y)

        pinch_event = False
        if lmb:
            if self.pinch_state == PinchState.IDLE and (now - self.last_pinch_time >= PINCH_COOLDOWN):
                self.pinch_state = PinchState.TRIGGERED
                self.last_pinch_time = now
                pinch_event = True
                self.current_gesture = GestureType.PINCH
            else:
                self.pinch_state = PinchState.PINCHED
        else:
            self.pinch_state = PinchState.IDLE

        sonar_event = False
        if rmb and (now - self.last_sonar_time >= TWO_FINGER_COOLDOWN):
            self.last_sonar_time = now
            sonar_event = True
            self.current_gesture = GestureType.TWO_FINGERS

        palm_event = False
        if space and (now - self.last_palm_time >= PALM_COOLDOWN):
            self.last_palm_time = now
            palm_event = True
            self.current_gesture = GestureType.OPEN_PALM

        self.is_fist = key_s
        if self.is_fist:
            self.current_gesture = GestureType.FIST
        elif not (lmb or rmb or space):
            self.current_gesture = GestureType.MOVE

        return {
            "cursor_pos": (int(self.cursor_x), int(self.cursor_y)),
            "current_gesture": self.current_gesture,
            "pinch_triggered": pinch_event,
            "palm_triggered": palm_event,
            "sonar_triggered": sonar_event,
            "shield_active": self.is_fist,
            "pinch_distance": 0.0 if lmb else 1.0,
            "palm_cooldown_pct": max(0.0, min(1.0, (now - self.last_palm_time) / PALM_COOLDOWN)),
            "sonar_cooldown_pct": max(0.0, min(1.0, (now - self.last_sonar_time) / TWO_FINGER_COOLDOWN)),
        }

    def maintain_position(self, lmb: bool, rmb: bool, space: bool, key_s: bool) -> dict:
        """Maintains current cursor coordinates smoothly without jumping to mouse."""
        now = time.time()
        pinch_event = False
        if lmb:
            if self.pinch_state == PinchState.IDLE and (now - self.last_pinch_time >= PINCH_COOLDOWN):
                self.pinch_state = PinchState.TRIGGERED
                self.last_pinch_time = now
                pinch_event = True
                self.current_gesture = GestureType.PINCH
            else:
                self.pinch_state = PinchState.PINCHED
        else:
            self.pinch_state = PinchState.IDLE

        sonar_event = False
        if rmb and (now - self.last_sonar_time >= TWO_FINGER_COOLDOWN):
            self.last_sonar_time = now
            sonar_event = True
            self.current_gesture = GestureType.TWO_FINGERS

        palm_event = False
        if space and (now - self.last_palm_time >= PALM_COOLDOWN):
            self.last_palm_time = now
            palm_event = True
            self.current_gesture = GestureType.OPEN_PALM

        self.is_fist = key_s
        if self.is_fist:
            self.current_gesture = GestureType.FIST
        elif not (lmb or rmb or space):
            self.current_gesture = GestureType.MOVE

        return {
            "cursor_pos": (int(self.cursor_x), int(self.cursor_y)),
            "current_gesture": self.current_gesture,
            "pinch_triggered": pinch_event,
            "palm_triggered": palm_event,
            "sonar_triggered": sonar_event,
            "shield_active": self.is_fist,
            "pinch_distance": 0.0 if lmb else 1.0,
            "palm_cooldown_pct": max(0.0, min(1.0, (now - self.last_palm_time) / PALM_COOLDOWN)),
            "sonar_cooldown_pct": max(0.0, min(1.0, (now - self.last_sonar_time) / TWO_FINGER_COOLDOWN)),
        }

    def process_landmarks(self, landmarks: List[Tuple[float, float, float]], raw_x: float, raw_y: float) -> dict:
        """
        Analyzes 21 MediaPipe hand landmarks and drives the gesture state machine.
        """
        now = time.time()
        if not landmarks or len(landmarks) < 21:
            self.current_gesture = GestureType.NONE
            return {
                "cursor_pos": (int(self.cursor_x), int(self.cursor_y)),
                "current_gesture": GestureType.NONE,
                "pinch_triggered": False,
                "palm_triggered": False,
                "sonar_triggered": False,
                "shield_active": False,
                "pinch_distance": 1.0,
                "palm_cooldown_pct": max(0.0, min(1.0, (now - self.last_palm_time) / PALM_COOLDOWN)),
                "sonar_cooldown_pct": max(0.0, min(1.0, (now - self.last_sonar_time) / TWO_FINGER_COOLDOWN)),
            }

        # 1. Position Smoothing with Deadzone Jitter Reduction
        dx = raw_x - self.cursor_x
        dy = raw_y - self.cursor_y
        dist = math.hypot(dx, dy)
        if dist > self.jitter_deadzone:
            # Dynamic alpha: high responsiveness for swift hand movement, smooth settling for fine pointing
            dyn_alpha = min(0.95, max(0.42, self.smoothing_alpha + (dist / 280.0) * 0.55))
            self.cursor_x += dx * dyn_alpha
            self.cursor_y += dy * dyn_alpha

        # 2. Extract Key Landmarks
        wrist = landmarks[0]
        thumb_cmc = landmarks[1]
        thumb_mcp = landmarks[2]
        thumb_ip = landmarks[3]
        thumb_tip = landmarks[4]

        index_mcp = landmarks[5]
        index_pip = landmarks[6]
        index_dip = landmarks[7]
        index_tip = landmarks[8]

        middle_mcp = landmarks[9]
        middle_pip = landmarks[10]
        middle_dip = landmarks[11]
        middle_tip = landmarks[12]

        ring_mcp = landmarks[13]
        ring_pip = landmarks[14]
        ring_dip = landmarks[15]
        ring_tip = landmarks[16]

        pinky_mcp = landmarks[17]
        pinky_pip = landmarks[18]
        pinky_dip = landmarks[19]
        pinky_tip = landmarks[20]

        # 3. Analyze Finger Extension States
        # A finger is extended if its tip is significantly farther from wrist than PIP/MCP
        def is_finger_extended(tip, pip, mcp):
            tip_dist = math.hypot(tip[0] - wrist[0], tip[1] - wrist[1])
            pip_dist = math.hypot(pip[0] - wrist[0], pip[1] - wrist[1])
            return tip_dist > pip_dist * 1.15

        self.extended_fingers["index"] = is_finger_extended(index_tip, index_pip, index_mcp)
        self.extended_fingers["middle"] = is_finger_extended(middle_tip, middle_pip, middle_mcp)
        self.extended_fingers["ring"] = is_finger_extended(ring_tip, ring_pip, ring_mcp)
        self.extended_fingers["pinky"] = is_finger_extended(pinky_tip, pinky_pip, pinky_mcp)

        # Thumb extension: check distance from thumb tip to pinky MCP compared to thumb IP
        thumb_dist_pinky = math.hypot(thumb_tip[0] - pinky_mcp[0], thumb_tip[1] - pinky_mcp[1])
        thumb_ip_dist_pinky = math.hypot(thumb_ip[0] - pinky_mcp[0], thumb_ip[1] - pinky_mcp[1])
        self.extended_fingers["thumb"] = thumb_dist_pinky > thumb_ip_dist_pinky * 1.1

        num_extended = sum([
            self.extended_fingers["index"],
            self.extended_fingers["middle"],
            self.extended_fingers["ring"],
            self.extended_fingers["pinky"]
        ])

        # 4. Fist Check (Defensive Shield): All fingers curled
        self.is_fist = (num_extended == 0) and not self.extended_fingers["thumb"]

        # 5. Two Fingers (Sonar): Index & Middle extended, Ring & Pinky curled
        is_two_fingers = (
            self.extended_fingers["index"]
            and self.extended_fingers["middle"]
            and not self.extended_fingers["ring"]
            and not self.extended_fingers["pinky"]
            and not self.is_fist
        )

        sonar_event = False
        if is_two_fingers:
            if not self.sonar_triggered and (now - self.last_sonar_time >= TWO_FINGER_COOLDOWN):
                self.last_sonar_time = now
                self.sonar_triggered = True
                sonar_event = True
        else:
            self.sonar_triggered = False

        # 6. Open Palm (Water Current): 4 or 5 fingers extended, spread out
        is_open_palm = (num_extended >= 4)
        palm_event = False
        if is_open_palm:
            if not self.palm_triggered and (now - self.last_palm_time >= PALM_COOLDOWN):
                self.last_palm_time = now
                self.palm_triggered = True
                palm_event = True
        else:
            self.palm_triggered = False

        # 7. Click Detection: Supports BOTH Index Finger Tap & Index-Thumb Pinch
        # 7a. Index-Thumb Pinch Distance
        p_dx = thumb_tip[0] - index_tip[0]
        p_dy = thumb_tip[1] - index_tip[1]
        self.pinch_distance = math.hypot(p_dx, p_dy)

        # 7b. Index Finger Air Tap / Flexion Ratio
        # When pointing, index tip is extended far from MCP (ratio > 1.7)
        # When tapping/clicking, index finger bends down toward palm (ratio < INDEX_TAP_BEND_RATIO)
        index_tip_mcp = math.hypot(index_tip[0] - index_mcp[0], index_tip[1] - index_mcp[1])
        index_pip_mcp = math.hypot(index_pip[0] - index_mcp[0], index_pip[1] - index_mcp[1]) + 1e-6
        index_bend_ratio = index_tip_mcp / index_pip_mcp

        is_pinch = (self.pinch_distance < PINCH_THRESHOLD)
        is_index_tap = (index_bend_ratio < INDEX_TAP_BEND_RATIO) and not self.is_fist and not is_two_fingers and not is_open_palm

        is_click_active = is_pinch or is_index_tap

        pinch_event = False
        # State machine transition for click / pinch
        if is_click_active:
            if self.pinch_state == PinchState.IDLE:
                if (now - self.last_pinch_time) >= PINCH_COOLDOWN:
                    self.pinch_state = PinchState.TRIGGERED
                    self.last_pinch_time = now
                    pinch_event = True
                else:
                    self.pinch_state = PinchState.PINCHED
            elif self.pinch_state == PinchState.TRIGGERED:
                self.pinch_state = PinchState.PINCHED
        else:
            # Immediate, debounce-clean reset when finger unbends or pinch opens
            self.pinch_state = PinchState.IDLE

        # Determine Primary Continuous Gesture Label
        if pinch_event or self.pinch_state in (PinchState.PINCHED, PinchState.TRIGGERED):
            self.current_gesture = GestureType.PINCH
        elif is_two_fingers:
            self.current_gesture = GestureType.TWO_FINGERS
        elif is_open_palm:
            self.current_gesture = GestureType.OPEN_PALM
        elif self.is_fist:
            self.current_gesture = GestureType.FIST
        else:
            self.current_gesture = GestureType.MOVE

        palm_cooldown_pct = max(0.0, min(1.0, (now - self.last_palm_time) / PALM_COOLDOWN))
        sonar_cooldown_pct = max(0.0, min(1.0, (now - self.last_sonar_time) / TWO_FINGER_COOLDOWN))

        return {
            "cursor_pos": (int(self.cursor_x), int(self.cursor_y)),
            "current_gesture": self.current_gesture,
            "pinch_triggered": pinch_event,
            "palm_triggered": palm_event,
            "sonar_triggered": sonar_event,
            "shield_active": self.is_fist,
            "pinch_distance": self.pinch_distance,
            "palm_cooldown_pct": palm_cooldown_pct,
            "sonar_cooldown_pct": sonar_cooldown_pct,
            "extended_fingers": self.extended_fingers,
        }
