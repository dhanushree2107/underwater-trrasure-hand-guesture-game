"""
Underwater Treasure Hunt - Level Environment & Progression System
Handles all 5 thematic levels, procedural parallax seabeds, swaying corals,
ancient ruins, shipwrecks, depth fog, and victory/defeat evaluation.
"""

import math
import random
import time
from typing import Dict, List, Tuple
import pygame

from config import (
    LEVELS,
    LevelConfig,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_DEEP_BLUE,
    COLOR_OCEAN_CYAN,
    COLOR_NEON_TEAL,
    COLOR_GOLD,
    COLOR_WHITE,
)
from game.treasure import TreasureManager
from game.enemy import MarineLifeManager
from game.particles import ParticleSystem
from game.player import Player

class Seaweed:
    """Animated swaying kelp frond anchored to sea floor."""
    def __init__(self, x: float, height: float, color: Tuple[int, int, int]):
        self.x = x
        self.height = height
        self.color = color
        self.sway_phase = random.uniform(0.0, math.pi * 2)
        self.sway_speed = random.uniform(1.2, 2.2)
        self.sway_amp = random.uniform(18.0, 36.0)

    def draw(self, surface: pygame.Surface, current_active: bool = False) -> None:
        t = time.time()
        extra_sway = 22.0 if current_active else 0.0
        points = []
        segments = 6
        base_y = SCREEN_HEIGHT
        for i in range(segments + 1):
            ratio = i / segments
            y = base_y - self.height * ratio
            offset = math.sin(t * self.sway_speed + self.sway_phase + ratio * 2.0) * (self.sway_amp * ratio) + (extra_sway * ratio)
            points.append((self.x + offset, y))
        
        if len(points) >= 2:
            pygame.draw.lines(surface, self.color, False, points, 6)


