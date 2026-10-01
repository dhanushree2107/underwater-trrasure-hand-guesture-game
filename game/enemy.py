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


class Jellyfish:
    """Bioluminescent electric jellyfish drifting in the abyssal layers."""

    def __init__(self, x: float = None, y: float = None):
        self.x = x if x is not None else random.uniform(80.0, SCREEN_WIDTH - 80.0)
        self.y = y if y is not None else random.uniform(150.0, SCREEN_HEIGHT - 120.0)
        self.radius = 24.0
        self.pulse_phase = random.uniform(0.0, math.pi * 2)
        self.drift_speed_y = random.uniform(28.0, 48.0)
        self.drift_dir_y = random.choice([-1, 1])
        self.deflected = False
        self.deflect_timer = 0.0

    def update(self, dt: float, current_active: bool = False) -> None:
        self.pulse_phase += 4.0 * dt
        if self.deflected:
            self.deflect_timer -= dt
            self.y -= 220.0 * dt
            if self.deflect_timer <= 0:
                self.deflected = False
        else:
            self.y += self.drift_speed_y * self.drift_dir_y * dt
            if self.y < 110.0:
                self.drift_dir_y = 1
            elif self.y > SCREEN_HEIGHT - 80.0:
                self.drift_dir_y = -1

        if current_active:
            self.x += 160.0 * dt
            if self.x > SCREEN_WIDTH + 40:
                self.x = -30.0

    def check_collision(self, px: float, py: float) -> bool:
        return distance(px, py, self.x, self.y) <= (self.radius + 18.0)

    def draw(self, surface: pygame.Surface) -> None:
        cx, cy = int(self.x), int(self.y)
        pulse = math.sin(self.pulse_phase)
        r = int(self.radius + pulse * 3.0)

        # Translucent neon bell surface
        bell_surf = pygame.Surface((r * 2 + 10, r * 2 + 10), pygame.SRCALPHA)
        alpha = int(170 + 50 * pulse)
        # Glowing bell dome
        pygame.draw.circle(bell_surf, (180, 80, 255, alpha), (r + 5, r + 5), r)
        pygame.draw.circle(bell_surf, (230, 180, 255, 230), (r + 5, r + 5), int(r * 0.65))
        pygame.draw.circle(bell_surf, (255, 255, 255, 255), (r + 5, r + 5), 3)
        surface.blit(bell_surf, (cx - r - 5, cy - r - 5))

        # Trailing electric tentacles
        for i in range(4):
            tx = cx - 12 + i * 8
            tentacle_pts = [(tx, cy + 4)]
            for s in range(1, 5):
                seg_y = cy + 4 + s * 9
                seg_x = tx + math.sin(self.pulse_phase * 1.5 + s + i) * 6.0
                tentacle_pts.append((seg_x, seg_y))
            if len(tentacle_pts) >= 2:
                pygame.draw.lines(surface, (200, 120, 255), False, tentacle_pts, 2)


class Whirlpool:
    """A swirling oceanic whirlpool that pulls the swimmer towards its center."""
    def __init__(self, x: float, y: float, radius: float = 85.0, duration: float = 14.0):
        self.x = x
        self.y = y
        self.radius = radius
        self.duration = duration
        self.life = duration
        self.angle = 0.0
        self.pull_force = 190.0
        self.swimmer_escaped = False
        self.was_in_danger = False

    def update(self, dt: float) -> bool:
        self.life -= dt
        self.angle += 3.8 * dt
        return self.life > 0

    def apply_suction(self, px: float, py: float) -> Tuple[float, float, bool, bool]:
        """
        Calculates suction force on swimmer.
        Returns (force_x, force_y, damaged: bool, escaped_event: bool).
        """
        dist = distance(px, py, self.x, self.y)
        influence_radius = self.radius * 2.0
        damaged = False
        escaped_event = False

        if dist < influence_radius:
            self.was_in_danger = True
            dx = self.x - px
            dy = self.y - py
            ndist = max(1.0, dist)
            factor = (1.0 - dist / influence_radius)
            fx = (dx / ndist) * self.pull_force * factor
            fy = (dy / ndist) * self.pull_force * factor

            if dist < 24.0:
                damaged = True
            return fx, fy, damaged, False
        else:
            if self.was_in_danger and not self.swimmer_escaped:
                self.swimmer_escaped = True
                escaped_event = True
            return 0.0, 0.0, False, escaped_event

    def draw(self, surface: pygame.Surface) -> None:
        cx, cy = int(self.x), int(self.y)
        r = int(self.radius)
        spiral_surf = pygame.Surface((r * 2 + 40, r * 2 + 40), pygame.SRCALPHA)
        scx, scy = r + 20, r + 20

        alpha = int(140 * min(1.0, self.life / 2.0))
        for arm in range(4):
            base_a = self.angle + arm * (math.pi / 2.0)
            points = []
            for step in range(12):
                step_r = (step / 12.0) * r
                step_a = base_a + (step * 0.35)
                ax = scx + math.cos(step_a) * step_r
                ay = scy + math.sin(step_a) * step_r
                points.append((ax, ay))
            if len(points) >= 2:
                pygame.draw.lines(spiral_surf, (*COLOR_OCEAN_CYAN[:3], alpha), False, points, 3)

        pygame.draw.circle(spiral_surf, (5, 20, 45, int(alpha * 1.2)), (scx, scy), int(r * 0.28))
        surface.blit(spiral_surf, (cx - scx, cy - scy))


