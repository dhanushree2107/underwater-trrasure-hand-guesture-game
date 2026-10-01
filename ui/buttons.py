"""
Underwater Treasure Hunt - UI Button Component
Provides glassmorphism styling, hover glow animations, sound effects,
and dual interaction support (both Mouse click and Hand Pinch).
"""

import math
import time
from typing import Callable, Optional, Tuple
import pygame

from config import (
    COLOR_NEON_TEAL,
    COLOR_OCEAN_CYAN,
    COLOR_GOLD,
    COLOR_WHITE,
    COLOR_DARK_OVERLAY,
)
from audio.sound_manager import SoundManager

class Button:
    """A polished glassmorphic interactive UI button."""

    @staticmethod
    def clean_label(text: str) -> str:
        """Removes special unicode/emoji symbols that render as hollow tofu outline boxes in Pygame SysFont."""
        replacements = {
            "▶": ">",
            "◀": "<",
            "⟳": "",
            "⚡": "",
            "🗺️": "",
            "🏛️": "",
            "🗺": "",
            "🏛": "",
            "✓": "OK",
            "✌️": "",
            "🤏": "",
            "✋": "",
            "✊": "",
            "⭐": "*",
            "🔥": "",
            "🔒": "",
            "📦": "",
            "💎": "",
            "🎁": "",
            "❤️": "",
            "🖤": "",
        }
        cleaned = text
        for k, v in replacements.items():
            cleaned = cleaned.replace(k, v)
        return " ".join(cleaned.split())

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        font_size: int = 22,
        on_click: Optional[Callable[[], None]] = None,
        sound_manager: Optional[SoundManager] = None,
        accent_color: Tuple[int, int, int] = COLOR_NEON_TEAL
    ):
        if not pygame.font.get_init():
            pygame.font.init()
        self.rect = rect
        self.raw_text = text
        self.text = self.clean_label(text)
        self.font = pygame.font.SysFont("segoeui", font_size, bold=True)
        self.on_click = on_click
        self.sound_manager = sound_manager
        self.accent_color = accent_color

        self.is_hovered: bool = False
        self.prev_hovered: bool = False
        self.hover_progress: float = 0.0
        self.click_anim_time: float = 0.0
        self.hover_dwell_time: float = 0.0
        self.dwell_threshold: float = 0.50  # 0.50s of steady pointing automatically clicks!

    def update(self, cursor_x: int, cursor_y: int, is_clicked: bool, dt: float = 0.016) -> bool:
        """
        Updates button hover and click states.
        Triggers on:
        - Instant Click (Index Tap / Pinch / Left Mouse Click)
        - Hover Dwell (Holding cursor steadily over button for 0.5s)
        """
        self.is_hovered = self.rect.collidepoint(cursor_x, cursor_y)
        
        # Audio feedback on hover enter
        if self.is_hovered and not self.prev_hovered:
            if self.sound_manager:
                self.sound_manager.play('hover', volume_mult=0.4)
        self.prev_hovered = self.is_hovered

        # Smooth hover expansion interpolation
        target_hover = 1.0 if self.is_hovered else 0.0
        self.hover_progress += (target_hover - self.hover_progress) * min(1.0, 14.0 * dt)

        if self.click_anim_time > 0:
            self.click_anim_time -= dt

        # Dwell progress accumulation
        if self.is_hovered:
            self.hover_dwell_time += dt
        else:
            self.hover_dwell_time = max(0.0, self.hover_dwell_time - dt * 2.0)

        dwell_triggered = (self.hover_dwell_time >= self.dwell_threshold)

        # Trigger action if clicked (pinch/tap/mouse) OR dwell-hovered
        if self.is_hovered and (is_clicked or dwell_triggered):
            self.click_anim_time = 0.18
            self.hover_dwell_time = -0.5  # Brief pause before re-arming dwell
            if self.sound_manager:
                self.sound_manager.play('click', volume_mult=0.8)
            if self.on_click:
                self.on_click()
            return True

        return False

    def draw(self, surface: pygame.Surface) -> None:
        """Renders the glassmorphic button with animated glow border and dwell meter."""
        # Scale slightly on hover with even expansion on all sides
        expand = int(self.hover_progress * 4)
        draw_rect = self.rect.inflate(expand * 2, expand * 2)

        # 1. Semi-transparent Glass Background
        glass_surf = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
        bg_alpha = int(140 + self.hover_progress * 60)
        bg_color = (12, 28, 52, bg_alpha) if not self.click_anim_time > 0 else (25, 75, 110, 220)
        pygame.draw.rect(glass_surf, bg_color, (0, 0, draw_rect.width, draw_rect.height), border_radius=10)
        surface.blit(glass_surf, draw_rect.topleft)

        # 2. Glowing Border
        border_col = self.accent_color if self.is_hovered else (45, 95, 140)
        border_width = 3 if self.is_hovered else 2
        pygame.draw.rect(surface, border_col, draw_rect, width=border_width, border_radius=10)

        # 3. Dwell Progress Meter (Fills when pointing at button)
        if self.is_hovered and self.hover_dwell_time > 0:
            pct = min(1.0, max(0.0, self.hover_dwell_time / self.dwell_threshold))
            if pct > 0:
                bar_w = int((draw_rect.width - 24) * pct)
                bar_rect = pygame.Rect(draw_rect.left + 12, draw_rect.bottom - 6, bar_w, 3)
                pygame.draw.rect(surface, self.accent_color, bar_rect, border_radius=2)

        # 4. Text Label perfectly centered inside button outline box
        text_col = COLOR_WHITE if not self.is_hovered else (220, 255, 250)
        text_surf = self.font.render(self.text, True, text_col)
        tx = draw_rect.centerx - text_surf.get_width() // 2
        ty = draw_rect.centery - text_surf.get_height() // 2
        
        # Soft shadow
        shadow_surf = self.font.render(self.text, True, (5, 10, 20))
        surface.blit(shadow_surf, (tx + 1, ty + 1))
        surface.blit(text_surf, (tx, ty))
