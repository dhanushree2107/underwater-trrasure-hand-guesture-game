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
    DUAL_HAND_SWIM_BOOST,
    DUAL_HAND_PADDLE_MAX_BOOST,
    DUAL_HAND_STROKE_THRESHOLD,
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
    Supports both single-hand and dual-hand swimming & cooperative gestures.
    """

    def __init__(self):
        # Smoothing & Position (Primary Hand / Right Hand)
        self.cursor_x: float = SCREEN_WIDTH / 2.0
        self.cursor_y: float = SCREEN_HEIGHT / 2.0
        self.target_x: float = SCREEN_WIDTH / 2.0
        self.target_y: float = SCREEN_HEIGHT / 2.0
        self.smoothing_alpha: float = SMOOTHING_ALPHA

        # Deadzone threshold in pixels to eradicate static jitter
        self.jitter_deadzone: float = 2.5

        # Primary Hand Gesture State Machine
        self.pinch_state: PinchState = PinchState.IDLE
        self.last_pinch_time: float = 0.0
        self.pinch_distance: float = 1.0

        self.last_palm_time: float = 0.0
        self.palm_triggered: bool = False

        self.last_sonar_time: float = 0.0
        self.sonar_triggered: bool = False

        self.is_fist: bool = False
        self.current_gesture: GestureType = GestureType.NONE

        # Diagnostics for Primary Hand
        self.extended_fingers: Dict[str, bool] = {
            "thumb": False,
            "index": False,
            "middle": False,
            "ring": False,
            "pinky": False
        }

        # Second Hand State Machine (for dual-hand tracking & dual-hand swimming)
        self.second_cursor_x: float = SCREEN_WIDTH / 2.0
        self.second_cursor_y: float = SCREEN_HEIGHT / 2.0
        self.second_pinch_state: PinchState = PinchState.IDLE
        self.second_last_pinch_time: float = 0.0
        self.second_pinch_distance: float = 1.0
        self.second_is_fist: bool = False
        self.second_current_gesture: GestureType = GestureType.NONE
        self.second_palm_triggered: bool = False
        self.second_sonar_triggered: bool = False
        self.second_last_palm_time: float = 0.0
        self.second_last_sonar_time: float = 0.0
        self.second_extended_fingers: Dict[str, bool] = {
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

        self.second_pinch_state = PinchState.IDLE
        self.second_current_gesture = GestureType.NONE
        self.second_palm_triggered = False
        self.second_sonar_triggered = False
        self.second_is_fist = False

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

    def _analyze_landmarks_features(self, landmarks: List[Tuple[float, float, float]]) -> dict:
        """Extracts finger extension states, gestures, and tap/pinch metrics from 21 landmarks."""
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

        def is_finger_extended(tip, pip, mcp):
            tip_dist = math.hypot(tip[0] - wrist[0], tip[1] - wrist[1])
            pip_dist = math.hypot(pip[0] - wrist[0], pip[1] - wrist[1])
            return tip_dist > pip_dist * 1.15

        ext_index = is_finger_extended(index_tip, index_pip, index_mcp)
        ext_middle = is_finger_extended(middle_tip, middle_pip, middle_mcp)
        ext_ring = is_finger_extended(ring_tip, ring_pip, ring_mcp)
        ext_pinky = is_finger_extended(pinky_tip, pinky_pip, pinky_mcp)

        thumb_dist_pinky = math.hypot(thumb_tip[0] - pinky_mcp[0], thumb_tip[1] - pinky_mcp[1])
        thumb_ip_dist_pinky = math.hypot(thumb_ip[0] - pinky_mcp[0], thumb_ip[1] - pinky_mcp[1])
        ext_thumb = thumb_dist_pinky > thumb_ip_dist_pinky * 1.1

        num_extended = sum([ext_index, ext_middle, ext_ring, ext_pinky])
        is_fist = (num_extended == 0) and not ext_thumb
        is_two_fingers = (ext_index and ext_middle and not ext_ring and not ext_pinky and not is_fist)
        is_open_palm = (num_extended >= 4)

        p_dx = thumb_tip[0] - index_tip[0]
        p_dy = thumb_tip[1] - index_tip[1]
        pinch_dist = math.hypot(p_dx, p_dy)

        index_tip_mcp = math.hypot(index_tip[0] - index_mcp[0], index_tip[1] - index_mcp[1])
        index_pip_mcp = math.hypot(index_pip[0] - index_mcp[0], index_pip[1] - index_mcp[1]) + 1e-6
        index_bend_ratio = index_tip_mcp / index_pip_mcp

        is_pinch = (pinch_dist < PINCH_THRESHOLD)
        is_index_tap = (index_bend_ratio < INDEX_TAP_BEND_RATIO) and not is_fist and not is_two_fingers and not is_open_palm
        is_click_active = is_pinch or is_index_tap

        return {
            "extended_fingers": {
                "thumb": ext_thumb,
                "index": ext_index,
                "middle": ext_middle,
                "ring": ext_ring,
                "pinky": ext_pinky,
            },
            "is_fist": is_fist,
            "is_two_fingers": is_two_fingers,
            "is_open_palm": is_open_palm,
            "pinch_distance": pinch_dist,
            "is_click_active": is_click_active,
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
            dyn_alpha = min(0.95, max(0.42, self.smoothing_alpha + (dist / 280.0) * 0.55))
            self.cursor_x += dx * dyn_alpha
            self.cursor_y += dy * dyn_alpha

        # 2. Extract and analyze features
        features = self._analyze_landmarks_features(landmarks)
        self.extended_fingers = features["extended_fingers"]
        self.is_fist = features["is_fist"]
        self.pinch_distance = features["pinch_distance"]

        # 3. Sonar detection
        sonar_event = False
        if features["is_two_fingers"]:
            if not self.sonar_triggered and (now - self.last_sonar_time >= TWO_FINGER_COOLDOWN):
                self.last_sonar_time = now
                self.sonar_triggered = True
                sonar_event = True
        else:
            self.sonar_triggered = False

        # 4. Open Palm detection
        palm_event = False
        if features["is_open_palm"]:
            if not self.palm_triggered and (now - self.last_palm_time >= PALM_COOLDOWN):
                self.last_palm_time = now
                self.palm_triggered = True
                palm_event = True
        else:
            self.palm_triggered = False

        # 5. Click / Pinch state machine
        pinch_event = False
        if features["is_click_active"]:
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
            self.pinch_state = PinchState.IDLE

        # 6. Current gesture label
        if pinch_event or self.pinch_state in (PinchState.PINCHED, PinchState.TRIGGERED):
            self.current_gesture = GestureType.PINCH
        elif features["is_two_fingers"]:
            self.current_gesture = GestureType.TWO_FINGERS
        elif features["is_open_palm"]:
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

    def process_dual_landmarks(
        self,
        hand1_landmarks: List[Tuple[float, float, float]],
        hand1_x: float,
        hand1_y: float,
        hand1_label: str = "Right",
        hand2_landmarks: Optional[List[Tuple[float, float, float]]] = None,
        hand2_x: Optional[float] = None,
        hand2_y: Optional[float] = None,
        hand2_label: str = "Left",
        swim_target_x: Optional[float] = None,
        swim_target_y: Optional[float] = None,
        paddle_speed: float = 0.0,
    ) -> dict:
        """
        Coordinates dual-hand tracking, swimming navigation, and cooperative gestures.
        Allows either hand to pinch/grab, shield, or fire sonar, and coordinates two-hand swimming.
        """
        now = time.time()
        
        # 1. Smooth Hand 1 position
        dx1 = hand1_x - self.cursor_x
        dy1 = hand1_y - self.cursor_y
        dist1 = math.hypot(dx1, dy1)
        if dist1 > self.jitter_deadzone:
            dyn_alpha1 = min(0.95, max(0.42, self.smoothing_alpha + (dist1 / 280.0) * 0.55))
            self.cursor_x += dx1 * dyn_alpha1
            self.cursor_y += dy1 * dyn_alpha1

        # 2. Analyze Hand 1 features & gestures
        feat1 = self._analyze_landmarks_features(hand1_landmarks)
        self.extended_fingers = feat1["extended_fingers"]
        self.is_fist = feat1["is_fist"]
        self.pinch_distance = feat1["pinch_distance"]

        # Hand 1 Sonar
        sonar_1 = False
        if feat1["is_two_fingers"]:
            if not self.sonar_triggered and (now - self.last_sonar_time >= TWO_FINGER_COOLDOWN):
                self.last_sonar_time = now
                self.sonar_triggered = True
                sonar_1 = True
        else:
            self.sonar_triggered = False

        # Hand 1 Palm
        palm_1 = False
        if feat1["is_open_palm"]:
            if not self.palm_triggered and (now - self.last_palm_time >= PALM_COOLDOWN):
                self.last_palm_time = now
                self.palm_triggered = True
                palm_1 = True
        else:
            self.palm_triggered = False

        # Hand 1 Click / Pinch state machine
        pinch_1 = False
        if feat1["is_click_active"]:
            if self.pinch_state == PinchState.IDLE:
                if (now - self.last_pinch_time) >= PINCH_COOLDOWN:
                    self.pinch_state = PinchState.TRIGGERED
                    self.last_pinch_time = now
                    pinch_1 = True
                else:
                    self.pinch_state = PinchState.PINCHED
            elif self.pinch_state == PinchState.TRIGGERED:
                self.pinch_state = PinchState.PINCHED
        else:
            self.pinch_state = PinchState.IDLE

        # Hand 1 label
        if pinch_1 or self.pinch_state in (PinchState.PINCHED, PinchState.TRIGGERED):
            self.current_gesture = GestureType.PINCH
        elif feat1["is_two_fingers"]:
            self.current_gesture = GestureType.TWO_FINGERS
        elif feat1["is_open_palm"]:
            self.current_gesture = GestureType.OPEN_PALM
        elif self.is_fist:
            self.current_gesture = GestureType.FIST
        else:
            self.current_gesture = GestureType.MOVE

        # Process Hand 2 if present
        has_dual = False
        pinch_2 = False
        palm_2 = False
        sonar_2 = False
        fist_2 = False

        if hand2_landmarks and len(hand2_landmarks) >= 21 and hand2_x is not None and hand2_y is not None:
            has_dual = True
            dx2 = hand2_x - self.second_cursor_x
            dy2 = hand2_y - self.second_cursor_y
            dist2 = math.hypot(dx2, dy2)
            if dist2 > self.jitter_deadzone:
                dyn_alpha2 = min(0.95, max(0.42, self.smoothing_alpha + (dist2 / 280.0) * 0.55))
                self.second_cursor_x += dx2 * dyn_alpha2
                self.second_cursor_y += dy2 * dyn_alpha2

            feat2 = self._analyze_landmarks_features(hand2_landmarks)
            self.second_extended_fingers = feat2["extended_fingers"]
            self.second_is_fist = feat2["is_fist"]
            self.second_pinch_distance = feat2["pinch_distance"]
            fist_2 = self.second_is_fist

            # Hand 2 Sonar
            if feat2["is_two_fingers"]:
                if not self.second_sonar_triggered and (now - self.second_last_sonar_time >= TWO_FINGER_COOLDOWN):
                    self.second_last_sonar_time = now
                    self.second_sonar_triggered = True
                    sonar_2 = True
            else:
                self.second_sonar_triggered = False

            # Hand 2 Palm
            if feat2["is_open_palm"]:
                if not self.second_palm_triggered and (now - self.second_last_palm_time >= PALM_COOLDOWN):
                    self.second_last_palm_time = now
                    self.second_palm_triggered = True
                    palm_2 = True
            else:
                self.second_palm_triggered = False

            # Hand 2 Click / Pinch
            if feat2["is_click_active"]:
                if self.second_pinch_state == PinchState.IDLE:
                    if (now - self.second_last_pinch_time) >= PINCH_COOLDOWN:
                        self.second_pinch_state = PinchState.TRIGGERED
                        self.second_last_pinch_time = now
                        pinch_2 = True
                    else:
                        self.second_pinch_state = PinchState.PINCHED
                elif self.second_pinch_state == PinchState.TRIGGERED:
                    self.second_pinch_state = PinchState.PINCHED
            else:
                self.second_pinch_state = PinchState.IDLE

            # Hand 2 Gesture label
            if pinch_2 or self.second_pinch_state in (PinchState.PINCHED, PinchState.TRIGGERED):
                self.second_current_gesture = GestureType.PINCH
            elif feat2["is_two_fingers"]:
                self.second_current_gesture = GestureType.TWO_FINGERS
            elif feat2["is_open_palm"]:
                self.second_current_gesture = GestureType.OPEN_PALM
            elif self.second_is_fist:
                self.second_current_gesture = GestureType.FIST
            else:
                self.second_current_gesture = GestureType.MOVE

        # Combined Gesture Logic
        combined_pinch = pinch_1 or pinch_2
        combined_is_pinching = (self.pinch_state in (PinchState.PINCHED, PinchState.TRIGGERED)) or (self.second_pinch_state in (PinchState.PINCHED, PinchState.TRIGGERED))
        combined_shield = self.is_fist or fist_2
        combined_sonar = sonar_1 or sonar_2
        combined_palm = palm_1 or palm_2
        is_mega_palm = (self.current_gesture == GestureType.OPEN_PALM and self.second_current_gesture == GestureType.OPEN_PALM)

        # Dual-hand Swimming Navigation target
        if has_dual:
            mid_x = (self.cursor_x + self.second_cursor_x) / 2.0
            mid_y = (self.cursor_y + self.second_cursor_y) / 2.0
            
            # If one hand is actively grabbing/pinching, prioritize that hand for picking up
            if self.pinch_state in (PinchState.PINCHED, PinchState.TRIGGERED):
                active_pos = (int(self.cursor_x), int(self.cursor_y))
            elif self.second_pinch_state in (PinchState.PINCHED, PinchState.TRIGGERED):
                active_pos = (int(self.second_cursor_x), int(self.second_cursor_y))
            else:
                # Default swimming navigation guides towards dual-hand midpoint!
                active_pos = (int(mid_x), int(mid_y))

            paddle_boost = min(DUAL_HAND_PADDLE_MAX_BOOST, max(DUAL_HAND_SWIM_BOOST, DUAL_HAND_SWIM_BOOST + (paddle_speed / 300.0) * 0.5))
        else:
            active_pos = (int(self.cursor_x), int(self.cursor_y))
            paddle_boost = 1.0

        return {
            "cursor_pos": active_pos,
            "current_gesture": self.current_gesture,
            "pinch_triggered": combined_pinch,
            "is_pinching": combined_is_pinching,
            "palm_triggered": combined_palm,
            "sonar_triggered": combined_sonar,
            "shield_active": combined_shield,
            "is_mega_palm": is_mega_palm,
            "has_dual_hands": has_dual,
            "is_dual_hand_swimming": has_dual,
            "paddle_boost": paddle_boost,
            "first_cursor_pos": (int(self.cursor_x), int(self.cursor_y)),
            "second_cursor_pos": (int(self.second_cursor_x), int(self.second_cursor_y)) if has_dual else None,
            "first_gesture": self.current_gesture,
            "second_gesture": self.second_current_gesture if has_dual else GestureType.NONE,
            "first_label": hand1_label,
            "second_label": hand2_label,
            "pinch_distance": min(self.pinch_distance, self.second_pinch_distance if has_dual else self.pinch_distance),
            "palm_cooldown_pct": max(0.0, min(1.0, (now - self.last_palm_time) / PALM_COOLDOWN)),
            "sonar_cooldown_pct": max(0.0, min(1.0, (now - self.last_sonar_time) / TWO_FINGER_COOLDOWN)),
            "extended_fingers": self.extended_fingers,
        }
