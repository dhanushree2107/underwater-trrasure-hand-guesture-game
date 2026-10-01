"""
Underwater Treasure Hunt - Two-Hand Motion & Swimming Dynamics Tracker
Calculates real-time movement velocities, rhythmic stroke detection,
vector alignment, swim synchronization levels, and combo swim triggers.
"""

from collections import deque
from dataclasses import dataclass
from enum import Enum
import math
import time
from typing import Deque, List, Optional, Tuple

from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    DUAL_HAND_SWIM_BOOST,
    DUAL_HAND_PADDLE_MAX_BOOST,
    DUAL_HAND_STROKE_THRESHOLD,
)

class SwimTrackingStatus(Enum):
    TWO_HANDS = "TWO_HANDS"               # Optimal dual-hand swimming
    ONE_HAND = "ONE_HAND"                 # Single hand warning
    NO_HANDS = "NO_HANDS"                 # Paused / hands absent
    LOW_CONFIDENCE = "LOW_CONFIDENCE"     # Obscured hands


@dataclass
class HandMotionSnapshot:
    """A point-in-time spatial snapshot of an individual hand."""
    timestamp: float
    wrist_x: float
    wrist_y: float
    palm_x: float
    palm_y: float
    confidence: float


@dataclass
class DualSwimMotionResult:
    """Calculated swimming vectors and metrics across both hands."""
    status: SwimTrackingStatus
    status_message: str
    left_velocity: Tuple[float, float]
    right_velocity: Tuple[float, float]
    combined_vector: Tuple[float, float]
    motion_intensity: float            # Combined movement speed in px/s
    sync_level: float                  # 0.0 to 1.0 (0% to 100% synchronization)
    is_synchronized: bool
    is_combo_swim: bool                # Rhythmic synchronized stroke combo
    combo_mult: float                  # Speed multiplier (1.0 - 2.0x)
    turning_torque: float              # Rotational steering torque when hands move inversely
    left_confidence: float
    right_confidence: float
    direction_label: str               # "IDLE", "SWIM LEFT", "SWIM RIGHT", "SWIM UP", "SWIM DOWN", "FORWARD PROPULSION"


