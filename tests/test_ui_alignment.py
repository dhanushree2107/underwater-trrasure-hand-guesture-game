"""
Tests for UI Button alignment, wording outline box sanitization, and modal panel containment.
"""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import pytest
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from ui.buttons import Button
from ui.menu import MainMenu
from ui.screens import LevelCompleteScreen, GameOverScreen, VictoryScreen

pygame.init()

@pytest.fixture(autouse=True)
def setup_pygame():
    if not pygame.get_init():
        pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()
    yield

def test_button_label_cleaning_eliminates_tofu_boxes():
    """Verifies that unicode characters causing hollow outline boxes (tofu) are sanitized."""
    test_cases = [
        ("START EXPEDITION ▶", "START EXPEDITION >"),
        ("EXPEDITION ZONES 🗺️", "EXPEDITION ZONES"),
        ("UNDERWATER MUSEUM 🏛️", "UNDERWATER MUSEUM"),
        ("ABYSSAL CHALLENGES ⚡", "ABYSSAL CHALLENGES"),
        ("REPLAY ⟳", "REPLAY"),
        ("◀ MAIN MENU", "< MAIN MENU"),
    ]
    for raw, expected in test_cases:
        cleaned = Button.clean_label(raw)
        assert cleaned == expected, f"Failed on raw: {raw}, got: {cleaned}, expected: {expected}"

    btn = Button(pygame.Rect(100, 100, 200, 40), "EXPEDITION ZONES 🗺️")
    assert btn.text == "EXPEDITION ZONES"
    assert "🗺" not in btn.text

def test_main_menu_button_alignment_and_sizing():
    """Verifies that all menu buttons are horizontally centered and properly spaced."""
    menu = MainMenu(
        on_play=lambda: None,
        on_level_select=lambda: None,
        on_instructions=lambda: None,
        on_camera_check=lambda: None,
        on_quit=lambda: None,
        on_museum=lambda: None,
        on_challenges=lambda: None,
    )

    for btn in menu.buttons:
        # Check horizontal centering
        assert btn.rect.centerx == SCREEN_WIDTH // 2
        # Check comfortable width for text
        assert btn.rect.width >= 300
        assert btn.rect.height >= 40

    # Check vertical ordering
    for i in range(len(menu.buttons) - 1):
        assert menu.buttons[i].rect.bottom < menu.buttons[i+1].rect.top

def test_level_complete_screen_buttons_inside_panel_box():
    """Verifies that action buttons are strictly contained within the modal panel outline box."""
    screen = LevelCompleteScreen(
        on_next_level=lambda: None,
        on_menu=lambda: None,
        on_replay=lambda: None,
        on_museum=lambda: None
    )

    # Panel geometry in LevelCompleteScreen: panel_w = 800, panel_h = 570, py = 40
    panel_w = 800
    panel_h = 570
    px = SCREEN_WIDTH // 2 - panel_w // 2
    py = 40
    panel_rect = pygame.Rect(px, py, panel_w, panel_h)

    for btn in screen.buttons:
        assert panel_rect.contains(btn.rect), f"Button {btn.text} ({btn.rect}) overflows panel ({panel_rect})"
        assert btn.rect.bottom <= panel_rect.bottom - 15, f"Button {btn.text} too close to bottom border"
        assert btn.rect.top >= panel_rect.top + 50, f"Button {btn.text} too close to top border"

def test_game_over_and_victory_buttons_inside_panel():
    """Verifies that buttons in GameOver and Victory modals do not clip or breach panel outlines."""
    go_screen = GameOverScreen(on_retry=lambda: None, on_menu=lambda: None)
    panel_w, panel_h = 640, 420
    px = SCREEN_WIDTH // 2 - panel_w // 2
    py = 100
    go_panel = pygame.Rect(px, py, panel_w, panel_h)

    assert go_panel.contains(go_screen.menu_btn.rect)
    assert go_panel.contains(go_screen.retry_btn.rect)

    v_screen = VictoryScreen(on_play_again=lambda: None, on_menu=lambda: None)
    v_panel_w, v_panel_h = 720, 490
    v_px = SCREEN_WIDTH // 2 - v_panel_w // 2
    v_py = 60
    v_panel = pygame.Rect(v_px, v_py, v_panel_w, v_panel_h)

    assert v_panel.contains(v_screen.menu_btn.rect)
    assert v_panel.contains(v_screen.again_btn.rect)
