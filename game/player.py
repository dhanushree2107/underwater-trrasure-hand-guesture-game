"""
Underwater Treasure Hunt - Underwater Swimmer & Explorer System
The player physically controls an underwater scuba diver exploring the abyss.
Features swimming physics, fin flutter kinematics, dynamic pitch tilting,
headlight beam, carried treasure mechanics, oxygen reserves, and shield forcefields.
"""

import math
import random
import time
from typing import Optional, Tuple
import pygame

from config import (
    INITIAL_OXYGEN,
    PASSIVE_OXYGEN_DEPLETION_RATE,
    SONAR_INITIAL_CHARGES,
    WATER_CURRENT_DURATION,
    SWIMMER_SPEED,
    SWIMMER_ACCEL,
    SWIMMER_FRICTION,
    COLOR_OCEAN_CYAN,
    COLOR_NEON_TEAL,
    COLOR_GOLD,
    COLOR_EMERALD,
    COLOR_CORAL_RED,
    COLOR_AMBER_WARNING,
    COLOR_WHITE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)

class Player:
    """The underwater explorer swimmer character controlled via hand gestures."""

    def __init__(self):
        # Kinematics & Position
        self.x: float = SCREEN_WIDTH / 2.0
        self.y: float = SCREEN_HEIGHT / 2.0
        self.vx: float = 0.0
        self.vy: float = 0.0
        self.facing_right: bool = True
        self.swim_angle: float = 0.0
        self.fin_flutter: float = 0.0
        self.speed: float = SWIMMER_SPEED

        # Vitals & Equipment
        self.oxygen: float = INITIAL_OXYGEN
        self.display_oxygen: float = INITIAL_OXYGEN
        self.lives: int = 3
        self.max_lives: int = 3
        self.invulnerability_timer: float = 0.0
        self.arm_stroke_phase: float = 0.0
        self.score: int = 0
        self.level_score: int = 0
        self.sonar_charges: int = SONAR_INITIAL_CHARGES
        
        # Action timers
        self.current_active_timer: float = 0.0
        self.screen_shake_timer: float = 0.0
        self.screen_shake_intensity: float = 0.0
        self.bubble_exhaust_timer: float = 0.0

        # Treasure Carrying State
        self.carried_treasure = None  # Reference to Treasure object being carried

        # Interaction & Swimmer Visuals
        self.is_hovering_interactable: bool = False
        self.is_hovering_danger: bool = False
        self.is_hovering_chest: bool = False
        self.is_pinching: bool = False
        self.pinch_anim_scale: float = 1.0
        self.shield_active: bool = False
        self.pulse_phase: float = 0.0

        # Dual-hand Swimming State
        self.is_dual_hand_swimming: bool = False
        self.paddle_boost: float = 1.0
        self.dual_swim_wake_phase: float = 0.0

    def reset_for_level(self) -> None:
        """Resets oxygen, charges, and carried items when embarking on a level."""
        self.oxygen = INITIAL_OXYGEN
        self.display_oxygen = INITIAL_OXYGEN
        self.invulnerability_timer = 0.0
        self.sonar_charges = SONAR_INITIAL_CHARGES
        self.current_active_timer = 0.0
        self.level_score = 0
        self.screen_shake_timer = 0.0
        self.carried_treasure = None
        self.is_dual_hand_swimming = False
        self.paddle_boost = 1.0
        self.dual_swim_wake_phase = 0.0
        self.vx = 0.0
        self.vy = 0.0

    def add_score(self, amount: int) -> None:
        """Adjusts score by given amount (can be positive or penalty)."""
        self.score = max(0, self.score + amount)
        self.level_score = max(0, self.level_score + amount)

    def reduce_oxygen(self, penalty: float, shake_duration: float = 0.4, shake_power: float = 8.0) -> None:
        """Drains oxygen and triggers screen shake feedback."""
        self.oxygen = max(0.0, self.oxygen - penalty)
        self.trigger_screen_shake(shake_duration, shake_power)

    def lose_life(self) -> bool:
        """
        Drains 1 life upon major hazard collision (Shark, Trap, Guardian).
        Returns True if player is still alive, False if all 3 lives lost.
        """
        if self.invulnerability_timer > 0.0:
            return True

        self.lives = max(0, self.lives - 1)
        self.invulnerability_timer = 2.2  # 2.2 seconds grace period
        self.trigger_screen_shake(0.65, 14.0)
        self.reduce_oxygen(15.0)

        # Drop carried treasure on impact
        if self.carried_treasure:
            self.carried_treasure.drop(self.x, self.y)
            self.carried_treasure = None

        return self.lives > 0

    def trigger_screen_shake(self, duration: float = 0.4, intensity: float = 8.0) -> None:
        """Triggers an underwater rumble screen shake."""
        self.screen_shake_timer = duration
        self.screen_shake_intensity = intensity

    def activate_sonar(self) -> bool:
        """Attempts to consume a sonar charge. Returns True if successful."""
        if self.sonar_charges > 0:
            self.sonar_charges -= 1
            return True
        return False

    def activate_water_current(self) -> bool:
        """Activates directional water current if not already active."""
        if self.current_active_timer <= 0:
            self.current_active_timer = WATER_CURRENT_DURATION
            return True
        return False

    def grab_treasure(self, treasure) -> None:
        """Attaches a treasure to the swimmer's hands."""
        self.carried_treasure = treasure
        treasure.is_carried = True

    def release_carried_treasure(self):
        """Releases the carried treasure. Returns the released treasure object."""
        treasure = self.carried_treasure
        if treasure:
            treasure.is_carried = False
            self.carried_treasure = None
        return treasure

    def update(
        self,
        dt: float,
        target_x: float,
        target_y: float,
        is_pinching: bool,
        shield_active: bool,
        current_force_x: float = 0.0,
        is_dual_hand_swimming: bool = False,
        paddle_boost: float = 1.0,
    ) -> bool:
        """
        Updates swimmer kinematics, smooth acceleration, orientation, and vitals.
        Supports both single-hand guiding and high-propulsion dual-hand swimming.
        Returns True if a regulator bubble should be emitted.
        """
        self.is_pinching = is_pinching
        self.shield_active = shield_active
        self.is_dual_hand_swimming = is_dual_hand_swimming
        self.paddle_boost = paddle_boost
        self.pulse_phase += 4.5 * dt
        if self.invulnerability_timer > 0.0:
            self.invulnerability_timer = max(0.0, self.invulnerability_timer - dt)
        if is_dual_hand_swimming:
            self.dual_swim_wake_phase += 11.0 * dt
            self.arm_stroke_phase += 12.0 * dt
        else:
            self.arm_stroke_phase += 5.5 * dt

        # 1. Swimming Physics: Responsive, agile navigation towards hand target
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)

        # Smooth responsive velocity towards hand target
        if dist > 3.0:
            dir_x = dx / dist
            dir_y = dy / dist
            
            # Dynamic swim speed: scales aggressively with distance, augmented by dual-hand propulsion
            base_speed = min(1800.0, max(600.0, dist * 8.5))
            current_speed = base_speed * (self.paddle_boost if is_dual_hand_swimming else 1.0)
            target_vx = dir_x * current_speed
            target_vy = dir_y * current_speed
            
            # Ultra-agile acceleration towards target velocity (achieves full speed in ~25ms)
            self.vx += (target_vx - self.vx) * min(1.0, 32.0 * dt)
            self.vy += (target_vy - self.vy) * min(1.0, 32.0 * dt)

            # Responsive catch-up assist when hand whips across screen
            if dist > 300.0:
                self.x += dir_x * min(dist - 300.0, 750.0 * dt)
                self.y += dir_y * min(dist - 300.0, 750.0 * dt)
            
            # Orientation
            if abs(dx) > 10.0:
                self.facing_right = (dx > 0)
            
            # Pitch tilt based on vertical movement
            desired_tilt = math.atan2(self.vy, abs(self.vx) + 1e-4) * 0.45
            self.swim_angle += (desired_tilt - self.swim_angle) * min(1.0, 14.0 * dt)
            
            # Fin kick flutter speed scales with swimming speed and dual-hand stroke
            swim_speed = math.hypot(self.vx, self.vy)
            flutter_mult = 1.6 if is_dual_hand_swimming else 1.0
            self.fin_flutter += swim_speed * 0.045 * flutter_mult * dt
        else:
            # Idle glide deceleration
            self.vx *= (0.65 ** (dt * 60.0))
            self.vy *= (0.65 ** (dt * 60.0))
            self.swim_angle *= (0.75 ** (dt * 60.0))
            self.fin_flutter += 3.0 * dt

        # Water Current displacement
        if current_force_x != 0.0:
            self.vx += current_force_x * 0.5 * dt

        # Integrate velocity
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Boundary clamping within playable screen area
        self.x = max(45.0, min(SCREEN_WIDTH - 45.0, self.x))
        self.y = max(85.0, min(SCREEN_HEIGHT - 65.0, self.y))

        # 2. Update Carried Treasure position to follow swimmer's hands
        if self.carried_treasure:
            hand_offset_x = 36.0 if self.facing_right else -36.0
            hand_offset_y = 6.0
            self.carried_treasure.x = self.x + hand_offset_x
            self.carried_treasure.y = self.y + hand_offset_y

        # 3. Passive Oxygen Depletion
        self.oxygen = max(0.0, self.oxygen - (PASSIVE_OXYGEN_DEPLETION_RATE * dt))

        # Smooth Display Oxygen Bar Interpolation
        diff = self.oxygen - self.display_oxygen
        self.display_oxygen += diff * min(1.0, 8.0 * dt)

        # Active Water Current Timer
        if self.current_active_timer > 0:
            self.current_active_timer -= dt

        # Screen Shake Decay
        if self.screen_shake_timer > 0:
            self.screen_shake_timer -= dt

        # Pinch visual animation spring
        target_scale = 0.65 if is_pinching else 1.0
        self.pinch_anim_scale += (target_scale - self.pinch_anim_scale) * min(1.0, 16.0 * dt)

        # Scuba Regulator Bubble Exhaust Timer
        self.bubble_exhaust_timer += dt * (1.6 if is_dual_hand_swimming else 1.0)
        emit_bubble = False
        threshold = 0.45 if is_dual_hand_swimming else 0.75
        if self.bubble_exhaust_timer >= threshold:
            self.bubble_exhaust_timer = random.uniform(0.0, 0.15)
            emit_bubble = True

        return emit_bubble

    def get_screen_shake_offset(self) -> Tuple[int, int]:
        """Returns current (dx, dy) screen shake offset."""
        if self.screen_shake_timer <= 0:
            return (0, 0)
        decay = self.screen_shake_timer / 0.4
        power = self.screen_shake_intensity * decay
        return (int(random.uniform(-power, power)), int(random.uniform(-power, power)))

    def draw_swimmer(self, surface: pygame.Surface) -> None:
        """
        Renders the underwater scuba explorer character with swimming fins,
        scuba tank, glowing mask, flashlight beam, and carried treasure.
        """
        cx, cy = int(self.x), int(self.y)
        d = 1 if self.facing_right else -1
        tilt_deg = math.degrees(self.swim_angle) * (1 if self.facing_right else -1)
        fin_kick = math.sin(self.fin_flutter) * 10.0

        # 1. Swimmer Headlamp / Torch Beam (Volumetric Illumination)
        light_len = 160
        light_w = 70
        torch_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        torch_origin = (cx + d * 22, cy - 4)
        torch_poly = [
            torch_origin,
            (cx + d * light_len, cy - light_w // 2 + int(self.swim_angle * 80)),
            (cx + d * light_len, cy + light_w // 2 + int(self.swim_angle * 80)),
        ]
        pygame.draw.polygon(torch_surf, (220, 245, 255, 30), torch_poly)
        surface.blit(torch_surf, (0, 0))

        # 2. Forcefield Shield Dome (when Fist ✊ or 'S' key is held)
        if self.shield_active:
            shield_r = 52
            shield_surf = pygame.Surface((shield_r * 2 + 10, shield_r * 2 + 10), pygame.SRCALPHA)
            alpha = int(150 + 60 * math.sin(self.pulse_phase * 2.5))
            pygame.draw.circle(shield_surf, (*COLOR_NEON_TEAL[:3], alpha), (shield_r + 5, shield_r + 5), shield_r, 4)
            pygame.draw.circle(shield_surf, (*COLOR_WHITE[:3], int(alpha * 0.4)), (shield_r + 5, shield_r + 5), shield_r - 4)
            surface.blit(shield_surf, (cx - shield_r - 5, cy - shield_r - 5))

        # 3. Scuba Diver Character Sprite / Geometry
        # Diver Surface with Rotation support
        swimmer_surf = pygame.Surface((90, 70), pygame.SRCALPHA)
        scx, scy = 45, 35

        # Colors
        suit_dark = (18, 32, 54)
        suit_accent = COLOR_NEON_TEAL
        tank_color = (240, 200, 30)  # Yellow scuba air cylinder
        mask_glow = (80, 230, 255)
        skin_tone = (235, 185, 145)

        # Twin Swim Fins (fluttering back)
        fin_top_y = scy + 8 + int(fin_kick)
        fin_bot_y = scy + 16 - int(fin_kick)
        fin_poly_1 = [
            (scx - 22, scy + 10),
            (scx - 38, fin_top_y),
            (scx - 36, fin_top_y + 6),
            (scx - 20, scy + 12),
        ]
        fin_poly_2 = [
            (scx - 20, scy + 12),
            (scx - 38, fin_bot_y),
            (scx - 36, fin_bot_y + 6),
            (scx - 18, scy + 14),
        ]
        pygame.draw.polygon(swimmer_surf, (10, 80, 140), fin_poly_1)
        pygame.draw.polygon(swimmer_surf, (15, 105, 180), fin_poly_2)

        # Diver Legs & Wetsuit Torso
        pygame.draw.line(swimmer_surf, suit_dark, (scx, scy + 6), (scx - 20, scy + 11), 7)
        body_rect = pygame.Rect(scx - 14, scy - 8, 30, 18)
        pygame.draw.ellipse(swimmer_surf, suit_dark, body_rect)
        pygame.draw.ellipse(swimmer_surf, suit_accent, body_rect, width=2)

        # Scuba Air Cylinder (Tank on back)
        tank_rect = pygame.Rect(scx - 10, scy - 15, 20, 8)
        pygame.draw.rect(swimmer_surf, tank_color, tank_rect, border_radius=4)
        pygame.draw.rect(swimmer_surf, (40, 40, 40), (scx - 12, scy - 13, 3, 4)) # Valve

        # Diver Head & Mask Visor
        pygame.draw.circle(swimmer_surf, suit_dark, (scx + 15, scy - 2), 10)
        # Glowing Mask Visor
        mask_rect = pygame.Rect(scx + 17, scy - 6, 8, 7)
        pygame.draw.ellipse(swimmer_surf, mask_glow, mask_rect)
        pygame.draw.ellipse(swimmer_surf, COLOR_WHITE, mask_rect, width=1)

        # Arms (Reaching forward or dynamic swimming stroke)
        if self.carried_treasure:
            # Both hands clasping treasure in front
            pygame.draw.line(swimmer_surf, suit_dark, (scx + 8, scy + 2), (scx + 28, scy + 4), 5)
            pygame.draw.circle(swimmer_surf, skin_tone, (scx + 28, scy + 4), 3)
        else:
            # Free swimming stroke reacting dynamically to two-hand motion
            arm_cycle = math.sin(self.arm_stroke_phase) * 6.0
            arm_reach = 22.0 + math.cos(self.arm_stroke_phase) * 5.0
            pygame.draw.line(swimmer_surf, suit_dark, (scx + 6, scy + 2), (scx + int(arm_reach), scy + int(arm_cycle)), 4)
            pygame.draw.circle(swimmer_surf, skin_tone, (scx + int(arm_reach), scy + int(arm_cycle)), 3)

        # Flip horizontally if swimming left
        if not self.facing_right:
            swimmer_surf = pygame.transform.flip(swimmer_surf, True, False)

        # Invulnerability damage flash
        if self.invulnerability_timer > 0.0 and (int(self.invulnerability_timer * 14) % 2 == 0):
            # Flash red/translucent damage silhouette
            dmg_surf = swimmer_surf.copy()
            dmg_surf.fill((255, 60, 60, 120), special_flags=pygame.BLEND_RGBA_MULT)
            swimmer_surf = dmg_surf

        # Rotate with swimming pitch angle
        rotated_surf = pygame.transform.rotate(swimmer_surf, -tilt_deg)
        new_rect = rotated_surf.get_rect(center=(cx, cy))
        surface.blit(rotated_surf, new_rect.topleft)

        # 4. Precision Interaction Reticle (At the diver's hands)
        hand_x = cx + d * 32
        hand_y = cy + 4
        reticle_r = int(14 * self.pinch_anim_scale)
        
        # Color cues
        if self.is_hovering_chest:
            cursor_col = COLOR_EMERALD  # Ready to deposit!
        elif self.is_hovering_danger:
            cursor_col = COLOR_CORAL_RED
        elif self.is_hovering_interactable or self.carried_treasure:
            cursor_col = COLOR_GOLD
        elif self.is_pinching:
            cursor_col = (255, 240, 120)
        else:
            cursor_col = COLOR_NEON_TEAL

        # Glowing ring
        pygame.draw.circle(surface, cursor_col, (hand_x, hand_y), reticle_r, 2)
        pygame.draw.circle(surface, COLOR_WHITE, (hand_x, hand_y), 3)

        # Carried Treasure HUD prompt above swimmer
        if self.carried_treasure:
            font = pygame.font.SysFont("segoeui", 14, bold=True)
            prompt = font.render("CARRYING RELIC ▶ SWIM TO CHEST!", True, COLOR_GOLD)
            surface.blit(prompt, (cx - prompt.get_width() // 2, cy - 42))

        # Dual-hand Swimming Hydrodynamic Wake visual
        if self.is_dual_hand_swimming:
            wake_surf = pygame.Surface((120, 50), pygame.SRCALPHA)
            wake_alpha = int(120 + 50 * math.sin(self.dual_swim_wake_phase))
            wake_col = (*COLOR_OCEAN_CYAN[:3], wake_alpha)
            # Trailing dual swim wake arcs
            pygame.draw.arc(wake_surf, wake_col, pygame.Rect(10, 10, 50, 30), 0.5, 2.6, 2)
            pygame.draw.arc(wake_surf, wake_col, pygame.Rect(60, 10, 50, 30), 0.5, 2.6, 2)
            surface.blit(wake_surf, (cx - 60, cy - 25))