class Level:
    """Represents an active game stage with custom environment, challenges, and goals."""

    def __init__(self, level_id: int):
        self.config: LevelConfig = LEVELS.get(level_id, LEVELS[1])
        self.level_id = level_id
        self.time_remaining: float = self.config.time_limit
        
        self.deposited_count: int = 0
        self.required_deposits: int = self.config.required_deposits

        # Managers
        self.treasure_manager = TreasureManager()
        self.marine_manager = MarineLifeManager(fish_count=12 + level_id * 2)
        
        # Scenery
        self.seaweeds: List[Seaweed] = []
        self._init_scenery()

        # Spawn Level Interactive Items
        self.treasure_manager.spawn_level_treasures(
            common_count=self.config.common_treasures,
            gold_count=self.config.gold_treasures,
            rare_count=self.config.rare_treasures,
            ancient_count=self.config.ancient_treasures,
            fake_count=self.config.fake_treasures,
            trap_count=self.config.traps,
            screen_w=SCREEN_WIDTH,
            screen_h=SCREEN_HEIGHT
        )

    def _init_scenery(self) -> None:
        """Constructs coral beds and kelp forest based on level depth."""
        kelp_colors = [
            (24, 88, 54),
            (18, 72, 45),
            (32, 108, 68),
            (14, 58, 38)
        ]
        # Place swaying kelp along seafloor
        for i in range(16):
            kx = (i * 85) + random.uniform(-20, 20)
            kh = random.uniform(120.0, 280.0)
            col = random.choice(kelp_colors)
            self.seaweeds.append(Seaweed(kx, kh, col))

    def update(self, dt: float, current_active: bool, cursor_pos: Tuple[int, int], shield_active: bool) -> Tuple[bool, bool, bool, bool]:
        """
        Updates level timers, marine life, and hazards.
        Returns:
            (is_level_complete, is_game_over, player_damaged_by_shark, shark_deflected)
        """
        self.time_remaining = max(0.0, self.time_remaining - dt)
        
        # Update Treasures & Collection Chest Depot
        self.treasure_manager.update(dt, current_active, player_pos=cursor_pos)

        # Update Marine Life & Sharks
        self.marine_manager.update(
            dt,
            current_active,
            cursor_pos,
            shark_allowed=self.config.shark_enabled,
            shark_interval=self.config.shark_interval
        )

        # Check Shark Collision
        cx, cy = cursor_pos
        shark_hit, shark_deflected = self.marine_manager.check_shark_interaction(cx, cy, shield_active)

        # Check Win/Loss conditions based on deposited relics objective
        is_level_complete = (self.deposited_count >= self.required_deposits)
        is_game_over = (self.time_remaining <= 0)

        return is_level_complete, is_game_over, shark_hit, shark_deflected

    def draw_background(self, surface: pygame.Surface, current_active: bool = False) -> None:
        """Renders realistic multi-depth underwater gradient, parallax seabed, and scenery."""
        # 1. Depth Gradient
        top_col = self.config.ambient_color
        bot_col = self.config.deep_color
        grad_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # 3-step vertical interpolation for smooth performance
        for y in range(0, SCREEN_HEIGHT, 4):
            t = y / SCREEN_HEIGHT
            r = int(top_col[0] + (bot_col[0] - top_col[0]) * t)
            g = int(top_col[1] + (bot_col[1] - top_col[1]) * t)
            b = int(top_col[2] + (bot_col[2] - top_col[2]) * t)
            pygame.draw.rect(grad_surf, (r, g, b), (0, y, SCREEN_WIDTH, 4))
        surface.blit(grad_surf, (0, 0))

        # 2. Level-Specific Thematic Scenery Backdrop
        if self.level_id == 4:
            # Level 4: Sunken Shipwreck Silhouette
            ship_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            hull_col = (12, 22, 34, 180)
            # Sunken hull
            hull_poly = [
                (140, SCREEN_HEIGHT),
                (160, SCREEN_HEIGHT - 180),
                (360, SCREEN_HEIGHT - 150),
                (540, SCREEN_HEIGHT - 170),
                (620, SCREEN_HEIGHT),
            ]
            pygame.draw.polygon(ship_surf, hull_col, hull_poly)
            # Tilted Mast & Yardarms
            pygame.draw.line(ship_surf, hull_col, (340, SCREEN_HEIGHT - 150), (320, SCREEN_HEIGHT - 380), 12)
            pygame.draw.line(ship_surf, hull_col, (260, SCREEN_HEIGHT - 310), (380, SCREEN_HEIGHT - 325), 6)
            surface.blit(ship_surf, (0, 0))

        elif self.level_id == 5:
            # Level 5: Sunken Ancient Temple of Atlantis
            temple_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pillar_col = (20, 32, 50, 190)
            # Ancient Pillars
            for px in (120, 240, SCREEN_WIDTH - 240, SCREEN_WIDTH - 120):
                pygame.draw.rect(temple_surf, pillar_col, (px, SCREEN_HEIGHT - 260, 48, 260))
                # Capital & Base
                pygame.draw.rect(temple_surf, pillar_col, (px - 10, SCREEN_HEIGHT - 275, 68, 16))
                pygame.draw.rect(temple_surf, pillar_col, (px - 6, SCREEN_HEIGHT - 20, 60, 20))
            # Ruined architrave
            pygame.draw.polygon(temple_surf, pillar_col, [
                (90, SCREEN_HEIGHT - 275),
                (280, SCREEN_HEIGHT - 275),
                (260, SCREEN_HEIGHT - 310),
                (110, SCREEN_HEIGHT - 310),
            ])
            surface.blit(temple_surf, (0, 0))

        # 3. Parallax Sandy Sea Floor
        seafloor_col = (int(bot_col[0] * 1.5 + 8), int(bot_col[1] * 1.5 + 14), int(bot_col[2] * 1.5 + 20))
        floor_points = [(0, SCREEN_HEIGHT)]
        for x in range(0, SCREEN_WIDTH + 50, 40):
            fy = SCREEN_HEIGHT - 55 + math.sin(x * 0.015) * 14.0
            floor_points.append((x, fy))
        floor_points.append((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.draw.polygon(surface, seafloor_col, floor_points)

        # 4. Swaying Seaweed
        for sw in self.seaweeds:
            sw.draw(surface, current_active)

    def draw_fog(self, surface: pygame.Surface) -> None:
        """Draws depth fog and ambient darkness overlay for deep water levels."""
        if self.config.visibility < 0.95:
            fog_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            fog_alpha = int(255 * (1.0 - self.config.visibility))
            fog_surf.fill((*self.config.deep_color[:3], max(0, min(230, fog_alpha))))
            surface.blit(fog_surf, (0, 0))
