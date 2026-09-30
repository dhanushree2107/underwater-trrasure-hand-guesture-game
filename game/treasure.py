"""
Underwater Treasure Hunt - Treasure System & Collection Depot
Defines all treasure archetypes, deceptive fake treasures, dangerous traps,
and the seafloor Treasure Chest collection depot where relics are deposited.
"""

from enum import Enum
import math
import random
import time
from typing import List, Optional, Tuple
import pygame

from config import (
    SCORE_COMMON,
    SCORE_GOLD,
    SCORE_RARE,
    SCORE_ANCIENT,
    SCORE_FAKE_PENALTY,
    FAKE_TREASURE_OXYGEN_PENALTY,
    TRAP_OXYGEN_PENALTY,
    SONAR_REVEAL_DURATION,
    DEPOSIT_ZONE_RADIUS,
    COLOR_GOLD,
    COLOR_NEON_TEAL,
    COLOR_OCEAN_CYAN,
    COLOR_CORAL_RED,
    COLOR_AMBER_WARNING,
    COLOR_PURPLE_MYSTIC,
    COLOR_EMERALD,
    COLOR_WHITE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)
from game.collision import point_in_circle, distance

class TreasureType(Enum):
    COMMON = "COMMON"
    GOLD = "GOLD"
    RARE = "RARE"
    ANCIENT = "ANCIENT"
    FAKE = "FAKE"
    TRAP = "TRAP"