class OctopusTentacle:
    """An undulating giant octopus tentacle that blocks paths and lashes out."""
    def __init__(self, base_x: float, base_y: float, target_y: float):
        self.base_x = base_x
        self.base_y = base_y
        self.target_y = target_y
        self.current_y = base_y
        self.phase = random.uniform(0, math.pi * 2)
        self.wave_speed = random.uniform(2.5, 3.8)
        self.width = random.uniform(22.0, 32.0)
        self.length = abs(base_y - target_y)

    def update(self, dt: float, extend_progress: float) -> None:
        self.phase += self.wave_speed * dt
        self.current_y = self.base_y + (self.target_y - self.base_y) * extend_progress

    def check_collision(self, px: float, py: float) -> bool:
        min_y = min(self.base_y, self.current_y)
        max_y = max(self.base_y, self.current_y)
        if min_y - 20 <= py <= max_y + 20:
            sway = math.sin(self.phase + (py * 0.02)) * 28.0
            tentacle_x = self.base_x + sway
            if abs(px - tentacle_x) < (self.width + 18.0):
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        steps = 14
        points = []
        dy = (self.current_y - self.base_y) / steps
        for i in range(steps + 1):
            curr_y = self.base_y + dy * i
            sway = math.sin(self.phase + (curr_y * 0.02)) * 28.0 * (i / steps)
            points.append((int(self.base_x + sway), int(curr_y)))

        if len(points) >= 2:
            pygame.draw.lines(surface, (140, 35, 75), False, points, int(self.width))
            pygame.draw.lines(surface, (200, 70, 110), False, points, max(2, int(self.width * 0.4)))


class OctopusAmbush:
    """A surprise octopus ambush event with multiple undulating tentacles."""
    def __init__(self, duration: float = 12.0):
        self.duration = duration
        self.life = duration
        self.tentacles: List[OctopusTentacle] = [
            OctopusTentacle(base_x=220.0, base_y=SCREEN_HEIGHT + 40.0, target_y=SCREEN_HEIGHT - 320.0),
            OctopusTentacle(base_x=640.0, base_y=SCREEN_HEIGHT + 40.0, target_y=SCREEN_HEIGHT - 360.0),
            OctopusTentacle(base_x=1050.0, base_y=SCREEN_HEIGHT + 40.0, target_y=SCREEN_HEIGHT - 310.0),
        ]

    def update(self, dt: float) -> bool:
        self.life -= dt
        progress = min(1.0, (self.duration - self.life) / 1.5)
        if self.life < 1.5:
            progress = max(0.0, self.life / 1.5)

        for t in self.tentacles:
            t.update(dt, progress)
        return self.life > 0

    def check_collision(self, px: float, py: float) -> bool:
        return any(t.check_collision(px, py) for t in self.tentacles)

    def draw(self, surface: pygame.Surface) -> None:
        for t in self.tentacles:
            t.draw(surface)


