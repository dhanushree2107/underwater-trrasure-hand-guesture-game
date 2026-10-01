"""
Underwater Treasure Hunt - Main Menu System
Presents an animated underwater title scene with volumetric god rays,
schools of fish, rising bubbles, and interactive glassmorphic buttons.
"""

import math
import time
from typing import Callable, Optional
import pygame

from config import (
    TITLE,
    SUBTITLE,
    COLOR_NEON_TEAL,
    COLOR_OCEAN_CYAN,
    COLOR_GOLD,
    COLOR_EMERALD,
    COLOR_AMBER_WARNING,
    COLOR_WHITE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)
from ui.buttons import Button
from audio.sound_manager import SoundManager
from game.particles import ParticleSystem
from game.enemy import MarineLifeManager

class MainMenu:
    """Animated underwater title menu screen."""

    def __init__(
        self,
        on_play: Callable[[], None],
        on_level_select: Callable[[], None],
        on_challenges: Callable[[], None],
        on_instructions: Callable[[], None],
        on_camera_check: Callable[[], None],
        on_quit: Callable[[], None],
        sound_manager: Optional[SoundManager] = None
    ):
        self.on_play = on_play
        self.on_level_select = on_level_select
        self.on_challenges = on_challenges
        self.on_instructions = on_instructions
        self.on_camera_check = on_camera_check
        self.on_quit = on_quit
        self.sound_manager = sound_manager

        self.font_title = pygame.font.SysFont("segoeui", 50, bold=True)
        self.font_subtitle = pygame.font.SysFont("segoeui", 19, bold=True)

        # Ambient background scenery for menu
        self.particles = ParticleSystem()
        self.marine_manager = MarineLifeManager(fish_count=10)

        # Interactive Menu Buttons
        btn_w, btn_h = 280, 46
        cx = SCREEN_WIDTH // 2 - btn_w // 2
        start_y = 250
        spacing = 52

        self.play_btn = Button(
            pygame.Rect(cx, start_y, btn_w, btn_h),
            "START EXPEDITION ▶",
            font_size=19,
            on_click=self.on_play,
            sound_manager=self.sound_manager,
            accent_color=COLOR_GOLD
        )
        self.level_select_btn = Button(
            pygame.Rect(cx, start_y + spacing, btn_w, btn_h),
            "EXPEDITION ZONES 🗺️",
            font_size=18,
            on_click=self.on_level_select,
            sound_manager=self.sound_manager,
            accent_color=COLOR_EMERALD
        )
        self.challenges_btn = Button(
            pygame.Rect(cx, start_y + spacing * 2, btn_w, btn_h),
            "ABYSSAL CHALLENGES ⚡",
            font_size=18,
            on_click=self.on_challenges,
            sound_manager=self.sound_manager,
            accent_color=COLOR_AMBER_WARNING
        )
        self.instructions_btn = Button(
            pygame.Rect(cx, start_y + spacing * 3, btn_w, btn_h),
            "HOW TO PLAY / GESTURES",
            font_size=18,
            on_click=self.on_instructions,
            sound_manager=self.sound_manager,
            accent_color=COLOR_NEON_TEAL
        )
        self.camera_btn = Button(
            pygame.Rect(cx, start_y + spacing * 4, btn_w, btn_h),
            "CAMERA & VISION CHECK",
            font_size=18,
            on_click=self.on_camera_check,
            sound_manager=self.sound_manager,
            accent_color=COLOR_OCEAN_CYAN
        )
        self.quit_btn = Button(
            pygame.Rect(cx, start_y + spacing * 5, btn_w, btn_h),
            "QUIT EXPEDITION",
            font_size=18,
            on_click=self.on_quit,
            sound_manager=self.sound_manager,
            accent_color=(220, 75, 75)
        )

        self.buttons = [
            self.play_btn,
            self.level_select_btn,
            self.challenges_btn,
            self.instructions_btn,
            self.camera_btn,
            self.quit_btn
        ]
        self.title_glow_phase = 0.0

    def update(self, cursor_x: int, cursor_y: int, is_clicked: bool, dt: float) -> None:
        self.title_glow_phase += 2.0 * dt
        self.particles.update(dt)
        self.marine_manager.update(dt, current_active=False, cursor_pos=(cursor_x, cursor_y))

        for btn in self.buttons:
            btn.update(cursor_x, cursor_y, is_clicked, dt)

    def draw(self, surface: pygame.Surface) -> None:
        """Renders the underwater title sequence."""
        # 1. Vertical Ocean Gradient
        for y in range(0, SCREEN_HEIGHT, 4):
            t = y / SCREEN_HEIGHT
            r = int(10 + (2 - 10) * t)
            g = int(48 + (12 - 48) * t)
            b = int(88 + (28 - 88) * t)
            pygame.draw.rect(surface, (r, g, b), (0, y, SCREEN_WIDTH, 4))

        # 2. Ambient Light Rays & Bubbles
        self.particles.draw_ambient(surface)
        self.marine_manager.draw(surface)
        self.particles.draw_foreground(surface)

        # 3. Dynamic Title Banner with Glow
        pulse = math.sin(self.title_glow_phase)
        title_y = 110 + int(pulse * 4)

        # Title Glow Aura
        glow_surf = self.font_title.render(TITLE.upper(), True, COLOR_NEON_TEAL)
        glow_alpha = int(90 + 40 * pulse)
        alpha_surf = pygame.Surface(glow_surf.get_size(), pygame.SRCALPHA)
        alpha_surf.blit(glow_surf, (0, 0))
        alpha_surf.set_alpha(max(0, min(255, glow_alpha)))
        surface.blit(alpha_surf, (SCREEN_WIDTH // 2 - glow_surf.get_width() // 2, title_y - 2))

        # Primary Crisp Title
        title_surf = self.font_title.render(TITLE.upper(), True, COLOR_WHITE)
        surface.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, title_y))

        # Subtitle
        sub_surf = self.font_subtitle.render(SUBTITLE, True, COLOR_OCEAN_CYAN)
        surface.blit(sub_surf, (SCREEN_WIDTH // 2 - sub_surf.get_width() // 2, title_y + 70))

        # 4. Buttons
        for btn in self.buttons:
            btn.draw(surface)

        # Bottom Version / Company Footer
        foot_font = pygame.font.SysFont("segoeui", 13)
        foot = foot_font.render("v1.0.0 Company Release  |  Hand Gesture Vision Pipeline Powered by MediaPipe & Pygame", True, (120, 160, 190))
        surface.blit(foot, (SCREEN_WIDTH // 2 - foot.get_width() // 2, SCREEN_HEIGHT - 30))