class Treasure:
    """An interactive underwater item that can be grabbed, carried, and deposited."""

    def __init__(self, x: float, y: float, treasure_type: TreasureType):
        self.x = x
        self.y = y
        self.base_y = y
        self.type = treasure_type
        self.radius = 30.0
        self.collected = False     # True once successfully deposited into the chest
        self.is_carried = False    # True while swimmer is actively carrying it
        self.revealed_timer = 0.0

        # Animation state
        self.float_phase = random.uniform(0.0, math.pi * 2)
        self.float_speed = random.uniform(1.8, 2.6)
        self.float_amp = random.uniform(4.0, 8.0)
        self.shimmer_phase = random.uniform(0.0, math.pi * 2)

        # Configure score & oxygen impacts
        if self.type == TreasureType.COMMON:
            self.score_value = SCORE_COMMON
            self.oxygen_penalty = 0.0
            self.base_color = (210, 180, 140)  # Bronze / Shell
        elif self.type == TreasureType.GOLD:
            self.score_value = SCORE_GOLD
            self.oxygen_penalty = 0.0
            self.base_color = COLOR_GOLD
        elif self.type == TreasureType.RARE:
            self.score_value = SCORE_RARE
            self.oxygen_penalty = 0.0
            self.base_color = COLOR_OCEAN_CYAN
        elif self.type == TreasureType.ANCIENT:
            self.score_value = SCORE_ANCIENT
            self.oxygen_penalty = 0.0
            self.base_color = COLOR_PURPLE_MYSTIC
        elif self.type == TreasureType.FAKE:
            self.score_value = SCORE_FAKE_PENALTY
            self.oxygen_penalty = FAKE_TREASURE_OXYGEN_PENALTY
            # Visually disguises itself as a Gold or Rare treasure
            self.base_color = COLOR_GOLD if random.random() < 0.6 else COLOR_OCEAN_CYAN
        elif self.type == TreasureType.TRAP:
            self.score_value = 0
            self.oxygen_penalty = TRAP_OXYGEN_PENALTY
            self.base_color = (70, 75, 85)  # Spiked iron naval mine
            self.radius = 34.0

    def update(self, dt: float, current_force_x: float = 0.0) -> None:
        if self.collected:
            return

        self.shimmer_phase += 3.5 * dt

        if not self.is_carried:
            # Gentle bobbing on seabed
            self.float_phase += self.float_speed * dt
            self.y = self.base_y + math.sin(self.float_phase) * self.float_amp
            
            # Drift slightly when water current is active
            if current_force_x != 0:
                self.x += current_force_x * 0.25 * dt
                self.x = max(60.0, min(SCREEN_WIDTH - 60.0, self.x))

        if self.revealed_timer > 0:
            self.revealed_timer -= dt

    def drop(self, drop_x: float, drop_y: float) -> None:
        """Drops treasure back into the environment if released outside the chest."""
        self.is_carried = False
        self.x = drop_x
        # Sinks back towards seafloor
        self.base_y = min(SCREEN_HEIGHT - 90.0, max(120.0, drop_y + 35.0))
        self.y = self.base_y

    def reveal(self, duration: float = SONAR_REVEAL_DURATION) -> None:
        """Reveals true identity when swept by Sonar."""
        self.revealed_timer = duration

    def is_hovered(self, cursor_x: float, cursor_y: float) -> bool:
        """Checks if player swimmer or cursor is within grabbing distance."""
        if self.collected:
            return False
        return point_in_circle(cursor_x, cursor_y, self.x, self.y, self.radius + 26.0)

    def draw(self, surface: pygame.Surface) -> None:
        """Draws the procedural representation of the treasure."""
        if self.collected:
            return

        cx, cy = int(self.x), int(self.y)
        r = int(self.radius)

        # 1. Outer Glow (Intensifies when carried)
        glow_alpha = int(95 + 40 * math.sin(self.shimmer_phase)) if self.is_carried else int(45 + 25 * math.sin(self.shimmer_phase))
        glow_surf = pygame.Surface((r * 2 + 30, r * 2 + 30), pygame.SRCALPHA)
        glow_color = (*self.base_color[:3], glow_alpha)
        pygame.draw.circle(glow_surf, glow_color, (r + 15, r + 15), r + (14 if self.is_carried else 10))
        surface.blit(glow_surf, (cx - r - 15, cy - r - 15))

        # 2. Main Object Shape by Type
        if self.type == TreasureType.TRAP:
            # Spiked Naval Sea Mine
            pygame.draw.circle(surface, (45, 50, 58), (cx, cy), r - 6)
            pygame.draw.circle(surface, (70, 78, 88), (cx, cy), r - 10)
            for angle_deg in range(0, 360, 45):
                rad = math.radians(angle_deg)
                sx = cx + math.cos(rad) * (r + 3)
                sy = cy + math.sin(rad) * (r + 3)
                pygame.draw.line(surface, (30, 35, 42), (cx, cy), (int(sx), int(sy)), 5)
                pygame.draw.circle(surface, (200, 40, 40), (int(sx), int(sy)), 3)
            led_blink = (int(time.time() * 4) % 2) == 0
            led_color = (255, 30, 30) if led_blink else (90, 10, 10)
            pygame.draw.circle(surface, led_color, (cx, cy), 5)

        elif self.type == TreasureType.COMMON:
            # Pearl in a Clam Shell
            shell_rect = pygame.Rect(cx - r + 4, cy - r // 2, (r - 4) * 2, r)
            pygame.draw.ellipse(surface, (205, 175, 145), shell_rect)
            pygame.draw.circle(surface, (245, 245, 255), (cx, cy - 2), r // 2)
            pygame.draw.circle(surface, COLOR_WHITE, (cx - 3, cy - 5), max(2, r // 5))

        elif self.type in (TreasureType.GOLD, TreasureType.FAKE):
            # Golden Chest / Ingot Pile
            chest_w = int(r * 1.5)
            chest_h = int(r * 1.1)
            chest_rect = pygame.Rect(cx - chest_w // 2, cy - chest_h // 2, chest_w, chest_h)
            pygame.draw.rect(surface, (185, 130, 25), chest_rect, border_radius=6)
            pygame.draw.rect(surface, COLOR_GOLD, chest_rect, width=3, border_radius=6)
            pygame.draw.line(surface, COLOR_GOLD, (cx - chest_w // 2, cy), (cx + chest_w // 2, cy), 3)
            pygame.draw.circle(surface, (255, 240, 140), (cx, cy), 5)
            pygame.draw.circle(surface, (20, 20, 20), (cx, cy + 1), 2)

        elif self.type == TreasureType.RARE:
            # Sapphire Relic / Chalice
            poly = [
                (cx - r // 2, cy - r // 2),
                (cx + r // 2, cy - r // 2),
                (cx + r // 4, cy + r // 6),
                (cx + 4, cy + r // 3),
                (cx + r // 3, cy + r // 2),
                (cx - r // 3, cy + r // 2),
                (cx - 4, cy + r // 3),
                (cx - r // 4, cy + r // 6),
            ]
            pygame.draw.polygon(surface, COLOR_OCEAN_CYAN, poly)
            pygame.draw.polygon(surface, COLOR_WHITE, poly, 2)
            pygame.draw.circle(surface, (100, 230, 255), (cx, cy - 4), 6)

        elif self.type == TreasureType.ANCIENT:
            # Mythical Sunken Crown of Atlantis
            crown_poly = [
                (cx - r + 4, cy + r // 3),
                (cx - r + 4, cy - r // 4),
                (cx - r // 2, cy - r // 2),
                (cx, cy - r // 4),
                (cx + r // 2, cy - r // 2),
                (cx + r - 4, cy - r // 4),
                (cx + r - 4, cy + r // 3),
            ]
            pygame.draw.polygon(surface, COLOR_GOLD, crown_poly)
            pygame.draw.polygon(surface, (255, 245, 180), crown_poly, 2)
            pygame.draw.circle(surface, COLOR_CORAL_RED, (cx - r // 2, cy - r // 2 + 4), 4)
            pygame.draw.circle(surface, COLOR_EMERALD, (cx, cy - r // 4 + 4), 5)
            pygame.draw.circle(surface, COLOR_CORAL_RED, (cx + r // 2, cy - r // 2 + 4), 4)

        # 3. Sonar Reveal Aura / Overlay
        if self.revealed_timer > 0:
            reveal_alpha = int(220 * min(1.0, self.revealed_timer / 0.8))
            halo_surf = pygame.Surface((r * 2 + 24, r * 2 + 24), pygame.SRCALPHA)
            
            if self.type == TreasureType.TRAP:
                halo_color = (*COLOR_CORAL_RED[:3], reveal_alpha)
                pygame.draw.circle(halo_surf, halo_color, (r + 12, r + 12), r + 8, 3)
                font = pygame.font.SysFont("segoeui", 14, bold=True)
                tag = font.render("TRAP!", True, COLOR_CORAL_RED)
                surface.blit(tag, (cx - tag.get_width() // 2, cy - r - 22))

            elif self.type == TreasureType.FAKE:
                halo_color = (*COLOR_AMBER_WARNING[:3], reveal_alpha)
                pygame.draw.circle(halo_surf, halo_color, (r + 12, r + 12), r + 8, 3)
                font = pygame.font.SysFont("segoeui", 14, bold=True)
                tag = font.render("FAKE!", True, COLOR_AMBER_WARNING)
                surface.blit(tag, (cx - tag.get_width() // 2, cy - r - 22))

            else:
                halo_color = (*COLOR_EMERALD[:3], reveal_alpha)
                pygame.draw.circle(halo_surf, halo_color, (r + 12, r + 12), r + 8, 3)
                font = pygame.font.SysFont("segoeui", 14, bold=True)
                tag = font.render(f"+{self.score_value}", True, COLOR_EMERALD)
                surface.blit(tag, (cx - tag.get_width() // 2, cy - r - 22))

            surface.blit(halo_surf, (cx - r - 12, cy - r - 12))


class TreasureChest:
    """The underwater collection depot where swimmers deposit gathered relics."""

    def __init__(self, x: float = 160.0, y: float = SCREEN_HEIGHT - 80.0):
        self.x = x
        self.y = y
        self.radius = DEPOSIT_ZONE_RADIUS
        self.lid_open_pct = 0.0
        self.beacon_phase = 0.0
        self.deposited_count = 0
        self.rect = pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), int(self.radius * 2), int(self.radius * 2))

    def is_in_deposit_zone(self, px: float, py: float) -> bool:
        """Checks if player swimmer is within collection range of the chest."""
        return distance(px, py, self.x, self.y) <= self.radius

    def update(self, dt: float, player_is_near: bool) -> None:
        self.beacon_phase += 3.5 * dt
        target_open = 1.0 if player_is_near else 0.0
        self.lid_open_pct += (target_open - self.lid_open_pct) * min(1.0, 10.0 * dt)

    def draw(self, surface: pygame.Surface) -> None:
        cx, cy = int(self.x), int(self.y)
        
        # 1. Volumetric Glowing Deposit Beacon (Rises upward towards surface)
        pulse = math.sin(self.beacon_phase)
        beacon_alpha = int(35 + 20 * pulse)
        beacon_w = int(70 + 10 * pulse)
        beacon_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        beacon_poly = [
            (cx - beacon_w // 2, cy),
            (cx + beacon_w // 2, cy),
            (cx + beacon_w // 4, 0),
            (cx - beacon_w // 4, 0),
        ]
        pygame.draw.polygon(beacon_surf, (*COLOR_EMERALD[:3], beacon_alpha), beacon_poly)
        surface.blit(beacon_surf, (0, 0))

        # 2. Deposit Zone Ring on Seabed
        ring_r = int(self.radius)
        ring_alpha = int(120 + 50 * pulse)
        ring_surf = pygame.Surface((ring_r * 2 + 10, ring_r * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (*COLOR_EMERALD[:3], ring_alpha), (ring_r + 5, ring_r + 5), ring_r, 2)
        surface.blit(ring_surf, (cx - ring_r - 5, cy - ring_r - 5))

        # 3. Heavy Iron & Gold Ancient Vault Chest
        chest_w = 64
        chest_h = 42
        chest_x = cx - chest_w // 2
        chest_y = cy - chest_h // 2

        # Base Chest Body
        pygame.draw.rect(surface, (120, 80, 25), (chest_x, chest_y, chest_w, chest_h), border_radius=6)
        pygame.draw.rect(surface, (60, 40, 15), (chest_x, chest_y, chest_w, chest_h), width=2, border_radius=6)
        # Gold Riveted Bands
        pygame.draw.rect(surface, COLOR_GOLD, (chest_x + 8, chest_y, 8, chest_h))
        pygame.draw.rect(surface, COLOR_GOLD, (chest_x + chest_w - 16, chest_y, 8, chest_h))

        # Animated Chest Lid (Tilts open when swimmer is near)
        lid_h = 16
        lid_offset_y = int(self.lid_open_pct * 14)
        lid_rect = pygame.Rect(chest_x - 3, chest_y - 8 - lid_offset_y, chest_w + 6, lid_h)
        pygame.draw.rect(surface, (150, 100, 35), lid_rect, border_radius=5)
        pygame.draw.rect(surface, COLOR_GOLD, lid_rect, width=2, border_radius=5)
        
        # Golden Keyhole Emblem
        pygame.draw.circle(surface, COLOR_GOLD, (cx, chest_y + 16), 5)
        pygame.draw.circle(surface, (20, 20, 20), (cx, chest_y + 17), 2)

        # Deposit Depot Sign Label
        font = pygame.font.SysFont("segoeui", 14, bold=True)
        label_surf = font.render("TREASURE DEPOT", True, COLOR_EMERALD)
        surface.blit(label_surf, (cx - label_surf.get_width() // 2, cy + 28))


class TreasureManager:
    """Spawns, updates, reveals, and tracks all treasures and the collection depot."""

    def __init__(self):
        self.treasures: List[Treasure] = []
        self.chest: TreasureChest = TreasureChest()

    def clear(self) -> None:
        self.treasures.clear()

    def spawn_level_treasures(
        self,
        common_count: int,
        gold_count: int,
        rare_count: int,
        ancient_count: int,
        fake_count: int,
        trap_count: int,
        screen_w: int = 1280,
        screen_h: int = 720
    ) -> None:
        """Spawns treasures across sea floor away from deposit chest."""
        self.clear()
        
        # Place deposit chest on seabed
        chest_x = 150.0
        chest_y = screen_h - 75.0
        self.chest = TreasureChest(x=chest_x, y=chest_y)

        min_x = 260
        max_x = screen_w - 90
        min_y = 140
        max_y = screen_h - 110

        specs = (
            [(TreasureType.COMMON, 1) for _ in range(common_count)] +
            [(TreasureType.GOLD, 1) for _ in range(gold_count)] +
            [(TreasureType.RARE, 1) for _ in range(rare_count)] +
            [(TreasureType.ANCIENT, 1) for _ in range(ancient_count)] +
            [(TreasureType.FAKE, 1) for _ in range(fake_count)] +
            [(TreasureType.TRAP, 1) for _ in range(trap_count)]
        )
        random.shuffle(specs)

        for t_type, _ in specs:
            placed = False
            for _ in range(80):
                candidate_x = random.uniform(min_x, max_x)
                candidate_y = random.uniform(min_y, max_y)
                # Keep distance from chest and other treasures
                if distance(candidate_x, candidate_y, chest_x, chest_y) > 130.0:
                    if all(distance(candidate_x, candidate_y, t.x, t.y) > 85.0 for t in self.treasures):
                        self.treasures.append(Treasure(candidate_x, candidate_y, t_type))
                        placed = True
                        break
            if not placed:
                self.treasures.append(Treasure(random.uniform(min_x, max_x), random.uniform(min_y, max_y), t_type))

    def update(self, dt: float, current_active: bool = False, player_pos: Tuple[float, float] = None) -> None:
        force = 120.0 if current_active else 0.0
        for t in self.treasures:
            t.update(dt, force)

        player_is_near = False
        if player_pos:
            px, py = player_pos
            player_is_near = self.chest.is_in_deposit_zone(px, py)
        self.chest.update(dt, player_is_near)

    def trigger_sonar_wave(self, center_x: float, center_y: float, wave_radius: float) -> None:
        """Reveals treasures touched by expanding sonar wavefront."""
        for t in self.treasures:
            if not t.collected:
                dist = distance(center_x, center_y, t.x, t.y)
                if abs(dist - wave_radius) < 65.0 or dist < wave_radius:
                    t.reveal()

    def get_hovered_treasure(self, cursor_x: float, cursor_y: float) -> Optional[Treasure]:
        """Returns the first uncollected, uncarried treasure within reach."""
        for t in self.treasures:
            if t.is_hovered(cursor_x, cursor_y):
                return t
        return None

    def draw(self, surface: pygame.Surface) -> None:
        # Draw Seafloor Deposit Vault Chest
        self.chest.draw(surface)

        # Draw Uncollected Treasures
        for t in self.treasures:
            t.draw(surface)

    def remaining_real_treasures(self) -> int:
        """Returns count of remaining uncollected genuine relics."""
        return sum(1 for t in self.treasures if not t.collected and t.type not in (TreasureType.FAKE, TreasureType.TRAP))
