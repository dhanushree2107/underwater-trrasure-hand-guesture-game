"""
Underwater Treasure Hunt - Underwater Hand Cursor System
Renders a custom, high-visibility underwater reticle that follows the player's hand.
Features glowing multi-layer halos, bubble particle trails, dynamic state styling
(Normal, Treasure Target, Danger Warning, Pinch Grab, Sonar Pulse), and a
"HAND NOT DETECTED" indicator when tracking is lost.
"""

from enum import Enum
import math
import random
import time
from typing import List, Optional, Tuple
import pygame

from config import (
    COLOR_NEON_TEAL,
    COLOR_OCEAN_CYAN,
    COLOR_GOLD,
    COLOR_EMERALD,
    COLOR_CORAL_RED,
    COLOR_AMBER_WARNING,
    COLOR_WHITE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)
from hand_tracking.gesture_detector import GestureType

class CursorTargetState(Enum):
    NORMAL = "NORMAL"
    TREASURE_TARGET = "TREASURE_TARGET"
    DANGER = "DANGER"
    PINCH = "PINCH"
    SONAR = "SONAR"
    CURRENT = "CURRENT"
    SHIELD = "SHIELD"

class CursorTrailBubble:
    """A tiny bubble drifting behind the glowing hand cursor."""
    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        self.x = x + random.uniform(-4, 4)
        self.y = y + random.uniform(-4, 4)
        self.radius = random.uniform(2.0, 4.5)
        self.max_life = random.uniform(0.35, 0.65)
        self.life = self.max_life
        self.vy = random.uniform(-25.0, -10.0) # Upward buoyant drift
        self.vx = random.uniform(-10.0, 10.0)
        self.color = color

    def update(self, dt: float) -> bool:
        self.life -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.radius = max(0.8, self.radius - 1.5 * dt)
        return self.life > 0