class MarineLifeManager:
    """Manages swimming fish schools, occasional shark hazards, electric jellyfish, whirlpools, and octopus ambush."""

    def __init__(self, fish_count: int = 14):
        self.fish: List[Fish] = []
        for _ in range(fish_count):
            self.fish.append(Fish(x=random.uniform(0, SCREEN_WIDTH)))
        
        self.jellyfish: List[Jellyfish] = []
        self.current_shark: Optional[Shark] = None
        self.active_whirlpools: List[Whirlpool] = []
        self.current_octopus: Optional[OctopusAmbush] = None
        self.shark_warning_timer: float = 0.0
        self.shark_cooldown_timer: float = 22.0

    def spawn_jellyfish(self, count: int = 3) -> None:
        """Populates level with bioluminescent electric jellyfish."""
        self.jellyfish.clear()
        spacing = SCREEN_WIDTH // max(1, count + 1)
        for i in range(count):
            jx = spacing * (i + 1) + random.uniform(-40.0, 40.0)
            jy = random.uniform(140.0, SCREEN_HEIGHT - 130.0)
            self.jellyfish.append(Jellyfish(jx, jy))

    def trigger_shark_event(self) -> None:
        """Launches a shark warning followed by shark appearance."""
        if not self.current_shark and self.shark_warning_timer <= 0:
            self.shark_warning_timer = 2.5  # 2.5s warning banner before shark glides across

    def trigger_whirlpool(self, x: float = None, y: float = None) -> None:
        """Spawns an oceanic whirlpool pulling items and swimmer."""
        wx = x if x is not None else random.uniform(300.0, SCREEN_WIDTH - 300.0)
        wy = y if y is not None else random.uniform(220.0, SCREEN_HEIGHT - 220.0)
        self.active_whirlpools.append(Whirlpool(wx, wy))

    def trigger_octopus_ambush(self) -> None:
        """Triggers a giant octopus tentacle ambush."""
        if not self.current_octopus:
            self.current_octopus = OctopusAmbush(duration=13.0)

    def update(self, dt: float, current_active: bool = False, cursor_pos: Tuple[int, int] = None, shark_allowed: bool = False, shark_interval: float = 22.0) -> Tuple[bool, bool]:
        """
        Updates fish, jellyfish, shark, whirlpools, and octopus.
        Returns (shark_hit_player: bool, shark_deflected_by_shield: bool).
        """
        for f in self.fish:
            f.update(dt, current_active, cursor_pos)

        for j in self.jellyfish:
            j.update(dt, current_active)

        # Update Whirlpools
        self.active_whirlpools = [w for w in self.active_whirlpools if w.update(dt)]

        # Update Octopus Ambush
        if self.current_octopus:
            if not self.current_octopus.update(dt):
                self.current_octopus = None

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

    def check_jellyfish_interaction(self, px: float, py: float, shield_active: bool) -> Tuple[bool, bool]:
        """
        Checks collision between player and electric jellyfish.
        Returns (damaged: bool, deflected: bool).
        """
        for j in self.jellyfish:
            if not j.deflected and j.check_collision(px, py):
                if shield_active:
                    j.deflected = True
                    j.deflect_timer = 1.2
                    return False, True
                else:
                    j.deflected = True
                    j.deflect_timer = 1.0
                    return True, False
        return False, False

    def apply_whirlpools(self, px: float, py: float) -> Tuple[float, float, bool, bool]:
        """
        Calculates total suction displacement from whirlpools.
        Returns (total_fx, total_fy, damaged: bool, escaped_event: bool).
        """
        tot_fx, tot_fy = 0.0, 0.0
        dmg = False
        escaped = False
        for w in self.active_whirlpools:
            fx, fy, w_dmg, w_esc = w.apply_suction(px, py)
            tot_fx += fx
            tot_fy += fy
            if w_dmg:
                dmg = True
            if w_esc:
                escaped = True
        return tot_fx, tot_fy, dmg, escaped

    def check_octopus_interaction(self, px: float, py: float) -> bool:
        """Returns True if player swimmer touches an active octopus tentacle."""
        if self.current_octopus:
            return self.current_octopus.check_collision(px, py)
        return False

    def draw(self, surface: pygame.Surface) -> None:
        # Draw Whirlpools on sea backdrop
        for w in self.active_whirlpools:
            w.draw(surface)

        # Draw Octopus Ambush Tentacles
        if self.current_octopus:
            self.current_octopus.draw(surface)

        for f in self.fish:
            f.draw(surface)

        for j in self.jellyfish:
            j.draw(surface)

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
