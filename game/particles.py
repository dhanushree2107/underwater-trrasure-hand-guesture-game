"""
Underwater Treasure Hunt - Particle and Visual Effects System
Manages bubbles, light rays, sonar pulses, water current torrents,
score popups, marine snow, and explosion shockwaves.
"""

import math
import random
import time
from typing import List, Tuple
import pygame

from config import (
    COLOR_NEON_TEAL,
    COLOR_OCEAN_CYAN,
    COLOR_GOLD,
    COLOR_CORAL_RED,
    COLOR_AMBER_WARNING,
    COLOR_WHITE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)

class Bubble:
    """An ambient or burst rising underwater bubble."""
    def __init__(self, x: float, y: float, radius: float = None, speed: float = None, is_trail: bool = False):
        self.x = x
        self.y = y
        self.radius = radius or random.uniform(3.0, 9.0)
        self.base_radius = self.radius
        self.speed = speed or random.uniform(35.0, 90.0)
        self.wobble_phase = random.uniform(0, math.pi * 2)
        self.wobble_speed = random.uniform(2.0, 4.5)
        self.wobble_amp = random.uniform(1.0, 3.5)
        self.alpha = 180 if is_trail else random.randint(120, 220)
        self.alive = True
        self.lifetime = 1.8 if is_trail else 999.0
        self.age = 0.0

    def update(self, dt: float, current_force_x: float = 0.0) -> None:
        self.age += dt
        self.y -= self.speed * dt
        self.wobble_phase += self.wobble_speed * dt
        self.x += (math.sin(self.wobble_phase) * self.wobble_amp) + (current_force_x * dt)

        if self.lifetime < 900.0:
            fade_ratio = max(0.0, 1.0 - (self.age / self.lifetime))
            self.alpha = int(180 * fade_ratio)
            if self.age >= self.lifetime:
                self.alive = False

        if self.y < -20:
            self.alive = False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.alive or self.radius < 1.0:
            return
        r = int(self.radius)
        b_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        # Translucent sphere
        pygame.draw.circle(b_surf, (200, 245, 255, max(0, min(255, self.alpha))), (r + 2, r + 2), r, 2)
        # Highlight glint
        glint_offset = max(1, r // 3)
        pygame.draw.circle(b_surf, (255, 255, 255, max(0, min(255, int(self.alpha * 0.9)))), (r + 2 - glint_offset, r + 2 - glint_offset), max(1, r // 3))
        surface.blit(b_surf, (int(self.x - r - 2), int(self.y - r - 2)))


class ScorePopup:
    """Animated text floating upward and fading out upon scoring/penalty."""
    def __init__(self, x: float, y: float, text: str, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.lifetime = 1.3
        self.age = 0.0
        self.alive = True
        self.font = pygame.font.SysFont("segoeui", 26, bold=True)

    def update(self, dt: float) -> None:
        self.age += dt
        self.y -= 45.0 * dt
        if self.age >= self.lifetime:
            self.alive = False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.alive:
            return
        alpha = int(255 * (1.0 - (self.age / self.lifetime)))
        text_surf = self.font.render(self.text, True, self.color)
        alpha_surf = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA)
        alpha_surf.blit(text_surf, (0, 0))
        alpha_surf.set_alpha(max(0, min(255, alpha)))
        
        # Soft shadow
        shadow_surf = self.font.render(self.text, True, (10, 15, 30))
        shadow_alpha = pygame.Surface(shadow_surf.get_size(), pygame.SRCALPHA)
        shadow_alpha.blit(shadow_surf, (0, 0))
        shadow_alpha.set_alpha(max(0, min(255, int(alpha * 0.6))))
        
        surface.blit(shadow_alpha, (int(self.x - shadow_surf.get_width() // 2 + 2), int(self.y + 2)))
        surface.blit(alpha_surf, (int(self.x - text_surf.get_width() // 2), int(self.y)))


class SonarPulse:
    """Expanding glowing concentric rings indicating active sonar scan."""
    def __init__(self, center_x: float, center_y: float, max_radius: float = 750.0, speed: float = 450.0):
        self.x = center_x
        self.y = center_y
        self.radius = 10.0
        self.max_radius = max_radius
        self.speed = speed
        self.alive = True

    def update(self, dt: float) -> None:
        self.radius += self.speed * dt
        if self.radius >= self.max_radius:
            self.alive = False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.alive:
            return
        alpha_factor = max(0.0, 1.0 - (self.radius / self.max_radius))
        alpha = int(220 * alpha_factor)
        r = int(self.radius)
        if r <= 0:
            return

        # Main ring
        pulse_surf = pygame.Surface((r * 2 + 6, r * 2 + 6), pygame.SRCALPHA)
        color = (*COLOR_NEON_TEAL[:3], alpha)
        pygame.draw.circle(pulse_surf, color, (r + 3, r + 3), r, 3)

        # Subtle inner trailing ring
        if r > 25:
            inner_r = r - 18
            inner_color = (*COLOR_OCEAN_CYAN[:3], int(alpha * 0.5))
            pygame.draw.circle(pulse_surf, inner_color, (r + 3, r + 3), inner_r, 2)

        surface.blit(pulse_surf, (int(self.x - r - 3), int(self.y - r - 3)))


class CurrentStream:
    """Stream of flowing water particles emitted when water current is active."""
    def __init__(self, x: float, y: float, speed_x: float = 400.0):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.length = random.uniform(25.0, 60.0)
        self.thickness = random.randint(1, 3)
        self.alpha = random.randint(140, 220)
        self.alive = True
        self.lifetime = 1.8
        self.age = 0.0

    def update(self, dt: float) -> None:
        self.age += dt
        self.x += self.speed_x * dt
        if self.age >= self.lifetime or self.x > SCREEN_WIDTH + 50:
            self.alive = False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.alive:
            return
        fade = max(0.0, 1.0 - (self.age / self.lifetime))
        a = int(self.alpha * fade)
        surf = pygame.Surface((int(self.length) + 4, self.thickness + 4), pygame.SRCALPHA)
        pygame.draw.line(surf, (180, 240, 255, a), (0, 2), (int(self.length), 2), self.thickness)
        surface.blit(surf, (int(self.x), int(self.y)))


class Sparkle:
    """Sparkle particle for treasure discovery and collection bursts."""
    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(50.0, 180.0)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.lifetime = random.uniform(0.4, 0.8)
        self.age = 0.0
        self.size = random.uniform(2.5, 5.0)
        self.alive = True

    def update(self, dt: float) -> None:
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.94
        self.vy *= 0.94
        if self.age >= self.lifetime:
            self.alive = False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.alive:
            return
        alpha = int(255 * (1.0 - (self.age / self.lifetime)))
        s = int(self.size)
        surf = pygame.Surface((s * 2 + 2, s * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color[:3], max(0, min(255, alpha))), (s + 1, s + 1), s)
        surface.blit(surf, (int(self.x - s - 1), int(self.y - s - 1)))


class ParticleSystem:
    """Unified particle manager orchestrating all underwater visual effects."""

    def __init__(self):
        self.ambient_bubbles: List[Bubble] = []
        self.trail_bubbles: List[Bubble] = []
        self.score_popups: List[ScorePopup] = []
        self.sonar_pulses: List[SonarPulse] = []
        self.current_streams: List[CurrentStream] = []
        self.sparkles: List[Sparkle] = []

        # Light rays simulation parameters
        self.light_ray_phase = 0.0

        # Initialize ambient bubbles
        for _ in range(35):
            bx = random.uniform(0, SCREEN_WIDTH)
            by = random.uniform(0, SCREEN_HEIGHT)
            self.ambient_bubbles.append(Bubble(bx, by))

    def emit_cursor_trail(self, x: float, y: float) -> None:
        """Emits tiny trailing micro-bubbles behind cursor."""
        if random.random() < 0.45:
            self.trail_bubbles.append(Bubble(x + random.uniform(-4, 4), y + random.uniform(-4, 4), radius=random.uniform(1.8, 3.5), speed=random.uniform(20, 50), is_trail=True))

    def emit_treasure_burst(self, x: float, y: float, count: int = 18, color: Tuple[int, int, int] = COLOR_GOLD) -> None:
        """Explodes sparkling gold or jewel particles upon treasure collection."""
        for _ in range(count):
            self.sparkles.append(Sparkle(x, y, color))
            if random.random() < 0.6:
                self.trail_bubbles.append(Bubble(x, y, radius=random.uniform(2.5, 5.5), speed=random.uniform(60, 140), is_trail=True))

    def emit_score_popup(self, x: float, y: float, text: str, color: Tuple[int, int, int] = COLOR_GOLD) -> None:
        """Spawns an upward-drifting score indicator."""
        self.score_popups.append(ScorePopup(x, y, text, color))

    def emit_sonar_pulse(self, x: float, y: float) -> None:
        """Fires an expanding sonar wave from coordinates."""
        self.sonar_pulses.append(SonarPulse(x, y))

    def emit_water_current(self) -> None:
        """Emits a torrential burst of stream particles across the screen."""
        for _ in range(50):
            sx = random.uniform(-100, SCREEN_WIDTH * 0.5)
            sy = random.uniform(40, SCREEN_HEIGHT - 40)
            self.current_streams.append(CurrentStream(sx, sy, speed_x=random.uniform(350, 750)))

    def emit_trap_explosion(self, x: float, y: float) -> None:
        """Emits fiery red shockwave and dark debris particles for sea mines."""
        for _ in range(25):
            self.sparkles.append(Sparkle(x, y, COLOR_CORAL_RED))
        for _ in range(12):
            self.sparkles.append(Sparkle(x, y, COLOR_AMBER_WARNING))
        for _ in range(15):
            self.trail_bubbles.append(Bubble(x, y, radius=random.uniform(4.0, 9.0), speed=random.uniform(90, 200), is_trail=True))

    def update(self, dt: float, current_active: bool = False) -> None:
        """Updates physics and lifecycle of all particles."""
        self.light_ray_phase += dt * 0.8
        current_force = 160.0 if current_active else 0.0

        # Maintain ambient bubble count
        if len(self.ambient_bubbles) < 35 and random.random() < 0.3:
            self.ambient_bubbles.append(Bubble(random.uniform(0, SCREEN_WIDTH), SCREEN_HEIGHT + 10))

        # Update lists
        for b in self.ambient_bubbles:
            b.update(dt, current_force)
        self.ambient_bubbles = [b for b in self.ambient_bubbles if b.alive]

        for b in self.trail_bubbles:
            b.update(dt, current_force)
        self.trail_bubbles = [b for b in self.trail_bubbles if b.alive]

        for p in self.score_popups:
            p.update(dt)
        self.score_popups = [p for p in self.score_popups if p.alive]

        for s in self.sonar_pulses:
            s.update(dt)
        self.sonar_pulses = [s for s in self.sonar_pulses if s.alive]

        for c in self.current_streams:
            c.update(dt)
        self.current_streams = [c for c in self.current_streams if c.alive]

        for sp in self.sparkles:
            sp.update(dt)
        self.sparkles = [sp for sp in self.sparkles if sp.alive]

    def draw_ambient(self, surface: pygame.Surface) -> None:
        """Draws background ambient particles and light rays."""
        # 1. Volumetric God Rays
        ray_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        num_rays = 6
        for i in range(num_rays):
            offset = math.sin(self.light_ray_phase + i * 1.1) * 60.0
            x_top = (i + 1) * (SCREEN_WIDTH / (num_rays + 1)) + offset
            width_top = 45.0
            width_bottom = 120.0
            x_bottom = x_top + 150.0 + offset * 1.5
            
            ray_poly = [
                (x_top - width_top / 2, 0),
                (x_top + width_top / 2, 0),
                (x_bottom + width_bottom / 2, SCREEN_HEIGHT),
                (x_bottom - width_bottom / 2, SCREEN_HEIGHT),
            ]
            alpha = int(14 + 10 * math.sin(self.light_ray_phase * 1.5 + i))
            pygame.draw.polygon(ray_surf, (200, 245, 255, max(0, min(255, alpha))), ray_poly)

        surface.blit(ray_surf, (0, 0))

        # 2. Ambient Bubbles
        for b in self.ambient_bubbles:
            b.draw(surface)

    def draw_foreground(self, surface: pygame.Surface) -> None:
        """Draws dynamic foreground effects (streams, sonar rings, sparkles, score popups)."""
        for c in self.current_streams:
            c.draw(surface)

        for s in self.sonar_pulses:
            s.draw(surface)

        for b in self.trail_bubbles:
            b.draw(surface)

        for sp in self.sparkles:
            sp.draw(surface)

        for p in self.score_popups:
            p.draw(surface)