class HandCursor:
    """
    Dedicated underwater hand cursor that is ALWAYS visible during gameplay and menus.
    Tracks hand position with exponential smoothing, emits bubble trails, and
    displays visual cues for targeting, grabbing, and hazards.
    """

    def __init__(self):
        self.x: float = SCREEN_WIDTH / 2.0
        self.y: float = SCREEN_HEIGHT / 2.0
        self.target_state: CursorTargetState = CursorTargetState.NORMAL
        self.is_hand_detected: bool = True
        self.hand_lost_timer: float = 0.0

        # Animation states
        self.pulse_phase: float = 0.0
        self.pinch_scale: float = 1.0
        self.sonar_pulse_radius: float = 0.0
        self.trail_bubbles: List[CursorTrailBubble] = []
        self.bubble_emit_timer: float = 0.0

        # Typography
        if not pygame.font.get_init():
            pygame.font.init()
        self.font_badge = pygame.font.SysFont("segoeui", 12, bold=True)
        self.font_warning = pygame.font.SysFont("segoeui", 14, bold=True)

    def update(
        self,
        raw_x: float,
        raw_y: float,
        is_detected: bool,
        current_gesture: GestureType,
        is_hovering_treasure: bool = False,
        is_hovering_danger: bool = False,
        sonar_active: bool = False,
        dt: float = 0.016
    ) -> None:
        """Updates cursor kinematics, targeting states, and bubble trail."""
        self.is_hand_detected = is_detected
        self.pulse_phase += 5.5 * dt

        if not is_detected:
            self.hand_lost_timer += dt
        else:
            self.hand_lost_timer = 0.0

        # Smooth position interpolation towards hand target
        smooth_factor = min(1.0, 24.0 * dt)
        self.x += (raw_x - self.x) * smooth_factor
        self.y += (raw_y - self.y) * smooth_factor
        self.x = max(10.0, min(SCREEN_WIDTH - 10.0, self.x))
        self.y = max(10.0, min(SCREEN_HEIGHT - 10.0, self.y))

        # Determine visual target state
        if current_gesture == GestureType.PINCH:
            self.target_state = CursorTargetState.PINCH
            self.pinch_scale = max(0.65, self.pinch_scale - 6.0 * dt)
        else:
            self.pinch_scale = min(1.0, self.pinch_scale + 5.0 * dt)
            if sonar_active or current_gesture == GestureType.TWO_FINGERS:
                self.target_state = CursorTargetState.SONAR
                self.sonar_pulse_radius += 120.0 * dt
                if self.sonar_pulse_radius > 65.0:
                    self.sonar_pulse_radius = 15.0
            elif is_hovering_danger:
                self.target_state = CursorTargetState.DANGER
            elif is_hovering_treasure:
                self.target_state = CursorTargetState.TREASURE_TARGET
            elif current_gesture == GestureType.OPEN_PALM:
                self.target_state = CursorTargetState.CURRENT
            elif current_gesture == GestureType.FIST:
                self.target_state = CursorTargetState.SHIELD
            else:
                self.target_state = CursorTargetState.NORMAL

        # Emit cursor bubble trail
        self.bubble_emit_timer += dt
        if self.bubble_emit_timer >= 0.045:
            self.bubble_emit_timer = 0.0
            trail_col = COLOR_GOLD if self.target_state == CursorTargetState.TREASURE_TARGET else COLOR_NEON_TEAL
            self.trail_bubbles.append(CursorTrailBubble(self.x, self.y, trail_col))

        # Update bubbles
        self.trail_bubbles = [b for b in self.trail_bubbles if b.update(dt)]

    def draw(self, surface: pygame.Surface) -> None:
        """Renders the custom underwater cursor and 'HAND NOT DETECTED' banner."""
        cx = int(self.x)
        cy = int(self.y)

        # 1. Draw glowing bubble trail
        for b in self.trail_bubbles:
            alpha = int(255 * (b.life / b.max_life))
            bubble_surf = pygame.Surface((int(b.radius * 2 + 4), int(b.radius * 2 + 4)), pygame.SRCALPHA)
            bcx, bcy = int(b.radius + 2), int(b.radius + 2)
            pygame.draw.circle(bubble_surf, (*b.color[:3], int(alpha * 0.7)), (bcx, bcy), int(b.radius))
            pygame.draw.circle(bubble_surf, (255, 255, 255, alpha), (bcx - 1, bcy - 1), max(1, int(b.radius * 0.4)))
            surface.blit(bubble_surf, (int(b.x - bcx), int(b.y - bcy)))

        # 2. Configure State Styling
        pulse = math.sin(self.pulse_phase) * 3.0
        base_radius = int((18 + pulse) * self.pinch_scale)
        size = base_radius * 2 + 50
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        scx, scy = size // 2, size // 2

        if self.target_state == CursorTargetState.PINCH:
            main_col = COLOR_GOLD
            aura_col = (*COLOR_GOLD[:3], 140)
            badge_text = "GRAB 🤏"
        elif self.target_state == CursorTargetState.TREASURE_TARGET:
            main_col = COLOR_GOLD
            aura_col = (*COLOR_GOLD[:3], 120)
            badge_text = "TARGET 💎"
        elif self.target_state == CursorTargetState.DANGER:
            main_col = COLOR_CORAL_RED
            aura_col = (*COLOR_CORAL_RED[:3], 160)
            badge_text = "DANGER ⚠️"
        elif self.target_state == CursorTargetState.SONAR:
            main_col = COLOR_OCEAN_CYAN
            aura_col = (*COLOR_OCEAN_CYAN[:3], 130)
            badge_text = "SONAR ✌️"
        elif self.target_state == CursorTargetState.CURRENT:
            main_col = COLOR_WHITE
            aura_col = (*COLOR_WHITE[:3], 140)
            badge_text = "CURRENT ✋"
        elif self.target_state == CursorTargetState.SHIELD:
            main_col = COLOR_EMERALD
            aura_col = (*COLOR_EMERALD[:3], 160)
            badge_text = "SHIELD ✊"
        else:
            main_col = COLOR_NEON_TEAL
            aura_col = (*COLOR_NEON_TEAL[:3], 90)
            badge_text = "HAND 🖐️"

        # Multi-layer Glowing Halo
        pygame.draw.circle(surf, aura_col, (scx, scy), base_radius + 6, 3)
        pygame.draw.circle(surf, (*main_col[:3], 230), (scx, scy), base_radius, 2)
        pygame.draw.circle(surf, (*COLOR_WHITE[:3], 240), (scx, scy), 3)

        # Crosshairs / Reticle Brackets
        arm_len = 6
        gap = base_radius + 2
        pygame.draw.line(surf, main_col, (scx - gap - arm_len, scy), (scx - gap, scy), 2)
        pygame.draw.line(surf, main_col, (scx + gap, scy), (scx + gap + arm_len, scy), 2)
        pygame.draw.line(surf, main_col, (scx, scy - gap - arm_len), (scx, scy - gap), 2)
        pygame.draw.line(surf, main_col, (scx, scy + gap), (scx, scy + gap + arm_len), 2)

        # State-specific accents:
        if self.target_state == CursorTargetState.TREASURE_TARGET:
            # Diamond target brackets
            d_size = 7
            pygame.draw.lines(surf, COLOR_GOLD, False, [
                (scx - gap - 3, scy - d_size),
                (scx - gap - 8, scy),
                (scx - gap - 3, scy + d_size)
            ], 2)
            pygame.draw.lines(surf, COLOR_GOLD, False, [
                (scx + gap + 3, scy - d_size),
                (scx + gap + 8, scy),
                (scx + gap + 3, scy + d_size)
            ], 2)

        elif self.target_state == CursorTargetState.DANGER:
            # Flashing hazard triangle above reticle
            tri = [(scx, scy - base_radius - 16), (scx - 7, scy - base_radius - 5), (scx + 7, scy - base_radius - 5)]
            pygame.draw.polygon(surf, COLOR_CORAL_RED, tri)

        elif self.target_state == CursorTargetState.PINCH:
            # Inward grab arrows
            for angle in [math.pi * 0.25, math.pi * 0.75, math.pi * 1.25, math.pi * 1.75]:
                ax = scx + math.cos(angle) * (base_radius + 9)
                ay = scy + math.sin(angle) * (base_radius + 9)
                ix = scx + math.cos(angle) * (base_radius + 3)
                iy = scy + math.sin(angle) * (base_radius + 3)
                pygame.draw.line(surf, COLOR_GOLD, (int(ax), int(ay)), (int(ix), int(iy)), 2)

        elif self.target_state == CursorTargetState.SONAR:
            # Sonar ripple ring
            if self.sonar_pulse_radius > 0:
                sonar_alpha = max(0, int(200 * (1.0 - self.sonar_pulse_radius / 65.0)))
                pygame.draw.circle(surf, (*COLOR_OCEAN_CYAN[:3], sonar_alpha), (scx, scy), int(self.sonar_pulse_radius), 2)

        # Blit Reticle onto main surface
        surface.blit(surf, (cx - scx, cy - scy))

        # Small gesture badge pill next to cursor
        badge_surf = self.font_badge.render(badge_text, True, main_col)
        surface.blit(badge_surf, (cx + base_radius + 12, cy - 8))

        # 3. "HAND NOT DETECTED" Indicator Banner (if hand is lost)
        if not self.is_hand_detected:
            banner_w = 460
            banner_h = 36
            bx = SCREEN_WIDTH // 2 - banner_w // 2
            by = 82
            
            b_surf = pygame.Surface((banner_w, banner_h), pygame.SRCALPHA)
            b_surf.fill((25, 10, 10, 220))
            pygame.draw.rect(b_surf, COLOR_AMBER_WARNING, (0, 0, banner_w, banner_h), width=2, border_radius=8)
            
            pulse_warn = int(180 + math.sin(time.time() * 8.0) * 75)
            warn_col = (255, pulse_warn, 50)
            msg = "⚠️ HAND NOT DETECTED — HOLD HAND IN FRONT OF WEBCAM"
            txt_surf = self.font_warning.render(msg, True, warn_col)
            b_surf.blit(txt_surf, (banner_w // 2 - txt_surf.get_width() // 2, 8))
            
            surface.blit(b_surf, (bx, by))
