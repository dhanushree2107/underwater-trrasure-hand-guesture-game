"""
Underwater Treasure Hunt - Autonomous Marine Life & Predators
Implements procedural fish schools with swimming kinematics and
shark apex predator events with shield deflection mechanics.
"""

import math
import random
import time
from typing import List, Optional, Tuple
import pygame

from config import (
    COLOR_CORAL_RED,
    COLOR_OCEAN_CYAN,
    COLOR_GOLD,
    COLOR_WHITE,
    SHARK_OXYGEN_PENALTY,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)
from game.collision import point_in_circle, distance

class Fish:
    """An autonomous swimming fish with natural body flexion and tail undulation."""

    def __init__(self, x: float = None, y: float = None):
        self.direction = random.choice([-1, 1])  # 1 = moving right, -1 = moving left
        if x is None:
            self.x = -40.0 if self.direction == 1 else SCREEN_WIDTH + 40.0
        else:
            self.x = x
        self.y = y if y is not None else random.uniform(80.0, SCREEN_HEIGHT - 60.0)
        self.base_y = self.y
        self.speed = random.uniform(55.0, 130.0)
        self.size = random.uniform(14.0, 24.0)
        
        # Color palette by random species
        species = random.choice(["clown", "blue_tang", "silver", "gold"])
        if species == "clown":
            self.color_body = (245, 110, 30)
            self.color_accent = COLOR_WHITE
        elif species == "blue_tang":
            self.color_body = (20, 80, 220)
            self.color_accent = COLOR_GOLD
        elif species == "gold":
            self.color_body = COLOR_GOLD
            self.color_accent = (255, 120, 40)
        else:
            self.color_body = (180, 200, 215)
            self.color_accent = (100, 160, 200)

        self.swim_phase = random.uniform(0, math.pi * 2)
        self.tail_phase = random.uniform(0, math.pi * 2)
        self.tail_speed = random.uniform(8.0, 14.0)

    def update(self, dt: float, current_active: bool = False, cursor_pos: Tuple[int, int] = None) -> None:
        self.tail_phase += self.tail_speed * dt
        self.swim_phase += 2.0 * dt
        
        # Base swimming propulsion
        vx = self.speed * self.direction
        
        # React to Water Current
        if current_active:
            vx += 180.0

        # Avoid cursor if it gets very close (fright / scatter response)
        if cursor_pos:
            cx, cy = cursor_pos
            dist_to_cursor = distance(self.x, self.y, cx, cy)
            if dist_to_cursor < 75.0:
                push = (75.0 - dist_to_cursor) * 1.5
                if self.x < cx:
                    vx -= push
                else:
                    vx += push
                self.y += math.sin(self.swim_phase) * 2.0

        self.x += vx * dt
        self.y = self.base_y + math.sin(self.swim_phase) * 6.0

        # Wrap around screen edges
        if self.direction == 1 and self.x > SCREEN_WIDTH + 60:
            self.x = -50.0
            self.base_y = random.uniform(80.0, SCREEN_HEIGHT - 60.0)
        elif self.direction == -1 and self.x < -60:
            self.x = SCREEN_WIDTH + 50.0
            self.base_y = random.uniform(80.0, SCREEN_HEIGHT - 60.0)

    def draw(self, surface: pygame.Surface) -> None:
        cx, cy = int(self.x), int(self.y)
        s = self.size
        d = self.direction

        # Tail wag offset
        tail_wag = math.sin(self.tail_phase) * (s * 0.35)

        # Elliptical fish body
        body_rect = pygame.Rect(cx - int(s * 0.8), cy - int(s * 0.45), int(s * 1.6), int(s * 0.9))
        pygame.draw.ellipse(surface, self.color_body, body_rect)

        # Tail fin polygon
        tail_tip_x = cx - int(d * s * 1.1)
        tail_poly = [
            (cx - int(d * s * 0.6), cy),
            (tail_tip_x, int(cy - s * 0.5 + tail_wag)),
            (tail_tip_x, int(cy + s * 0.5 + tail_wag)),
        ]
        pygame.draw.polygon(surface, self.color_accent, tail_poly)

        # Dorsal fin
        dorsal_poly = [
            (cx - int(d * s * 0.2), int(cy - s * 0.4)),
            (cx, int(cy - s * 0.75)),
            (cx + int(d * s * 0.3), int(cy - s * 0.35)),
        ]
        pygame.draw.polygon(surface, self.color_accent, dorsal_poly)

        # Eye
        eye_x = cx + int(d * s * 0.45)
        eye_y = cy - int(s * 0.1)
        pygame.draw.circle(surface, COLOR_WHITE, (eye_x, eye_y), max(2, int(s * 0.16)))
        pygame.draw.circle(surface, (20, 20, 20), (eye_x + int(d * 1), eye_y), max(1, int(s * 0.08)))


