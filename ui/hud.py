"""
Underwater Treasure Hunt - In-Game HUD System
Renders sleek, non-intrusive status telemetry:
Level, Main Mission Objective, Oxygen Meter, Lives (❤️ ❤️ ❤️), Score, Timer,
Sonar Gems, Swim Sync Meter (SWIM SYNC ████████░░ 80%), Hand Tracking Confidence,
Subtle Treasure Compass (🧭 ↗ 42m), Carried Relic Banner, and Real-Time Gesture Badge.
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
    COLOR_PURPLE_MYSTIC,
    COLOR_WHITE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)
from hand_tracking.gesture_detector import GestureType

class HUD:
    """Renders the comprehensive game HUD during active dives."""

    def __init__(self):
        if not pygame.font.get_init():
            pygame.font.init()
        self.font_title = pygame.font.SysFont("segoeui", 18, bold=True)
        self.font_data = pygame.font.SysFont("segoeui", 16, bold=True)
        self.font_small = pygame.font.SysFont("segoeui", 12, bold=True)
        self.font_tiny = pygame.font.SysFont("segoeui", 11, bold=True)

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
        explored_grid: Optional[List[List[bool]]] = None,
        lives: int = 3,
        sync_level: float = 0.85,
        is_combo_swim: bool = False,
        left_confidence: float = 0.95,
        right_confidence: float = 0.92,
        compass_target: Optional[Tuple[float, float, str]] = None,
        ocean_condition: str = "CALM WATER",
    ) -> None:
        """Renders all HUD components including sync bar, lives, and compass."""
        # 1. Exploration Minimap (Bottom Left Corner)
        self._draw_minimap(surface, player_pos, chest_pos, exploration_ratio, explored_grid)

        # 2. Top HUD Banner Bar (Dark Translucent Glass)
        banner_h = 76
        glass_bar = pygame.Surface((SCREEN_WIDTH, banner_h), pygame.SRCALPHA)
        glass_bar.fill((8, 18, 35, 215))
        border_col = (245, 170, 30, 140) if is_challenge else (0, 180, 216, 120)
        pygame.draw.line(glass_bar, border_col, (0, banner_h - 1), (SCREEN_WIDTH, banner_h - 1), 2)
        surface.blit(glass_bar, (0, 0))

        # --- Section A: Level Title & Lives (Left) ---
        lvl_prefix = "CHALLENGE" if is_challenge else f"LVL {level_id}"
        lvl_text = f"{lvl_prefix}: {level_name.upper()}"
        title_col = COLOR_AMBER_WARNING if is_challenge else COLOR_NEON_TEAL
        lvl_surf = self.font_title.render(lvl_text, True, title_col)
        surface.blit(lvl_surf, (20, 10))

        # 3 Lives Indicator (♥ ♥ ♥)
        hearts_x = 20
        for i in range(3):
            heart_icon = "♥" if i < lives else "♡"
            h_col = COLOR_CORAL_RED if i < lives else (100, 110, 125)
            h_surf = self.font_title.render(heart_icon, True, h_col)
            surface.blit(h_surf, (hearts_x + i * 24, 36))

        # Objective Progress Badge (Next to Lives)
        obj_text = f"GOAL: {deposited_count}/{required_deposits} RELICS"
        obj_col = COLOR_EMERALD if deposited_count >= required_deposits else COLOR_GOLD
        obj_surf = self.font_small.render(obj_text, True, obj_col)
        surface.blit(obj_surf, (105, 42))

        # --- Section B: Score & Combo (Left Center) ---
        score_label = self.font_tiny.render("SCORE", True, (160, 200, 220))
        score_val = self.font_title.render(f"{score:,}", True, COLOR_GOLD)
        surface.blit(score_label, (260, 12))
        surface.blit(score_val, (260, 32))

        # Combo Streak Badge
        if combo_multiplier > 1.0:
            combo_surf = self.font_small.render(f"COMBO x{combo_multiplier:.1f}", True, (255, 140, 30))
            surface.blit(combo_surf, (260, 52))

        # --- Section C: Oxygen Bar (Center) ---
        bar_w = 210
        bar_h = 18
        bar_x = SCREEN_WIDTH // 2 - bar_w // 2 - 40
        bar_y = 30

        pct = max(0.0, min(100.0, display_oxygen))
        ox_label = self.font_tiny.render(f"OXYGEN RESERVE  {int(pct)}%", True, COLOR_WHITE)
        surface.blit(ox_label, (bar_x, 12))

        slot_rect = pygame.Rect(bar_x, bar_y, bar_w, bar_h)
        pygame.draw.rect(surface, (15, 30, 48), slot_rect, border_radius=5)
        pygame.draw.rect(surface, (40, 80, 120), slot_rect, width=2, border_radius=5)

        fill_color = COLOR_EMERALD if pct > 50 else (COLOR_AMBER_WARNING if pct > 25 else COLOR_CORAL_RED)
        fill_w = int((pct / 100.0) * (bar_w - 4))
        if fill_w > 0:
            fill_rect = pygame.Rect(bar_x + 2, bar_y + 2, fill_w, bar_h - 4)
            pygame.draw.rect(surface, fill_color, fill_rect, border_radius=3)

        # --- Section D: Swim Synchronization Meter (Right Center) ---
        sync_x = SCREEN_WIDTH // 2 + 85
        sync_y = 30
        sync_w = 140
        sync_pct = max(0, min(100, int(sync_level * 100)))

        sync_lbl = self.font_tiny.render(f"SWIM SYNC  {sync_pct}%", True, (180, 235, 255))
        surface.blit(sync_lbl, (sync_x, 12))

        sync_rect = pygame.Rect(sync_x, sync_y, sync_w, bar_h)
        pygame.draw.rect(surface, (15, 30, 48), sync_rect, border_radius=5)
        pygame.draw.rect(surface, COLOR_NEON_TEAL, sync_rect, width=1, border_radius=5)

        sync_fill_w = int((sync_pct / 100.0) * (sync_w - 4))
        if sync_fill_w > 0:
            s_col = COLOR_GOLD if is_combo_swim else COLOR_NEON_TEAL
            pygame.draw.rect(surface, s_col, (sync_x + 2, sync_y + 2, sync_fill_w, bar_h - 4), border_radius=3)

        if is_combo_swim:
            combo_pill = self.font_tiny.render("COMBO SWIM", True, COLOR_GOLD)
            surface.blit(combo_pill, (sync_x + sync_w + 8, sync_y + 2))

        # --- Section E: Timer & Sonar (Right) ---
        mins = int(time_remaining) // 60
        secs = int(time_remaining) % 60
        timer_col = COLOR_WHITE if time_remaining > 20 else COLOR_CORAL_RED
        timer_val = self.font_title.render(f"{mins:02d}:{secs:02d}", True, timer_col)
        surface.blit(timer_val, (SCREEN_WIDTH - 250, 22))

        # Sonar gems
        sonar_label = self.font_tiny.render("SONAR SCAN", True, (160, 200, 220))
        surface.blit(sonar_label, (SCREEN_WIDTH - 150, 10))
        for i in range(3):
            gem_x = SCREEN_WIDTH - 145 + (i * 26)
            gem_y = 38
            has_charge = (i < sonar_charges)
            gem_poly = [
                (gem_x, gem_y - 8),
                (gem_x + 7, gem_y),
                (gem_x, gem_y + 8),
                (gem_x - 7, gem_y),
            ]
            col = COLOR_NEON_TEAL if has_charge else (35, 55, 75)
            pygame.draw.polygon(surface, col, gem_poly)
            pygame.draw.polygon(surface, COLOR_WHITE if has_charge else (60, 90, 120), gem_poly, 1)

        # Hand Tracking Confidence Badges (Top Far Right Corner)
        l_conf_pct = int(left_confidence * 100)
        r_conf_pct = int(right_confidence * 100)
        conf_txt = f"L: {l_conf_pct}% | R: {r_conf_pct}%"
        conf_col = COLOR_EMERALD if (l_conf_pct > 60 and r_conf_pct > 60) else COLOR_AMBER_WARNING
        conf_surf = self.font_tiny.render(conf_txt, True, conf_col)
        surface.blit(conf_surf, (SCREEN_WIDTH - 150, 56))

        # --- Section F: Subtle Treasure Compass (Section 28) ---
        if compass_target:
            tx, ty, t_label = compass_target
            dx = tx - player_pos[0]
            dy = ty - player_pos[1]
            dist_m = int(math.hypot(dx, dy) / 16.0) # Scale px to meters
            angle_rad = math.atan2(dy, dx)
            arrows = ["→", "↘", "↓", "↙", "←", "↖", "↑", "↗"]
            norm_deg = math.degrees(angle_rad) % 360
            deg_idx = int((norm_deg + 22.5) / 45.0) % 8
            compass_arrow = arrows[deg_idx]

            comp_txt = f"{t_label}: {compass_arrow} {dist_m}m"
            comp_surf = self.font_small.render(comp_txt, True, COLOR_GOLD)
            surface.blit(comp_surf, (SCREEN_WIDTH // 2 - comp_surf.get_width() // 2, banner_h + 8))

        # --- Section G: Dynamic Ocean Condition Ribbon ---
        cond_surf = self.font_tiny.render(f"OCEAN: {ocean_condition}", True, (170, 215, 235))
        surface.blit(cond_surf, (SCREEN_WIDTH // 2 - cond_surf.get_width() // 2, banner_h + 30))

        # --- Section H: Carried Item Alert Ribbon ---
        if carried_treasure_type:
            ribbon_w = 440
            ribbon_h = 32
            rx = SCREEN_WIDTH // 2 - ribbon_w // 2
            ry = banner_h + 52
            
            r_surf = pygame.Surface((ribbon_w, ribbon_h), pygame.SRCALPHA)
            r_surf.fill((20, 45, 25, 220))
            pygame.draw.rect(r_surf, COLOR_EMERALD, (0, 0, ribbon_w, ribbon_h), width=2, border_radius=8)
            surface.blit(r_surf, (rx, ry))

            carried_str = f"CARRYING {carried_treasure_type} > SWIM TO DEPOT CHEST!"
            t_surf = self.font_small.render(carried_str, True, COLOR_WHITE)
            surface.blit(t_surf, (rx + ribbon_w // 2 - t_surf.get_width() // 2, ry + 8))

        # --- Section I: Bottom Floating Gesture Badge ---
        badge_w = 340
        badge_h = 36
        badge_x = SCREEN_WIDTH // 2 - badge_w // 2
        badge_y = SCREEN_HEIGHT - 44

        badge_surf = pygame.Surface((badge_w, badge_h), pygame.SRCALPHA)
        badge_surf.fill((10, 22, 40, 215))
        surface.blit(badge_surf, (badge_x, badge_y))

        if is_shield_active or current_gesture == GestureType.FIST:
            g_tag = "SHIELD"
            g_name = "SHIELD FORCEFIELD ACTIVE"
            g_col = COLOR_NEON_TEAL
        elif current_gesture == GestureType.PINCH:
            g_tag = "GRAB"
            g_name = "PINCH: GRAB / DEPOSIT"
            g_col = COLOR_GOLD
        elif water_current_active or current_gesture == GestureType.OPEN_PALM:
            g_tag = "CURRENT"
            g_name = "WATER CURRENT BURST"
            g_col = COLOR_OCEAN_CYAN
        elif current_gesture == GestureType.TWO_FINGERS:
            g_tag = "SONAR"
            g_name = "SONAR SCANNING"
            g_col = COLOR_EMERALD
        elif current_gesture == GestureType.MOVE:
            g_tag = "SWIM"
            g_name = "DUAL-HAND SWIMMING"
            g_col = (180, 220, 240)
        else:
            g_tag = "READY"
            g_name = "SEARCHING FOR HANDS..."
            g_col = (130, 150, 170)

        badge_text = self.font_small.render(f"[{g_tag}]  {g_name}", True, g_col)
        pygame.draw.rect(surface, g_col, (badge_x, badge_y, badge_w, badge_h), width=2, border_radius=8)
        surface.blit(badge_text, (badge_x + badge_w // 2 - badge_text.get_width() // 2, badge_y + 8))

    def _draw_minimap(
        self,
        surface: pygame.Surface,
        player_pos: Tuple[float, float],
        chest_pos: Tuple[float, float],
        exploration_ratio: float,
        explored_grid: Optional[List[List[bool]]]
    ) -> None:
        """Renders corner sonar radar minimap showing explored terrain, diver, and vault."""
        mw, mh = 124, 70
        mx = 20
        my = SCREEN_HEIGHT - mh - 18

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
        map_lbl = self.font_tiny.render(f"EXPLORED {int(exploration_ratio * 100)}%", True, (160, 210, 235))
        surface.blit(map_lbl, (mx + 4, my - 16))
