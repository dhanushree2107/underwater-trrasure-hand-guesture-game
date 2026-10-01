"""
Underwater Treasure Hunt - In-Game HUD System
Renders sleek, non-intrusive status telemetry:
Level, Objective Progress, Oxygen Meter, Score, Timer, Sonar Gems,
Carried Relic Banner, and Real-Time Gesture Badge.
"""

import math
import time
from typing import Optional, Tuple, List
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
        water_current_active: bool = False,
        carried_treasure_type: Optional[str] = None,
        combo_multiplier: float = 1.0,
        is_challenge: bool = False,
        player_pos: Tuple[float, float] = (640, 360),
        chest_pos: Tuple[float, float] = (150, 640),
        exploration_ratio: float = 0.0,
        explored_grid: Optional[List[List[bool]]] = None
    ) -> None:
        """Renders all HUD components including the Exploration Minimap."""
        # Exploration Minimap (Bottom Left Corner)
        self._draw_minimap(surface, player_pos, chest_pos, exploration_ratio, explored_grid)

        # Top HUD Banner Bar (Dark Translucent Glass)
        banner_h = 75
        glass_bar = pygame.Surface((SCREEN_WIDTH, banner_h), pygame.SRCALPHA)
        glass_bar.fill((8, 18, 35, 205))
        border_col = (245, 170, 30, 140) if is_challenge else (0, 180, 216, 110)
        pygame.draw.line(glass_bar, border_col, (0, banner_h - 1), (SCREEN_WIDTH, banner_h - 1), 2)
        surface.blit(glass_bar, (0, 0))

        # 1. Level Name (Left Side)
        lvl_prefix = "CHALLENGE ⚡" if is_challenge else f"LVL {level_id}"
        lvl_text = f"{lvl_prefix}: {level_name.upper()}"
        title_col = COLOR_AMBER_WARNING if is_challenge else COLOR_NEON_TEAL
        lvl_surf = self.font_title.render(lvl_text, True, title_col)
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

        # Combo Streak Badge (if multiplier active)
        if combo_multiplier > 1.0:
            pulse = math.sin(time.time() * 8.0) * 3.0
            combo_surf = self.font_small.render(f"COMBO x{combo_multiplier:.1f}! 🔥", True, (255, 140, 30))
            surface.blit(combo_surf, (375, 36 + int(pulse * 0.5)))

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

    def _draw_minimap(
        self,
        surface: pygame.Surface,
        player_pos: Tuple[float, float],
        chest_pos: Tuple[float, float],
        exploration_ratio: float,
        explored_grid: Optional[List[List[bool]]]
    ) -> None:
        """Renders corner sonar radar minimap showing explored terrain, diver, and vault."""
        mw, mh = 124, 72
        mx = 20
        my = SCREEN_HEIGHT - mh - 20

        map_surf = pygame.Surface((mw, mh), pygame.SRCALPHA)
        map_surf.fill((6, 16, 32, 215))
        pygame.draw.rect(map_surf, (0, 180, 216, 160), (0, 0, mw, mh), width=2, border_radius=6)

        # Draw Explored cells
        if explored_grid:
            rows = len(explored_grid)
            cols = len(explored_grid[0]) if rows > 0 else 0
            cw = mw / max(1, cols)
            ch = mh / max(1, rows)
            for r in range(rows):
                for c in range(cols):
                    if explored_grid[r][c]:
                        pygame.draw.rect(map_surf, (12, 48, 70), (int(c * cw), int(r * ch), max(1, int(cw)), max(1, int(ch))))

        # Chest Marker
        cx, cy = chest_pos
        mcx = int((cx / SCREEN_WIDTH) * mw)
        mcy = int((cy / SCREEN_HEIGHT) * mh)
        pygame.draw.rect(map_surf, COLOR_GOLD, (mcx - 3, mcy - 3, 6, 6))

        # Diver Marker
        px, py = player_pos
        mpx = int((px / SCREEN_WIDTH) * mw)
        mpy = int((py / SCREEN_HEIGHT) * mh)
        pygame.draw.circle(map_surf, COLOR_NEON_TEAL, (mpx, mpy), 3)
        pygame.draw.circle(map_surf, COLOR_WHITE, (mpx, mpy), 1)

        surface.blit(map_surf, (mx, my))

        # Minimap Label
        map_lbl = self.font_small.render(f"EXPLORED {int(exploration_ratio * 100)}%", True, (160, 210, 235))
        surface.blit(map_lbl, (mx + 4, my - 16))
