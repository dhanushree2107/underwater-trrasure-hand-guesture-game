"""
Underwater Treasure Hunt - How To Play / Tutorial Screen
Displays illustrated instructions for hand gesture controls, gameplay mechanics,
fake treasure traps, and fallback keyboard controls.
"""

from typing import Callable, Optional
import pygame

from config import (
    COLOR_NEON_TEAL,
    COLOR_OCEAN_CYAN,
    COLOR_GOLD,
    COLOR_CORAL_RED,
    COLOR_AMBER_WARNING,
    COLOR_EMERALD,
    COLOR_WHITE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)
from ui.buttons import Button
from audio.sound_manager import SoundManager

class HowToPlayScreen:
    """Visual tutorial explaining all gesture controls and game rules."""

    def __init__(self, on_back: Callable[[], None], sound_manager: Optional[SoundManager] = None):
        self.on_back = on_back
        self.sound_manager = sound_manager
        
        self.font_title = pygame.font.SysFont("segoeui", 34, bold=True)
        self.font_subtitle = pygame.font.SysFont("segoeui", 18)
        self.font_card_title = pygame.font.SysFont("segoeui", 20, bold=True)
        self.font_card_text = pygame.font.SysFont("segoeui", 14)

        btn_w, btn_h = 240, 48
        self.back_button = Button(
            rect=pygame.Rect(SCREEN_WIDTH // 2 - btn_w // 2, SCREEN_HEIGHT - 75, btn_w, btn_h),
            text="◀ BACK TO MENU",
            on_click=self.on_back,
            sound_manager=self.sound_manager,
            accent_color=COLOR_NEON_TEAL
        )

    def update(self, cursor_x: int, cursor_y: int, is_clicked: bool, dt: float) -> None:
        self.back_button.update(cursor_x, cursor_y, is_clicked, dt)

    def draw(self, surface: pygame.Surface) -> None:
        """Renders tutorial cards with gesture mappings and rules."""
        # Dimming backdrop
        bg_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        bg_surf.fill((6, 16, 32, 235))
        surface.blit(bg_surf, (0, 0))

        # Title
        title_surf = self.font_title.render("HOW TO PLAY & GESTURE CONTROLS", True, COLOR_NEON_TEAL)
        sub_surf = self.font_subtitle.render("Master the depths using real-time computer vision or mouse fallback", True, (180, 220, 240))
        surface.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 25))
        surface.blit(sub_surf, (SCREEN_WIDTH // 2 - sub_surf.get_width() // 2, 68))

        # 5 Gesture Instruction Cards
        cards = [
            {
                "icon": "🖐",
                "title": "HAND SWIMMING",
                "action": "Pilot Swimmer",
                "desc": "Your hand controls the underwater swimmer! Move hand left, right, up, down to guide the diver through the abyss.",
                "col": COLOR_NEON_TEAL
            },
            {
                "icon": "👆",
                "title": "INDEX CLICK / PINCH",
                "action": "Grab & Deposit",
                "desc": "Tap your index finger down or pinch thumb & index to CLICK! Grabs relics, deposits into chest vault, and clicks menu buttons. Fallback: Left Click.",
                "col": COLOR_GOLD
            },
            {
                "icon": "✋",
                "title": "OPEN PALM",
                "action": "Water Current",
                "desc": "Extend all 5 fingers spread out to unleash a rushing water current. Disperses schools of fish and shifts relics. Fallback: Spacebar.",
                "col": COLOR_OCEAN_CYAN
            },
            {
                "icon": "✌️",
                "title": "TWO FINGERS",
                "action": "Sonar Pulse",
                "desc": "Raise index + middle finger to fire a sonar scan. Reveals genuine vs fake treasures & dangerous sea mines! Fallback: Right Click.",
                "col": COLOR_EMERALD
            },
            {
                "icon": "✊",
                "title": "FIST GESTURE",
                "action": "Energy Shield",
                "desc": "Curl all fingers into a tight fist to activate your bubble shield. Deflects apex predators like sharks! Fallback: Hold 'S'.",
                "col": (190, 120, 240)
            },
        ]

        card_w = 220
        card_h = 240
        start_x = 55
        spacing = 245
        card_y = 115

        for i, card in enumerate(cards):
            cx = start_x + (i * spacing)
            card_rect = pygame.Rect(cx, card_y, card_w, card_h)
            
            # Card Panel
            c_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            c_surf.fill((12, 26, 48, 200))
            pygame.draw.rect(c_surf, card["col"], (0, 0, card_w, card_h), width=2, border_radius=12)
            surface.blit(c_surf, (cx, card_y))

            # Icon
            font_icon = pygame.font.SysFont("segoeuiemoji", 38)
            icon_surf = font_icon.render(card["icon"], True, COLOR_WHITE)
            surface.blit(icon_surf, (cx + card_w // 2 - icon_surf.get_width() // 2, card_y + 12))

            # Titles
            t_surf = self.font_card_title.render(card["title"], True, card["col"])
            act_surf = self.font_card_text.render(f"Action: {card['action']}", True, (240, 245, 250))
            surface.blit(t_surf, (cx + card_w // 2 - t_surf.get_width() // 2, card_y + 60))
            surface.blit(act_surf, (cx + card_w // 2 - act_surf.get_width() // 2, card_y + 86))

            # Wrapped description
            words = card["desc"].split(" ")
            line = ""
            line_y = card_y + 115
            for w in words:
                test_line = f"{line} {w}".strip()
                if self.font_card_text.size(test_line)[0] < card_w - 20:
                    line = test_line
                else:
                    l_surf = self.font_card_text.render(line, True, (180, 205, 225))
                    surface.blit(l_surf, (cx + 12, line_y))
                    line_y += 18
                    line = w
            if line:
                l_surf = self.font_card_text.render(line, True, (180, 205, 225))
                surface.blit(l_surf, (cx + 12, line_y))

        # Bottom Rules Box (Oxygen & Fake Treasure Warning)
        rule_w = SCREEN_WIDTH - 110
        rule_h = 135
        rule_x = 55
        rule_y = 380
        rule_surf = pygame.Surface((rule_w, rule_h), pygame.SRCALPHA)
        rule_surf.fill((16, 24, 40, 210))
        pygame.draw.rect(rule_surf, COLOR_AMBER_WARNING, (0, 0, rule_w, rule_h), width=2, border_radius=10)
        surface.blit(rule_surf, (rule_x, rule_y))

        r_title = self.font_card_title.render("CRITICAL MISSION RULES: OXYGEN & DECEPTIVE FAKES", True, COLOR_AMBER_WARNING)
        surface.blit(r_title, (rule_x + 20, rule_y + 14))

        rules = [
            "• DECEPTIVE FAKES: Some treasures are counterfeit! Grabbing one incurs a -50 score penalty & -12% oxygen loss.",
            "• SONAR SCAN: Always fire your 2-finger Sonar (✌️) to distinguish real treasures (Green) from fakes (Yellow) and traps (Red)!",
            "• EXPLOSIVE TRAPS: Spiked naval mines inflict a devastating -25% oxygen blast! Avoid touching them at all costs.",
            "• OXYGEN DEPLETION: Your oxygen depletes constantly over time. Reach the target score before your tank runs dry!"
        ]
        for idx, r_text in enumerate(rules):
            rt_surf = self.font_card_text.render(r_text, True, (215, 230, 245))
            surface.blit(rt_surf, (rule_x + 20, rule_y + 42 + idx * 21))

        # Draw Back button
        self.back_button.draw(surface)