class HandMotionTracker:
    """
    Analyzes temporal displacement of both hands over sliding time windows.
    Derives realistic swimming propulsion, opposite-hand turning, and rhythmic combo boosts.
    """

    def __init__(self, history_len: int = 15):
        self.history_len = history_len
        self.left_history: Deque[HandMotionSnapshot] = deque(maxlen=history_len)
        self.right_history: Deque[HandMotionSnapshot] = deque(maxlen=history_len)
        
        # Smoothed motion state
        self.smoothed_left_vx: float = 0.0
        self.smoothed_left_vy: float = 0.0
        self.smoothed_right_vx: float = 0.0
        self.smoothed_right_vy: float = 0.0
        self.smoothed_combined_vx: float = 0.0
        self.smoothed_combined_vy: float = 0.0

        # Rhythmic stroke & synchronization dynamics
        self.sync_score: float = 0.85
        self.combo_timer: float = 0.0
        self.is_combo_active: bool = False
        self.last_stroke_time: float = 0.0
        self.stroke_cycle_count: int = 0
        self.prev_motion_dir_x: float = 0.0
        self.prev_motion_dir_y: float = 0.0

        # Dead zones and filters
        self.min_velocity_threshold: float = 25.0   # Pixels/sec to register deliberate motion
        self.max_velocity_cap: float = 1400.0       # Clamp extreme jitter

    def reset(self) -> None:
        """Clears history buffers on level start or calibration reset."""
        self.left_history.clear()
        self.right_history.clear()
        self.smoothed_left_vx = 0.0
        self.smoothed_left_vy = 0.0
        self.smoothed_right_vx = 0.0
        self.smoothed_right_vy = 0.0
        self.smoothed_combined_vx = 0.0
        self.smoothed_combined_vy = 0.0
        self.sync_score = 0.85
        self.combo_timer = 0.0
        self.is_combo_active = False
        self.last_stroke_time = 0.0
        self.stroke_cycle_count = 0

    def record_frame(
        self,
        now: float,
        left_data: Optional[Tuple[float, float, float, float, float]],
        right_data: Optional[Tuple[float, float, float, float, float]],
    ) -> None:
        """
        Records spatial coordinates for the current frame.
        left_data/right_data format: (wrist_x, wrist_y, palm_x, palm_y, confidence)
        """
        if left_data is not None:
            wx, wy, px, py, conf = left_data
            self.left_history.append(HandMotionSnapshot(now, wx, wy, px, py, conf))
        if right_data is not None:
            wx, wy, px, py, conf = right_data
            self.right_history.append(HandMotionSnapshot(now, wx, wy, px, py, conf))

    def _calc_velocity(self, history: Deque[HandMotionSnapshot]) -> Tuple[float, float, float]:
        """Calculates smoothed velocity (vx, vy, confidence) from snapshot history."""
        if len(history) < 2:
            return 0.0, 0.0, 0.0

        p_new = history[-1]
        p_old = history[0]
        dt = p_new.timestamp - p_old.timestamp
        if dt <= 0.005:
            return 0.0, 0.0, p_new.confidence

        vx = (p_new.palm_x - p_old.palm_x) / dt
        vy = (p_new.palm_y - p_old.palm_y) / dt

        # Cap velocity to avoid camera glitch spikes
        speed = math.hypot(vx, vy)
        if speed > self.max_velocity_cap:
            scale = self.max_velocity_cap / speed
            vx *= scale
            vy *= scale

        # Deadzone filter
        if speed < self.min_velocity_threshold:
            vx = 0.0
            vy = 0.0

        avg_conf = sum(s.confidence for s in history) / len(history)
        return vx, vy, avg_conf

    def update(self, dt: float) -> DualSwimMotionResult:
        """
        Calculates the combined swimming velocity, synchronization level,
        opposite-hand turning moments, and combo propulsion boost.
        """
        # 1. Decay combo timer
        if self.combo_timer > 0.0:
            self.combo_timer -= dt
            self.is_combo_active = (self.combo_timer > 0.0)
        else:
            self.is_combo_active = False

        # 2. Extract raw hand velocities
        raw_lvx, raw_lvy, l_conf = self._calc_velocity(self.left_history)
        raw_rvx, raw_rvy, r_conf = self._calc_velocity(self.right_history)

        has_left = len(self.left_history) >= 2 and l_conf > 0.35
        has_right = len(self.right_history) >= 2 and r_conf > 0.35

        # 3. Determine Tracking Status
        if has_left and has_right:
            if l_conf < 0.55 or r_conf < 0.55:
                status = SwimTrackingStatus.LOW_CONFIDENCE
                status_msg = "IMPROVE HAND VISIBILITY 💡"
            else:
                status = SwimTrackingStatus.TWO_HANDS
                status_msg = "DUAL-HAND SWIMMING ACTIVE 🏊"
        elif has_left or has_right:
            status = SwimTrackingStatus.ONE_HAND
            status_msg = "TWO HANDS REQUIRED FOR FULL PROPULSION 👐"
        else:
            status = SwimTrackingStatus.NO_HANDS
            status_msg = "HANDS NOT DETECTED (PAUSED) ✋"

        # 4. Smooth hand velocities with low-pass filter
        alpha = min(1.0, 14.0 * dt)
        self.smoothed_left_vx += (raw_lvx - self.smoothed_left_vx) * alpha
        self.smoothed_left_vy += (raw_lvy - self.smoothed_left_vy) * alpha
        self.smoothed_right_vx += (raw_rvx - self.smoothed_right_vx) * alpha
        self.smoothed_right_vy += (raw_rvy - self.smoothed_right_vy) * alpha

        lvx, lvy = self.smoothed_left_vx, self.smoothed_left_vy
        rvx, rvy = self.smoothed_right_vx, self.smoothed_right_vy

        # 5. Combined Swim Vector & Turning Dynamics
        if status in (SwimTrackingStatus.TWO_HANDS, SwimTrackingStatus.LOW_CONFIDENCE):
            # Weighted average vector
            comb_vx = (lvx + rvx) * 0.5
            comb_vy = (lvy + rvy) * 0.5

            # Calculate direction alignment (dot product of normalized velocity vectors)
            l_mag = math.hypot(lvx, lvy)
            r_mag = math.hypot(rvx, rvy)

            if l_mag > 30.0 and r_mag > 30.0:
                dot = (lvx * rvx + lvy * rvy) / (l_mag * r_mag)
                instant_sync = max(0.0, min(1.0, (dot + 1.0) / 2.0))
                # Smooth synchronization score
                self.sync_score += (instant_sync - self.sync_score) * min(1.0, 6.0 * dt)

                # Rhythmic stroke reversal detection (e.g. left-right paddle strokes or breaststroke sweep)
                cur_dir_x = (lvx + rvx) / (l_mag + r_mag)
                if self.prev_motion_dir_x != 0.0 and (cur_dir_x * self.prev_motion_dir_x < -0.3):
                    now = time.time()
                    if (now - self.last_stroke_time) < 1.1:
                        self.stroke_cycle_count += 1
                        if self.stroke_cycle_count >= 2:
                            self.combo_timer = 2.4  # Trigger COMBO SWIM boost
                            self.is_combo_active = True
                            self.stroke_cycle_count = 0
                    self.last_stroke_time = now
                self.prev_motion_dir_x = cur_dir_x
            else:
                # Idle decay
                self.sync_score += (0.75 - self.sync_score) * min(1.0, 2.0 * dt)

            # Turning torque: if left hand moves forward/up and right moves back/down
            turning_torque = (rvy - lvy) * 0.002 + (rvx - lvx) * 0.001

        elif status == SwimTrackingStatus.ONE_HAND:
            # Degraded single-hand swimming (reduced control)
            if has_left:
                comb_vx = lvx * 0.45
                comb_vy = lvy * 0.45
            else:
                comb_vx = rvx * 0.45
                comb_vy = rvy * 0.45
            self.sync_score = 0.35
            turning_torque = 0.0
        else:
            # Hands missing: gradual deceleration to stop
            comb_vx = 0.0
            comb_vy = 0.0
            self.sync_score = 0.0
            turning_torque = 0.0

        # Smooth combined vector
        self.smoothed_combined_vx += (comb_vx - self.smoothed_combined_vx) * alpha
        self.smoothed_combined_vy += (comb_vy - self.smoothed_combined_vy) * alpha

        comb_speed = math.hypot(self.smoothed_combined_vx, self.smoothed_combined_vy)

        # 6. Combo propulsion multiplier
        combo_mult = 1.0
        if status in (SwimTrackingStatus.TWO_HANDS, SwimTrackingStatus.LOW_CONFIDENCE):
            sync_boost = 1.0 + (self.sync_score - 0.5) * 0.5  # up to 1.25x for high sync
            combo_boost = 1.45 if self.is_combo_active else 1.0
            paddle_boost = 1.0 + min(0.4, comb_speed / 1200.0)
            combo_mult = min(2.0, sync_boost * combo_boost * paddle_boost)

        # 7. Directional Human-Readable Label
        if comb_speed < 45.0:
            dir_label = "IDLE GLIDE"
        elif abs(self.smoothed_combined_vx) > abs(self.smoothed_combined_vy) * 1.3:
            dir_label = "SWIM RIGHT ⏩" if self.smoothed_combined_vx > 0 else "SWIM LEFT ⏪"
        elif abs(self.smoothed_combined_vy) > abs(self.smoothed_combined_vx) * 1.3:
            dir_label = "SWIM DOWN ⏬" if self.smoothed_combined_vy > 0 else "SWIM UP ⏫"
        else:
            dir_label = "FORWARD PROPULSION 🏊"

        return DualSwimMotionResult(
            status=status,
            status_message=status_msg,
            left_velocity=(self.smoothed_left_vx, self.smoothed_left_vy),
            right_velocity=(self.smoothed_right_vx, self.smoothed_right_vy),
            combined_vector=(self.smoothed_combined_vx, self.smoothed_combined_vy),
            motion_intensity=comb_speed,
            sync_level=self.sync_score,
            is_synchronized=(self.sync_score >= 0.70),
            is_combo_swim=self.is_combo_active,
            combo_mult=combo_mult,
            turning_torque=turning_torque,
            left_confidence=l_conf if has_left else 0.0,
            right_confidence=r_conf if has_right else 0.0,
            direction_label=dir_label,
        )
