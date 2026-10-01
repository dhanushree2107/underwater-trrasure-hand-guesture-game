"""
Underwater Treasure Hunt - Dynamic Ocean Conditions & Random Ocean Events
Manages ocean weather states, shark pursuits, whirlpool vortexes, octopus ambushes,
sudden darkness, ancient gesture puzzles, and the Level 5 Ancient Guardian encounter.
"""

from enum import Enum
import math
import random
import time
from typing import List, Optional, Tuple
import pygame

from config import (
    COLOR_CORAL_RED,
    COLOR_OCEAN_CYAN,
    COLOR_NEON_TEAL,
    COLOR_GOLD,
    COLOR_PURPLE_MYSTIC,
    COLOR_EMERALD,
    COLOR_WHITE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)


class OceanCondition(Enum):
    CALM_WATER = "CALM WATER"
    LIGHT_CURRENT = "LIGHT CURRENT"
    STRONG_CURRENT = "STRONG CURRENT"
    DARK_WATER = "DARK WATER"
    TURBULENT_WATER = "TURBULENT WATER"


class AncientGesturePuzzle:
    """
    An ancient stone mechanism requiring a specific sequence of hand gestures
    to deactivate ruin forcefields and unlock the path.
    Example sequence: ✌️ TWO FINGERS -> ✋ OPEN PALM -> 🤏 PINCH
    """

    def __init__(self, x: float = 640.0, y: float = 260.0):
        self.x = x
        self.y = y
        self.radius = 55.0
        self.target_sequence = ["TWO_FINGERS", "OPEN_PALM", "PINCH"]
        self.current_step = 0
        self.is_solved = False
        self.reset_timer = 0.0
        self.pulse_phase = 0.0
        self.symbol_icons = {"TWO_FINGERS": "✌️", "OPEN_PALM": "✋", "PINCH": "🤏"}

    @property
    def is_active(self) -> bool:
        return not self.is_solved

    def reset_puzzle(self) -> None:
        self.current_step = 0
        self.is_solved = False
        self.reset_timer = 0.0

    def input_gesture(self, gesture_name: str) -> Tuple[bool, bool]:
        """
        Submits a recognized gesture to the puzzle.
        Returns: (step_advanced: bool, puzzle_completed: bool)
        """
        if self.is_solved or self.reset_timer > 0.0:
            return False, False

        expected = self.target_sequence[self.current_step]
        if gesture_name == expected:
            self.current_step += 1
            if self.current_step >= len(self.target_sequence):
                self.is_solved = True
                return True, True
            return True, False
        elif gesture_name in ("FIST", "PINCH", "TWO_FINGERS", "OPEN_PALM") and gesture_name != expected:
            # Wrong gesture: momentary reset penalty
            self.current_step = 0
            self.reset_timer = 0.8
            return False, False

        return False, False

    def update(self, dt: float) -> None:
        self.pulse_phase += 3.5 * dt
        if self.reset_timer > 0.0:
            self.reset_timer = max(0.0, self.reset_timer - dt)

    def draw(self, surface: pygame.Surface) -> None:
        cx, cy = int(self.x), int(self.y)
        r = int(self.radius)

        # Stone circle base
        stone_col = (55, 65, 80) if not self.is_solved else (40, 110, 85)
        border_col = COLOR_PURPLE_MYSTIC if not self.is_solved else COLOR_EMERALD
        pygame.draw.circle(surface, stone_col, (cx, cy), r)
        pygame.draw.circle(surface, border_col, (cx, cy), r, 3)

        # Draw glyph indicators
        font = pygame.font.SysFont("segoeui", 18, bold=True)
        spacing = 38
        start_x = cx - ((len(self.target_sequence) - 1) * spacing) // 2

        for i, g_name in enumerate(self.target_sequence):
            gx = start_x + i * spacing
            gy = cy
            is_done = i < self.current_step
            is_curr = i == self.current_step and not self.is_solved
            
            box_col = COLOR_EMERALD if is_done else (COLOR_GOLD if is_curr else (110, 120, 135))
            pygame.draw.circle(surface, box_col, (gx, gy), 14, 2 if not is_done else 0)
            
            icon = self.symbol_icons.get(g_name, "?")
            txt = font.render(icon, True, COLOR_WHITE)
            surface.blit(txt, (gx - txt.get_width() // 2, gy - txt.get_height() // 2))

        # Title
        title_font = pygame.font.SysFont("segoeui", 13, bold=True)
        title_text = "ANCIENT MECHANISM SOLVED! ✨" if self.is_solved else "GESTURE SEQUENCE REQUIRED"
        title_surf = title_font.render(title_text, True, COLOR_GOLD if not self.is_solved else COLOR_EMERALD)
        surface.blit(title_surf, (cx - title_surf.get_width() // 2, cy - r - 22))


class TwoHandAncientSeal:
    """
    Major two-hand interactive seal on the Ancient Door (Section 23).
    Two glowing hand markers appear. Diver must place both hands near markers,
    then slowly move both hands apart in sync to break the seal!
    """

    def __init__(self, center_x: float = 640.0, center_y: float = 460.0):
        self.center_x = center_x
        self.center_y = center_y
        self.initial_marker_dist = 160.0
        self.left_marker = (center_x - self.initial_marker_dist / 2, center_y)
        self.right_marker = (center_x + self.initial_marker_dist / 2, center_y)
        
        self.separation_progress = 0.0  # 0.0 to 1.0 (unlocked at 1.0)
        self.is_opened = False
        self.hands_engaged = False
        self.pulse_phase = 0.0

    def reset(self) -> None:
        self.separation_progress = 0.0
        self.is_opened = False
        self.hands_engaged = False

    def update(
        self,
        dt: float,
        left_hand_pos: Optional[Tuple[float, float]],
        right_hand_pos: Optional[Tuple[float, float]],
    ) -> bool:
        """
        Updates two-hand separation progress.
        Returns True if ancient seal just opened!
        """
        self.pulse_phase += 4.0 * dt
        if self.is_opened:
            return False

        if left_hand_pos is None or right_hand_pos is None:
            self.hands_engaged = False
            self.separation_progress = max(0.0, self.separation_progress - 1.2 * dt)
            return False

        lx, ly = left_hand_pos
        rx, ry = right_hand_pos

        # Check if hands are aligned with left and right markers
        dist_l = math.hypot(lx - self.left_marker[0], ly - self.left_marker[1])
        dist_r = math.hypot(rx - self.right_marker[0], ry - self.right_marker[1])

        current_hand_dist = math.hypot(rx - lx, ry - ly)

        if dist_l < 110.0 and dist_r < 110.0:
            self.hands_engaged = True
            # Check if player is moving both hands apart
            if current_hand_dist > self.initial_marker_dist + 30.0:
                spread = current_hand_dist - (self.initial_marker_dist + 30.0)
                target_prog = min(1.0, spread / 220.0)
                self.separation_progress += (target_prog - self.separation_progress) * min(1.0, 5.0 * dt)
                if self.separation_progress >= 0.98:
                    self.is_opened = True
                    return True
        else:
            self.hands_engaged = False
        return False

    def check_pull_apart(
        self,
        hand1_pos: Tuple[float, float],
        hand2_pos: Tuple[float, float],
        h1_dx: float = 0.0,
        h2_dx: float = 0.0,
    ) -> bool:
        """Checks if both hands are placed near seal markers and pulling outward."""
        lx, ly = hand1_pos
        rx, ry = hand2_pos
        if (rx - lx) > (self.initial_marker_dist + 20.0) or (h2_dx - h1_dx > 40.0):
            self.separation_progress = 1.0
            self.is_opened = True
            return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_opened:
            return

        cx, cy = int(self.center_x), int(self.center_y)
        spread_offset = self.separation_progress * 110.0

        lx = int(self.left_marker[0] - spread_offset)
        rx = int(self.right_marker[1] if False else self.right_marker[0] + spread_offset)
        my = int(self.center_y)

        # Connecting glowing barrier line
        pulse = math.sin(self.pulse_phase)
        alpha = int(180 + 60 * pulse)
        line_col = (*COLOR_PURPLE_MYSTIC[:3], alpha)
        tether_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(tether_surf, line_col, (lx, my), (rx, my), 4)
        surface.blit(tether_surf, (0, 0))

        # Left hand marker
        l_col = COLOR_NEON_TEAL if self.hands_engaged else COLOR_OCEAN_CYAN
        pygame.draw.circle(surface, l_col, (lx, my), 32, 3)
        font = pygame.font.SysFont("segoeui", 14, bold=True)
        lbl_l = font.render("LEFT ✋", True, COLOR_NEON_TEAL)
        surface.blit(lbl_l, (lx - lbl_l.get_width() // 2, my - 8))

        # Right hand marker
        r_col = COLOR_GOLD if self.hands_engaged else (220, 180, 50)
        pygame.draw.circle(surface, r_col, (rx, my), 32, 3)
        lbl_r = font.render("RIGHT ✋", True, COLOR_GOLD)
        surface.blit(lbl_r, (rx - lbl_r.get_width() // 2, my - 8))

        # Center banner
        prog_pct = int(self.separation_progress * 100)
        banner_font = pygame.font.SysFont("segoeui", 15, bold=True)
        text = f"ANCIENT SEAL: PLACE BOTH HANDS & PULL APART ({prog_pct}%)"
        text_surf = banner_font.render(text, True, COLOR_GOLD if self.hands_engaged else COLOR_WHITE)
        surface.blit(text_surf, (cx - text_surf.get_width() // 2, cy - 58))


class AncientGuardian:
    """
    The legendary stone guardian of the Sunken Temple of Atlantis (Section 42).
    Awakens in Level 5, charges energy shockwaves, and must be pacified by solving
    the Ancient Gesture Puzzle and breaking the Two-Handed Ancient Seal.
    """

    def __init__(self, x: float = 640.0, y: float = 180.0):
        self.x = x
        self.y = y
        self.alive = True
        self.is_pacified = False
        self.phase = 0.0
        self.eye_glow_phase = 0.0
        self.shockwave_timer = 6.0
        self.shockwaves: List[Tuple[float, float, float]] = []  # (cx, cy, radius)

    def update(self, dt: float) -> Tuple[bool, bool]:
        """
        Updates guardian.
        Returns: (spawned_shockwave: bool, damaged_player: bool)
        """
        self.phase += 2.0 * dt
        self.eye_glow_phase += 4.5 * dt

        if self.is_pacified:
            return False, False

        self.shockwave_timer -= dt
        spawned = False
        if self.shockwave_timer <= 0.0:
            self.shockwave_timer = random.uniform(7.0, 10.0)
            self.shockwaves.append((self.x, self.y + 30.0, 15.0))
            spawned = True

        # Expand shockwaves
        new_sw = []
        for sx, sy, sr in self.shockwaves:
            sr += 320.0 * dt
            if sr < 750.0:
                new_sw.append((sx, sy, sr))
        self.shockwaves = new_sw

        return spawned, False

    def check_shockwave_hit(self, px: float, py: float, shield_active: bool) -> bool:
        """Checks if expanding guardian shockwave impacts swimmer without shield."""
        if self.is_pacified:
            return False

        for sx, sy, sr in self.shockwaves:
            dist = math.hypot(px - sx, py - sy)
            if abs(dist - sr) < 28.0:
                if not shield_active:
                    return True
        return False

    def pacify(self) -> None:
        """Pacifies the guardian into eternal slumber."""
        self.is_pacified = True
        self.shockwaves.clear()

    def draw(self, surface: pygame.Surface) -> None:
        cx, cy = int(self.x), int(self.y)
        
        # Expanding shockwave rings
        for sx, sy, sr in self.shockwaves:
            r = int(sr)
            if r > 5:
                alpha = int(200 * max(0.0, 1.0 - (sr / 750.0)))
                sw_surf = pygame.Surface((r * 2 + 10, r * 2 + 10), pygame.SRCALPHA)
                pygame.draw.circle(sw_surf, (*COLOR_PURPLE_MYSTIC[:3], alpha), (r + 5, r + 5), r, 4)
                surface.blit(sw_surf, (int(sx) - r - 5, int(sy) - r - 5))

        # Colossal Stone Guardian Idol
        body_col = (60, 70, 85) if not self.is_pacified else (40, 80, 75)
        # Giant stone head
        head_poly = [
            (cx - 75, cy - 60),
            (cx + 75, cy - 60),
            (cx + 90, cy + 30),
            (cx + 45, cy + 85),
            (cx - 45, cy + 85),
            (cx - 90, cy + 30),
        ]
        pygame.draw.polygon(surface, body_col, head_poly)
        pygame.draw.polygon(surface, (35, 42, 54), head_poly, 3)

        # Mystical Glyphs / Runes
        rune_col = COLOR_PURPLE_MYSTIC if not self.is_pacified else COLOR_EMERALD
        pygame.draw.line(surface, rune_col, (cx - 45, cy - 25), (cx + 45, cy - 25), 3)
        pygame.draw.line(surface, rune_col, (cx, cy - 45), (cx, cy + 45), 3)

        # Bioluminescent Glowing Eyes
        eye_pulse = math.sin(self.eye_glow_phase)
        eye_alpha = int(200 + 55 * eye_pulse) if not self.is_pacified else 60
        eye_col = (*(COLOR_CORAL_RED if not self.is_pacified else COLOR_EMERALD)[:3], eye_alpha)
        
        eye_surf = pygame.Surface((50, 30), pygame.SRCALPHA)
        pygame.draw.ellipse(eye_surf, eye_col, (0, 0, 22, 14))
        pygame.draw.ellipse(eye_surf, eye_col, (28, 0, 22, 14))
        surface.blit(eye_surf, (cx - 25, cy - 10))

        # Guardian Status Badge
        font = pygame.font.SysFont("segoeui", 14, bold=True)
        title_txt = "ANCIENT GUARDIAN [PACIFIED] ✨" if self.is_pacified else "🏛️ ANCIENT GUARDIAN AWAKENED"
        txt_surf = font.render(title_txt, True, COLOR_EMERALD if self.is_pacified else COLOR_CORAL_RED)
        surface.blit(txt_surf, (cx - txt_surf.get_width() // 2, cy - 85))


class OceanEventManager:
    """Orchestrates dynamic ocean weather conditions, shark chases, and ancient mechanisms."""

    def __init__(self):
        self.condition: OceanCondition = OceanCondition.CALM_WATER
        self.condition_timer: float = 25.0
        self.puzzle: AncientGesturePuzzle = AncientGesturePuzzle()
        self.ancient_seal: TwoHandAncientSeal = TwoHandAncientSeal()
        self.guardian: AncientGuardian = AncientGuardian()

    def start_level(self, level_id: int) -> None:
        self.puzzle.reset_puzzle()
        self.ancient_seal.reset()
        self.guardian = AncientGuardian()
        if level_id == 1:
            self.condition = OceanCondition.CALM_WATER
        elif level_id == 2:
            self.condition = OceanCondition.LIGHT_CURRENT
        elif level_id == 3:
            self.condition = OceanCondition.DARK_WATER
        elif level_id == 4:
            self.condition = OceanCondition.STRONG_CURRENT
        else:
            self.condition = OceanCondition.TURBULENT_WATER
        self.condition_timer = 30.0

    def update(
        self,
        dt: float,
        level_id: int = 1,
        swimmer_pos: Optional[Tuple[float, float]] = None,
        is_dual_swimming: bool = False,
        **kwargs
    ) -> None:
        self.condition_timer -= dt
        if self.condition_timer <= 0.0:
            self.condition_timer = random.uniform(22.0, 35.0)
            if level_id >= 2:
                # Cycle conditions
                choices = [OceanCondition.CALM_WATER, OceanCondition.LIGHT_CURRENT, OceanCondition.STRONG_CURRENT]
                if level_id >= 3:
                    choices.append(OceanCondition.DARK_WATER)
                if level_id >= 4:
                    choices.append(OceanCondition.TURBULENT_WATER)
                self.condition = random.choice(choices)

        if level_id == 5:
            self.puzzle.update(dt)
            self.guardian.update(dt)

    def get_current_condition(self) -> OceanCondition:
        return self.condition

    def draw(self, surface: pygame.Surface) -> None:
        if self.puzzle.is_active:
            self.puzzle.draw(surface)
        if not self.guardian.is_pacified:
            self.guardian.draw(surface)
