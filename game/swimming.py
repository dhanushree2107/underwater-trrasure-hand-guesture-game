"""
Underwater Treasure Hunt - Realistic Virtual Swimming Physics Engine
Translates real-time two-hand motion vectors into hydrodynamically realistic
swimmer acceleration, momentum, fluid drag, opposite-hand turning, and glide kinematics.
"""

import math
from typing import Tuple

from config import (
    SWIMMER_SPEED,
    SWIMMER_ACCEL,
    SWIMMER_FRICTION,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)
from hand_tracking.hand_motion import DualSwimMotionResult, SwimTrackingStatus


class SwimPhysicsEngine:
    """
    Simulates underwater diver kinematics based on dual-hand motion vectors,
    fluid drag, swimming stroke rhythm, and directional propulsion.
    """

    def __init__(
        self,
        base_speed: float = SWIMMER_SPEED,
        acceleration: float = SWIMMER_ACCEL,
        water_drag: float = 0.88,
    ):
        self.base_speed = base_speed
        self.acceleration = acceleration
        self.water_drag = water_drag

        # Kinematic state
        self.vx: float = 0.0
        self.vy: float = 0.0
        self.swim_tilt_angle: float = 0.0
        self.fin_flutter_phase: float = 0.0
        self.is_moving: bool = False
        self.stroke_power: float = 1.0

        # Physical constraints
        self.margin_x: float = 55.0
        self.margin_top: float = 85.0
        self.margin_bottom: float = 65.0

    def reset(self) -> None:
        """Resets swimmer velocities."""
        self.vx = 0.0
        self.vy = 0.0
        self.swim_tilt_angle = 0.0
        self.fin_flutter_phase = 0.0
        self.is_moving = False
        self.stroke_power = 1.0

    def apply_motion(
        self,
        dt: float,
        current_x: float,
        current_y: float,
        motion_result: DualSwimMotionResult,
        target_midpoint: Tuple[float, float],
        current_force_x: float = 0.0,
    ) -> Tuple[float, float, float, float, bool]:
        """
        Integrates dual-hand motion vectors and target steering into new coordinates.
        Returns: (new_x, new_y, new_vx, new_vy, is_fluttering)
        """
        status = motion_result.status

        # 1. Determine target displacement direction
        tx, ty = target_midpoint
        dx = tx - current_x
        dy = ty - current_y
        dist_to_target = math.hypot(dx, dy)

        if dist_to_target > 4.0:
            dir_x = dx / dist_to_target
            dir_y = dy / dist_to_target
        else:
            dir_x = 0.0
            dir_y = 0.0

        # 2. Derive swimming drive force
        # Hand motion velocity vector contributes directly to propulsion direction & intensity
        mv_x, mv_y = motion_result.combined_vector
        motion_speed = motion_result.motion_intensity

        if status == SwimTrackingStatus.TWO_HANDS or status == SwimTrackingStatus.LOW_CONFIDENCE:
            # Full dual-hand swimming mechanics
            propulsion_mult = motion_result.combo_mult
            
            # Combine target seeking with hand velocity impulses
            base_drive = min(1600.0, max(self.base_speed, dist_to_target * 5.5))
            hand_motion_boost = min(600.0, motion_speed * 0.75)
            effective_speed = (base_drive + hand_motion_boost) * propulsion_mult

            target_vx = dir_x * effective_speed
            target_vy = dir_y * effective_speed

            # Incorporate direct hand stroke vector
            if motion_speed > 40.0:
                target_vx += mv_x * 0.4
                target_vy += mv_y * 0.4

            # Agile fluid acceleration
            accel_rate = 26.0 * dt
            self.vx += (target_vx - self.vx) * min(1.0, accel_rate)
            self.vy += (target_vy - self.vy) * min(1.0, accel_rate)

            # High distance catch-up assist
            if dist_to_target > 320.0:
                current_x += dir_x * min(dist_to_target - 320.0, 700.0 * dt)
                current_y += dir_y * min(dist_to_target - 320.0, 700.0 * dt)

            self.is_moving = (dist_to_target > 8.0 or motion_speed > 35.0)

        elif status == SwimTrackingStatus.ONE_HAND:
            # Single-hand penalty: slower swimming, half acceleration
            target_vx = dir_x * (self.base_speed * 0.55)
            target_vy = dir_y * (self.base_speed * 0.55)
            accel_rate = 14.0 * dt
            self.vx += (target_vx - self.vx) * min(1.0, accel_rate)
            self.vy += (target_vy - self.vy) * min(1.0, accel_rate)
            self.is_moving = (dist_to_target > 10.0)

        else:
            # No hands detected: gradual momentum gliding to safe halt
            drag_factor = self.water_drag ** (dt * 60.0)
            self.vx *= drag_factor
            self.vy *= drag_factor
            self.is_moving = False

        # 3. Ambient water current drift
        if current_force_x != 0.0:
            self.vx += current_force_x * 0.6 * dt

        # 4. Integrate velocities into spatial position
        new_x = current_x + self.vx * dt
        new_y = current_y + self.vy * dt

        # 5. Boundary clamping
        new_x = max(self.margin_x, min(SCREEN_WIDTH - self.margin_x, new_x))
        new_y = max(self.margin_top, min(SCREEN_HEIGHT - self.margin_bottom, new_y))

        # 6. Swimmer tilt & fin flutter kinematics
        speed = math.hypot(self.vx, self.vy)
        if speed > 20.0:
            target_tilt = math.atan2(self.vy, abs(self.vx) + 1e-4) * 0.42
            # Add turning torque tilt from opposite hand motion
            target_tilt += motion_result.turning_torque * 0.25
            self.swim_tilt_angle += (target_tilt - self.swim_tilt_angle) * min(1.0, 15.0 * dt)
            self.fin_flutter_phase += speed * 0.045 * (1.5 if motion_result.is_combo_swim else 1.0) * dt
        else:
            self.swim_tilt_angle *= (0.80 ** (dt * 60.0))
            self.fin_flutter_phase += 2.5 * dt

        return new_x, new_y, self.vx, self.vy, self.is_moving