class Shark:
    """An apex predator patrolling the depth layers."""

    def __init__(self, direction: int = 1):
        self.direction = direction  # 1 = left-to-right, -1 = right-to-left
        self.x = -160.0 if direction == 1 else SCREEN_WIDTH + 160.0
        self.y = random.uniform(180.0, SCREEN_HEIGHT - 160.0)
        self.speed = 220.0
        self.width = 140.0
        self.height = 50.0
        self.alive = True
        self.tail_phase = 0.0
        self.deflected = False

    def update(self, dt: float) -> None:
        self.tail_phase += 7.0 * dt
        self.x += self.speed * self.direction * dt
        
        # Check boundary exit
        if self.direction == 1 and self.x > SCREEN_WIDTH + 200:
            self.alive = False
        elif self.direction == -1 and self.x < -200:
            self.alive = False

    def check_cursor_collision(self, cursor_x: float, cursor_y: float) -> bool:
        """Checks if player cursor collides with shark body or jaws."""
        return point_in_circle(cursor_x, cursor_y, self.x, self.y, 45.0)

    def draw(self, surface: pygame.Surface) -> None:
        if not self.alive:
            return

        cx, cy = int(self.x), int(self.y)
        d = self.direction
        tail_wag = math.sin(self.tail_phase) * 14.0

        # Shark Body (Sleek slate-gray torpedo)
        body_color = (65, 80, 95)
        belly_color = (195, 205, 215)
        
        # Upper body polygon
        body_poly = [
            (cx + int(d * 70), cy),                     # Snout tip
            (cx + int(d * 30), cy - 22),                 # Forehead
            (cx - int(d * 20), cy - 18),                 # Back
            (cx - int(d * 60), cy - 8),                  # Peduncle
            (cx - int(d * 80), int(cy - 25 + tail_wag)), # Upper caudal fin tip
            (cx - int(d * 68), int(cy + tail_wag)),      # Caudal fork
            (cx - int(d * 80), int(cy + 22 + tail_wag)), # Lower caudal fin tip
            (cx - int(d * 45), cy + 12),                 # Lower belly
            (cx + int(d * 20), cy + 14),                 # Ventral
        ]
        pygame.draw.polygon(surface, body_color, body_poly)

        # Dorsal Fin
        dorsal_poly = [
            (cx - int(d * 10), cy - 18),
            (cx - int(d * 2), cy - 44),
            (cx + int(d * 18), cy - 16),
        ]
        pygame.draw.polygon(surface, body_color, dorsal_poly)

        # Pectoral Fin
        pec_poly = [
            (cx + int(d * 15), cy + 8),
            (cx - int(d * 10), cy + 32),
            (cx - int(d * 15), cy + 10),
        ]
        pygame.draw.polygon(surface, (50, 65, 78), pec_poly)

        # Eye & Gill slits
        eye_x = cx + int(d * 48)
        eye_y = cy - 6
        pygame.draw.circle(surface, (20, 20, 20), (eye_x, eye_y), 4)
        pygame.draw.circle(surface, COLOR_WHITE, (eye_x + d, eye_y - 1), 1)

        # Gills
        for g in range(3):
            gx = cx + int(d * (25 - g * 6))
            pygame.draw.line(surface, (40, 50, 60), (gx, cy - 8), (gx, cy + 8), 2)


class MarineLifeManager:
    """Manages swimming fish schools and occasional shark hazards."""

    def __init__(self, fish_count: int = 14):
        self.fish: List[Fish] = []
        for _ in range(fish_count):
            self.fish.append(Fish(x=random.uniform(0, SCREEN_WIDTH)))
        
        self.current_shark: Optional[Shark] = None
        self.shark_warning_timer: float = 0.0
        self.shark_cooldown_timer: float = 22.0

    def trigger_shark_event(self) -> None:
        """Launches a shark warning followed by shark appearance."""
        if not self.current_shark and self.shark_warning_timer <= 0:
            self.shark_warning_timer = 2.5  # 2.5s warning banner before shark glides across

    def update(self, dt: float, current_active: bool = False, cursor_pos: Tuple[int, int] = None, shark_allowed: bool = False, shark_interval: float = 22.0) -> Tuple[bool, bool]:
        """
        Updates fish and shark.
        Returns (shark_hit_player: bool, shark_deflected_by_shield: bool).
        """
        for f in self.fish:
            f.update(dt, current_active, cursor_pos)

        hit = False
        deflected = False

        if shark_allowed:
            self.shark_cooldown_timer -= dt
            if self.shark_cooldown_timer <= 0 and not self.current_shark and self.shark_warning_timer <= 0:
                self.trigger_shark_event()
                self.shark_cooldown_timer = shark_interval

        # Shark Warning Banner Countdown
        if self.shark_warning_timer > 0:
            self.shark_warning_timer -= dt
            if self.shark_warning_timer <= 0:
                # Spawn Shark
                direction = random.choice([-1, 1])
                self.current_shark = Shark(direction)

        # Update Active Shark
        if self.current_shark:
            self.current_shark.update(dt)
            if not self.current_shark.alive:
                self.current_shark = None

        return hit, deflected

    def check_shark_interaction(self, cursor_x: float, cursor_y: float, shield_active: bool) -> Tuple[bool, bool]:
        """
        Checks collision between player cursor and shark.
        Returns (damaged: bool, deflected: bool).
        """
        if not self.current_shark or not self.current_shark.alive:
            return False, False

        if self.current_shark.check_cursor_collision(cursor_x, cursor_y):
            if shield_active:
                if not self.current_shark.deflected:
                    self.current_shark.deflected = True
                    self.current_shark.speed *= 1.8  # Flee faster
                    return False, True
            else:
                return True, False

        return False, False

    def draw(self, surface: pygame.Surface) -> None:
        for f in self.fish:
            f.draw(surface)

        if self.current_shark:
            self.current_shark.draw(surface)

        # Draw Warning Banner if active
        if self.shark_warning_timer > 0:
            alpha = int(180 + 75 * math.sin(time.time() * 12))
            banner_surf = pygame.Surface((SCREEN_WIDTH, 50), pygame.SRCALPHA)
            banner_surf.fill((160, 20, 20, max(0, min(255, alpha))))
            
            font = pygame.font.SysFont("segoeui", 22, bold=True)
            text = font.render("⚠ WARNING: APEX PREDATOR DETECTED! ACTIVATE SHIELD [FIST ✊ / 'S'] ⚠", True, COLOR_WHITE)
            banner_surf.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 12))
            surface.blit(banner_surf, (0, 100))
