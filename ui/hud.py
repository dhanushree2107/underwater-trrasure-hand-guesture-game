"""
Underwater Treasure Hunt - In-Game HUD System
Renders sleek, non-intrusive status telemetry:
Level, Objective Progress, Oxygen Meter, Score, Timer, Sonar Gems,
Carried Relic Banner, and Real-Time Gesture Badge.
"""

import math
import time
from typing import Optional, Tuple
import pygame

from config import (
    COLOR_NEON_TEAL,
    COLOR_OCEAN_CYAN,
    COLOR_GOLD,
    COLOR_EMERALD,
    COLOR_AMBER_WARNING,
    COLOR_CORAL_RED,
    COLOR_WHITE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)
from hand_tracking.gesture_detector import GestureType

class HUD:
    """Renders the game HUD during active dives."""

    def __init__(self):
        self.font_title = pygame.font.SysFont("segoeui", 20, bold=True)
        self.font_data = pygame.font.SysFont("segoeui", 17, bold=True)
        self.font_small = pygame.font.SysFont("segoeui", 13, bold=True)

    def draw(
        self,
        surface: pygame.Surface,
        level_id: int,
        level_name: str,
        deposited_count: int,
        required_deposits: int,
        score: int,
        display_oxygen: float,
        time_remaining: float,
        sonar_charges: int,
        current_gesture: GestureType,
        is_shield_active: bool,
        water_current_active: bool,
        carried_treasure_type: Optional[str] = None
    ) -> None:
        """Renders all HUD components."""
        # Top HUD Banner Bar (Dark Translucent Glass)
        banner_h = 75
        glass_bar = pygame.Surface((SCREEN_WIDTH, banner_h), pygame.SRCALPHA)
        glass_bar.fill((8, 18, 35, 205))
        pygame.draw.line(glass_bar, (0, 180, 216, 110), (0, banner_h - 1), (SCREEN_WIDTH, banner_h - 1), 2)
        surface.blit(glass_bar, (0, 0))

        # 1. Level Name (Left Side)
        lvl_text = f"LVL {level_id}: {level_name.upper()}"
        lvl_surf = self.font_title.render(lvl_text, True, COLOR_NEON_TEAL)
        surface.blit(lvl_surf, (20, 15))

        # Objective Progress Badge (Below Level Title)
        obj_text = f"OBJECTIVE: {deposited_count} / {required_deposits} STORED 🎁"
        obj_col = COLOR_EMERALD if deposited_count >= required_deposits else COLOR_GOLD
        obj_surf = self.font_small.render(obj_text, True, obj_col)
        surface.blit(obj_surf, (20, 42))

        # 2. Score Indicator
        score_label = self.font_small.render("SCORE", True, (160, 200, 220))
        score_val = self.font_title.render(f"{score:,}", True, COLOR_GOLD)
        surface.blit(score_label, (285, 14))
        surface.blit(score_val, (285, 34))

        # 3. Oxygen Bar (Center)
        bar_w = 230
        bar_h = 22
        bar_x = SCREEN_WIDTH // 2 - bar_w // 2
        bar_y = 36

        pct = max(0.0, min(100.0, display_oxygen))
        ox_label = self.font_small.render(f"OXYGEN RESERVE  {int(pct)}%", True, COLOR_WHITE)
        surface.blit(ox_label, (bar_x, 14))

        slot_rect = pygame.Rect(bar_x, bar_y, bar_w, bar_h)
        pygame.draw.rect(surface, (15, 30, 48), slot_rect, border_radius=6)
        pygame.draw.rect(surface, (40, 80, 120), slot_rect, width=2, border_radius=6)

        # Dynamic Bar Color by Oxygen Level
        if pct > 50:
            fill_color = COLOR_EMERALD
        elif pct > 25:
            fill_color = COLOR_AMBER_WARNING
        else:
            fill_color = (245, 45, 45)

        fill_w = int((pct / 100.0) * (bar_w - 4))
        if fill_w > 0:
            fill_rect = pygame.Rect(bar_x + 2, bar_y + 2, fill_w, bar_h - 4)
            pygame.draw.rect(surface, fill_color, fill_rect, border_radius=4)

        # 4. Timer Countdown (Right Center)
        mins = int(time_remaining) // 60
        secs = int(time_remaining) % 60
        timer_label = self.font_small.render("TIME", True, (160, 200, 220))
        timer_col = COLOR_WHITE if time_remaining > 20 else COLOR_CORAL_RED
        timer_val = self.font_title.render(f"{mins:02d}:{secs:02d}", True, timer_col)
        surface.blit(timer_label, (SCREEN_WIDTH - 360, 14))
        surface.blit(timer_val, (SCREEN_WIDTH - 360, 34))

        # 5. Sonar Charges (Right Side)
        sonar_label = self.font_small.render("SONAR (✌️)", True, (160, 200, 220))
        surface.blit(sonar_label, (SCREEN_WIDTH - 210, 14))
        for i in range(3):
            gem_x = SCREEN_WIDTH - 200 + (i * 30)
            gem_y = 44
            has_charge = (i < sonar_charges)
            gem_poly = [
                (gem_x, gem_y - 9),
                (gem_x + 8, gem_y),
                (gem_x, gem_y + 9),
                (gem_x - 8, gem_y),
            ]
            col = COLOR_NEON_TEAL if has_charge else (35, 55, 75)
            pygame.draw.polygon(surface, col, gem_poly)
            pygame.draw.polygon(surface, COLOR_WHITE if has_charge else (60, 90, 120), gem_poly, 1)

        # 6. Carried Item Alert Ribbon (Appears under banner when carrying a relic)
        if carried_treasure_type:
            ribbon_w = 420
            ribbon_h = 32
            rx = SCREEN_WIDTH // 2 - ribbon_w // 2
            ry = banner_h + 8
            
            r_surf = pygame.Surface((ribbon_w, ribbon_h), pygame.SRCALPHA)
            r_surf.fill((20, 45, 25, 215))
            pygame.draw.rect(r_surf, COLOR_EMERALD, (0, 0, ribbon_w, ribbon_h), width=2, border_radius=8)
            surface.blit(r_surf, (rx, ry))

            carried_str = f"💎 CARRYING {carried_treasure_type} ▶ SWIM TO CHEST DEPOT!"
            t_surf = self.font_small.render(carried_str, True, COLOR_WHITE)
            surface.blit(t_surf, (rx + ribbon_w // 2 - t_surf.get_width() // 2, ry + 8))

        # 7. Bottom Floating Real-Time Gesture Badge
        badge_w = 340
        badge_h = 38
        badge_x = SCREEN_WIDTH // 2 - badge_w // 2
        badge_y = SCREEN_HEIGHT - 48

        badge_surf = pygame.Surface((badge_w, badge_h), pygame.SRCALPHA)
        badge_surf.fill((10, 22, 40, 210))
        surface.blit(badge_surf, (badge_x, badge_y))

        if is_shield_active or current_gesture == GestureType.FIST:
            g_icon = "✊"
            g_name = "SHIELD ACTIVE"
            g_col = COLOR_NEON_TEAL
        elif current_gesture == GestureType.PINCH:
            g_icon = "🤏"
            g_name = "PINCH: GRAB / DEPOSIT"
            g_col = COLOR_GOLD
        elif water_current_active or current_gesture == GestureType.OPEN_PALM:
            g_icon = "✋"
            g_name = "WATER CURRENT BURST"
            g_col = COLOR_OCEAN_CYAN
        elif current_gesture == GestureType.TWO_FINGERS:
            g_icon = "✌️"
            g_name = "SONAR SCANNING"
            g_col = COLOR_EMERALD
        elif current_gesture == GestureType.MOVE:
            g_icon = "🖐"
            g_name = "HAND SWIMMING"
            g_col = (180, 220, 240)
        else:
            g_icon = "⏳"
            g_name = "SEARCHING FOR HAND..."
            g_col = (130, 150, 170)

        badge_text = self.font_small.render(f"{g_icon}  {g_name}", True, g_col)
        pygame.draw.rect(surface, g_col, (badge_x, badge_y, badge_w, badge_h), width=2, border_radius=8)
        surface.blit(badge_text, (badge_x + badge_w // 2 - badge_text.get_width() // 2, badge_y + 10))
