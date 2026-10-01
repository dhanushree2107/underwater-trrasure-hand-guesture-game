"""
Underwater Treasure Hunt - Smart Progressive Tutorial System
Guides new divers step-by-step through two-hand swimming, directional steering,
pinch grabbing, depot depositing, and sonar activation in Level 1.
"""

from dataclasses import dataclass
from typing import List, Optional
import pygame

from config import (
    COLOR_OCEAN_CYAN,
    COLOR_NEON_TEAL,
    COLOR_GOLD,
    COLOR_WHITE,
    COLOR_EMERALD,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)


@dataclass
class TutorialStep:
    step_id: str
    headline: str
    subtext: str
    icon: str
    required_action: str  # "SWIM_ANY", "SWIM_LEFT", "SWIM_RIGHT", "SWIM_UP", "SYNC_SWIM", "PINCH_GRAB", "DEPOSIT", "DONE"


class SmartTutorial:
    """Delivers contextual on-screen tutorial cues without interrupting gameplay flow."""

    def __init__(self):
        self.steps: List[TutorialStep] = [
            TutorialStep(
                step_id="swim_intro",
                headline="MOVE BOTH HANDS TO SWIM",
                subtext="Wave both hands in the webcam to swim through the water.",
                icon="👐",
                required_action="SWIM_ANY"
            ),
            TutorialStep(
                step_id="swim_left_right",
                headline="SWIM LEFT & RIGHT",
                subtext="Move both hands together towards the left or right edge of your screen.",
                icon="↔️",
                required_action="SWIM_DIRECTION"
            ),
            TutorialStep(
                step_id="swim_sync",
                headline="SYNCHRONIZED SWIMMING",
                subtext="Move both hands in rhythm to trigger COMBO SWIM and burst forward!",
                icon="🏊",
                required_action="SYNC_SWIM"
            ),
            TutorialStep(
                step_id="pinch_grab",
                headline="PINCH TO GRAB TREASURE",
                subtext="Hover your glowing Gold Right Cursor over a relic and pinch thumb & index.",
                icon="🤏",
                required_action="PINCH_GRAB"
            ),
            TutorialStep(
                step_id="deposit_depot",
                headline="CARRY TO TREASURE DEPOT",
                subtext="Swim your diver with the relic over the seafloor Treasure Chest to deposit!",
                icon="📦",
                required_action="DEPOSIT"
            ),
            TutorialStep(
                step_id="sonar_tip",
                headline="TWO FINGERS FOR SONAR",
                subtext="Raise Two Fingers (peace sign) on your right hand to reveal hidden relics!",
                icon="✌️",
                required_action="SONAR"
            ),
        ]
        self.current_step_idx: int = 0
        self.active: bool = False
        self.completed: bool = False
        self.display_timer: float = 0.0
        self.fade_alpha: float = 0.0

    def start_tutorial(self) -> None:
        self.current_step_idx = 0
        self.active = True
        self.completed = False
        self.display_timer = 0.0
        self.fade_alpha = 0.0

    def trigger_action(self, action_name: str) -> None:
        """Advances tutorial when user performs expected action."""
        if not self.active or self.completed:
            return

        current = self.steps[self.current_step_idx]
        matched = False
        if current.required_action == "SWIM_ANY" and action_name in ("SWIM_LEFT", "SWIM_RIGHT", "SWIM_UP", "SWIM_DOWN", "SWIM_ANY"):
            matched = True
        elif current.required_action == "SWIM_DIRECTION" and action_name in ("SWIM_LEFT", "SWIM_RIGHT"):
            matched = True
        elif current.required_action == "SYNC_SWIM" and action_name == "SYNC_SWIM":
            matched = True
        elif current.required_action == "PINCH_GRAB" and action_name == "PINCH_GRAB":
            matched = True
        elif current.required_action == "DEPOSIT" and action_name == "DEPOSIT":
            matched = True
        elif current.required_action == "SONAR" and action_name == "SONAR":
            matched = True

        if matched:
            self.current_step_idx += 1
            if self.current_step_idx >= len(self.steps):
                self.completed = True
                self.active = False

    def update(
        self,
        dt: float,
        is_hand_detected: bool = False,
        is_moving: bool = False,
        motion_result = None,
        is_pinching: bool = False,
        is_carrying: bool = False,
        deposited_count: int = 0,
        sonar_used: bool = False,
        **kwargs
    ) -> None:
        if not self.active or self.completed:
            return
        self.display_timer += dt
        target_alpha = 240.0
        self.fade_alpha += (target_alpha - self.fade_alpha) * min(1.0, 8.0 * dt)

        # Auto-trigger tutorial progression on matching actions
        if self.current_step_idx == 0 and is_moving:
            self.trigger_action("SWIM_ANY")
        elif self.current_step_idx == 1 and motion_result and motion_result.direction_label in ("SWIM LEFT", "SWIM RIGHT"):
            self.trigger_action("SWIM_LEFT")
        elif self.current_step_idx == 2 and motion_result and (motion_result.is_combo_swim or motion_result.sync_level > 0.75):
            self.trigger_action("SYNC_SWIM")
        elif self.current_step_idx == 3 and (is_carrying or is_pinching):
            self.trigger_action("PINCH_GRAB")
        elif self.current_step_idx == 4 and deposited_count > 0:
            self.trigger_action("DEPOSIT")
        elif self.current_step_idx == 5 and sonar_used:
            self.trigger_action("SONAR")

    def draw(self, surface: pygame.Surface) -> None:
        if not self.active or self.completed:
            return

        step = self.steps[self.current_step_idx]
        w, h = 620, 72
        x = SCREEN_WIDTH // 2 - w // 2
        y = 70

        # Semi-transparent glassmorphic card
        card_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        card_surf.fill((6, 22, 48, int(self.fade_alpha * 0.88)))
        pygame.draw.rect(card_surf, (*COLOR_NEON_TEAL[:3], int(self.fade_alpha)), (0, 0, w, h), width=2, border_radius=10)
        surface.blit(card_surf, (x, y))

        # Icon
        font_icon = pygame.font.SysFont("segoeuiemoji", 26)
        icon_surf = font_icon.render(step.icon, True, COLOR_GOLD)
        surface.blit(icon_surf, (x + 18, y + 14))

        # Headline
        font_h = pygame.font.SysFont("segoeui", 16, bold=True)
        head_surf = font_h.render(f"TUTORIAL: {step.headline}", True, COLOR_GOLD)
        surface.blit(head_surf, (x + 65, y + 10))

        # Subtext
        font_sub = pygame.font.SysFont("segoeui", 13)
        sub_surf = font_sub.render(step.subtext, True, (215, 235, 255))
        surface.blit(sub_surf, (x + 65, y + 36))
