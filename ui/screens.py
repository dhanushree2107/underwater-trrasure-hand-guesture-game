"""
Underwater Treasure Hunt - Core UI Screen Overlays
Implements:
1. CameraCheckScreen (Live camera verification, landmark feedback, and gesture test bed)
2. PauseScreen (In-game pause overlay)
3. LevelCompleteScreen (Victory fanfare, oxygen bonus tally, and star rating)
4. GameOverScreen (Oxygen depletion screen with retry)
5. VictoryScreen (All 5 levels conquered summary)
"""

import math
import time
from typing import Callable, Optional, Tuple
import cv2
import pygame

from config import (
    COLOR_NEON_TEAL,
    COLOR_OCEAN_CYAN,
    COLOR_GOLD,
    COLOR_CORAL_RED,
    COLOR_EMERALD,
    COLOR_AMBER_WARNING,
    COLOR_WHITE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)
from ui.buttons import Button
from audio.sound_manager import SoundManager
from hand_tracking.gesture_detector import GestureType

class CameraCheckScreen:
    """Pre-dive diagnostic screen allowing players to verify webcam and test gestures."""

    def __init__(
        self,
        on_start_game: Callable[[], None],
        on_back: Callable[[], None],
        sound_manager: Optional[SoundManager] = None
    ):
        self.on_start_game = on_start_game
        self.on_back = on_back
        self.sound_manager = sound_manager

        self.font_title = pygame.font.SysFont("segoeui", 32, bold=True)
        self.font_sub = pygame.font.SysFont("segoeui", 17)
        self.font_label = pygame.font.SysFont("segoeui", 19, bold=True)
        self.font_body = pygame.font.SysFont("segoeui", 15)

        btn_w, btn_h = 220, 48
        self.start_btn = Button(
            rect=pygame.Rect(SCREEN_WIDTH // 2 + 30, SCREEN_HEIGHT - 75, btn_w, btn_h),
            text="START DIVE ▶",
            on_click=self.on_start_game,
            sound_manager=self.sound_manager,
            accent_color=COLOR_EMERALD
        )
        self.back_btn = Button(
            rect=pygame.Rect(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT - 75, btn_w, btn_h),
            text="◀ MAIN MENU",
            on_click=self.on_back,
            sound_manager=self.sound_manager,
            accent_color=COLOR_NEON_TEAL
        )

    def update(self, cursor_x: int, cursor_y: int, is_clicked: bool, dt: float) -> None:
        self.start_btn.update(cursor_x, cursor_y, is_clicked, dt)
        self.back_btn.update(cursor_x, cursor_y, is_clicked, dt)

    def draw(
        self,
        surface: pygame.Surface,
        raw_frame,
        camera_available: bool,
        hand_detected: bool,
        current_gesture: GestureType,
        pinch_dist: float,
        camera_fps: float
    ) -> None:
        """Renders live camera preview box, status badges, and test results."""
        bg_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        bg_surf.fill((6, 16, 32, 240))
        surface.blit(bg_surf, (0, 0))

        # Title
        t_surf = self.font_title.render("VISION SYSTEM & CAMERA DIAGNOSTICS", True, COLOR_NEON_TEAL)
        sub_text = "Verify that your webcam tracks your hand gestures before beginning your expedition"
        s_surf = self.font_sub.render(sub_text, True, (180, 215, 235))
        surface.blit(t_surf, (SCREEN_WIDTH // 2 - t_surf.get_width() // 2, 22))
        surface.blit(s_surf, (SCREEN_WIDTH // 2 - s_surf.get_width() // 2, 62))

        # 1. Left Frame: Live Webcam Preview Feed
        feed_w, feed_h = 480, 360
        feed_x = 80
        feed_y = 115
        
        feed_rect = pygame.Rect(feed_x, feed_y, feed_w, feed_h)
        pygame.draw.rect(surface, (15, 30, 50), feed_rect, border_radius=10)
        pygame.draw.rect(surface, COLOR_NEON_TEAL, feed_rect, width=2, border_radius=10)

        if raw_frame is not None:
            try:
                # Resize and convert BGR OpenCV frame to Pygame Surface
                resized = cv2.resize(raw_frame, (feed_w, feed_h))
                rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
                # Pygame expects (width, height)
                frame_surface = pygame.surfarray.make_surface(rgb.swapaxes(0, 1))
                surface.blit(frame_surface, (feed_x, feed_y))
            except Exception:
                pass
        else:
            no_cam_text = self.font_label.render("CAMERA FEED OFFLINE", True, COLOR_CORAL_RED)
            surface.blit(no_cam_text, (feed_x + feed_w // 2 - no_cam_text.get_width() // 2, feed_y + feed_h // 2 - 10))

        # 2. Right Frame: Status Diagnostics & Live Gesture Tester
        diag_x = feed_x + feed_w + 50
        diag_y = feed_y
        diag_w = SCREEN_WIDTH - diag_x - 80
        diag_h = feed_h

        d_surf = pygame.Surface((diag_w, diag_h), pygame.SRCALPHA)
        d_surf.fill((12, 26, 46, 210))
        pygame.draw.rect(d_surf, (35, 75, 115), (0, 0, diag_w, diag_h), width=2, border_radius=10)
        surface.blit(d_surf, (diag_x, diag_y))

        # Status Rows
        # Camera Status
        cam_col = COLOR_EMERALD if camera_available else COLOR_AMBER_WARNING
        cam_status_str = f"ONLINE ({camera_fps:.1f} FPS)" if camera_available else "NOT FOUND (MOUSE FALLBACK READY)"
        c_label = self.font_label.render("CAMERA STATUS:", True, COLOR_WHITE)
        c_val = self.font_label.render(cam_status_str, True, cam_col)
        surface.blit(c_label, (diag_x + 25, diag_y + 25))
        surface.blit(c_val, (diag_x + 25, diag_y + 50))

        # Hand Detection Status
        hand_col = COLOR_EMERALD if hand_detected else (COLOR_AMBER_WARNING if camera_available else (140, 160, 180))
        hand_status_str = "HAND TRACKED & LOCKED" if hand_detected else "SEARCHING FOR HAND..."
        h_label = self.font_label.render("VISION SENSOR:", True, COLOR_WHITE)
        h_val = self.font_label.render(hand_status_str, True, hand_col)
        surface.blit(h_label, (diag_x + 25, diag_y + 90))
        surface.blit(h_val, (diag_x + 25, diag_y + 115))

        # Live Gesture Recognition Display Box
        g_box_y = diag_y + 160
        g_box_w = diag_w - 50
        g_box_h = 95
        pygame.draw.rect(surface, (18, 38, 65), (diag_x + 25, g_box_y, g_box_w, g_box_h), border_radius=8)
        pygame.draw.rect(surface, COLOR_NEON_TEAL, (diag_x + 25, g_box_y, g_box_w, g_box_h), width=2, border_radius=8)

        g_title = self.font_body.render("CURRENT ACTIVE GESTURE DETECTED:", True, (160, 205, 230))
        surface.blit(g_title, (diag_x + 38, g_box_y + 14))

        # Gesture name and icon
        g_text = f"{current_gesture.value}"
        g_val = self.font_title.render(g_text, True, COLOR_GOLD if current_gesture == GestureType.PINCH else COLOR_WHITE)
        surface.blit(g_val, (diag_x + 38, g_box_y + 40))

        # Fallback advisory note
        note_y = diag_y + 275
        notes = [
            "✔ Mouse/Keyboard fallback is always enabled.",
            "• Left Click = Pinch to collect",
            "• Right Click = Two-Finger Sonar",
            "• Spacebar = Open Palm Water Current",
            "• Hold 'S' = Fist Shield",
        ]
        for idx, n in enumerate(notes):
            n_surf = self.font_body.render(n, True, (190, 215, 235))
            surface.blit(n_surf, (diag_x + 25, note_y + idx * 20))

        # Buttons
        self.back_btn.draw(surface)
        self.start_btn.draw(surface)


class PauseScreen:
    """Semi-transparent pause modal with mission resume and restart options."""

    def __init__(
        self,
        on_resume: Callable[[], None],
        on_restart: Callable[[], None],
        on_menu: Callable[[], None],
        sound_manager: Optional[SoundManager] = None
    ):
        self.font_title = pygame.font.SysFont("segoeui", 38, bold=True)
        self.on_resume = on_resume
        self.on_restart = on_restart
        self.on_menu = on_menu
        self.sound_manager = sound_manager

        btn_w, btn_h = 240, 48
        cx = SCREEN_WIDTH // 2 - btn_w // 2
        self.resume_btn = Button(pygame.Rect(cx, 240, btn_w, btn_h), "RESUME MISSION", on_click=self.on_resume, sound_manager=self.sound_manager, accent_color=COLOR_EMERALD)
        self.restart_btn = Button(pygame.Rect(cx, 310, btn_w, btn_h), "RESTART LEVEL", on_click=self.on_restart, sound_manager=self.sound_manager, accent_color=COLOR_AMBER_WARNING)
        self.menu_btn = Button(pygame.Rect(cx, 380, btn_w, btn_h), "QUIT TO MENU", on_click=self.on_menu, sound_manager=self.sound_manager, accent_color=COLOR_CORAL_RED)

    def update(self, cursor_x: int, cursor_y: int, is_clicked: bool, dt: float) -> None:
        self.resume_btn.update(cursor_x, cursor_y, is_clicked, dt)
        self.restart_btn.update(cursor_x, cursor_y, is_clicked, dt)
        self.menu_btn.update(cursor_x, cursor_y, is_clicked, dt)

    def draw(self, surface: pygame.Surface) -> None:
        modal_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        modal_surf.fill((5, 12, 25, 215))
        surface.blit(modal_surf, (0, 0))

        title = self.font_title.render("MISSION PAUSED", True, COLOR_NEON_TEAL)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 140))

        self.resume_btn.draw(surface)
        self.restart_btn.draw(surface)
        self.menu_btn.draw(surface)


class LevelCompleteScreen:
    """Triumphant victory banner displayed upon retrieving all genuine relics."""

    def __init__(
        self,
        on_next_level: Callable[[], None],
        on_menu: Callable[[], None],
        sound_manager: Optional[SoundManager] = None
    ):
        self.font_title = pygame.font.SysFont("segoeui", 38, bold=True)
        self.font_label = pygame.font.SysFont("segoeui", 22, bold=True)
        self.font_data = pygame.font.SysFont("segoeui", 20)
        self.on_next_level = on_next_level
        self.on_menu = on_menu
        self.sound_manager = sound_manager

        btn_w, btn_h = 230, 48
        self.next_btn = Button(pygame.Rect(SCREEN_WIDTH // 2 + 20, 460, btn_w, btn_h), "NEXT LEVEL ▶", on_click=self.on_next_level, sound_manager=self.sound_manager, accent_color=COLOR_EMERALD)
        self.menu_btn = Button(pygame.Rect(SCREEN_WIDTH // 2 - 250, 460, btn_w, btn_h), "MAIN MENU", on_click=self.on_menu, sound_manager=self.sound_manager, accent_color=COLOR_NEON_TEAL)

    def update(self, cursor_x: int, cursor_y: int, is_clicked: bool, dt: float) -> None:
        self.next_btn.update(cursor_x, cursor_y, is_clicked, dt)
        self.menu_btn.update(cursor_x, cursor_y, is_clicked, dt)

    def draw(self, surface: pygame.Surface, level_name: str, level_score: int, total_score: int, remaining_oxygen: float) -> None:
        modal_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        modal_surf.fill((6, 18, 38, 230))
        surface.blit(modal_surf, (0, 0))

        # Panel Box
        panel_w = 620
        panel_h = 440
        px = SCREEN_WIDTH // 2 - panel_w // 2
        py = 90
        pygame.draw.rect(surface, (12, 28, 52), (px, py, panel_w, panel_h), border_radius=16)
        pygame.draw.rect(surface, COLOR_NEON_TEAL, (px, py, panel_w, panel_h), width=2, border_radius=16)

        # Title
        t_surf = self.font_title.render("LEVEL COMPLETE!", True, COLOR_GOLD)
        surface.blit(t_surf, (SCREEN_WIDTH // 2 - t_surf.get_width() // 2, py + 25))

        sub_surf = self.font_data.render(f"Cleared: {level_name}", True, COLOR_OCEAN_CYAN)
        surface.blit(sub_surf, (SCREEN_WIDTH // 2 - sub_surf.get_width() // 2, py + 75))

        # Stats Tally
        ox_bonus = int(remaining_oxygen * 5)
        stats = [
            ("Relic Points Gathered:", f"+{level_score}"),
            ("Remaining Oxygen Reserve:", f"{remaining_oxygen:.1f}%"),
            ("Oxygen Efficiency Bonus:", f"+{ox_bonus}"),
            ("Total Cumulative Score:", f"{total_score + ox_bonus:,}"),
        ]

        for idx, (label, val) in enumerate(stats):
            l_s = self.font_label.render(label, True, COLOR_WHITE)
            v_s = self.font_label.render(val, True, COLOR_GOLD if "Score" in label or "Bonus" in label else COLOR_EMERALD)
            surface.blit(l_s, (px + 60, py + 130 + idx * 42))
            surface.blit(v_s, (px + panel_w - 60 - v_s.get_width(), py + 130 + idx * 42))

        # Star Rating based on oxygen
        stars = 3 if remaining_oxygen > 50 else (2 if remaining_oxygen > 20 else 1)
        star_str = "⭐ " * stars
        star_surf = pygame.font.SysFont("segoeuiemoji", 32).render(star_str, True, COLOR_GOLD)
        surface.blit(star_surf, (SCREEN_WIDTH // 2 - star_surf.get_width() // 2, py + 310))

        self.menu_btn.draw(surface)
        self.next_btn.draw(surface)


class GameOverScreen:
    """Screen displayed when oxygen depletes or mission timer expires."""

    def __init__(
        self,
        on_retry: Callable[[], None],
        on_menu: Callable[[], None],
        sound_manager: Optional[SoundManager] = None
    ):
        self.font_title = pygame.font.SysFont("segoeui", 38, bold=True)
        self.font_label = pygame.font.SysFont("segoeui", 22, bold=True)
        self.font_data = pygame.font.SysFont("segoeui", 18)
        self.on_retry = on_retry
        self.on_menu = on_menu
        self.sound_manager = sound_manager

        btn_w, btn_h = 230, 48
        self.retry_btn = Button(pygame.Rect(SCREEN_WIDTH // 2 + 20, 420, btn_w, btn_h), "RETRY DIVE ⟳", on_click=self.on_retry, sound_manager=self.sound_manager, accent_color=COLOR_AMBER_WARNING)
        self.menu_btn = Button(pygame.Rect(SCREEN_WIDTH // 2 - 250, 420, btn_w, btn_h), "MAIN MENU", on_click=self.on_menu, sound_manager=self.sound_manager, accent_color=COLOR_NEON_TEAL)

    def update(self, cursor_x: int, cursor_y: int, is_clicked: bool, dt: float) -> None:
        self.retry_btn.update(cursor_x, cursor_y, is_clicked, dt)
        self.menu_btn.update(cursor_x, cursor_y, is_clicked, dt)

    def draw(self, surface: pygame.Surface, reason: str, score: int, level_name: str) -> None:
        modal_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        modal_surf.fill((25, 6, 8, 235))
        surface.blit(modal_surf, (0, 0))

        # Panel Box
        panel_w = 600
        panel_h = 390
        px = SCREEN_WIDTH // 2 - panel_w // 2
        py = 110
        pygame.draw.rect(surface, (36, 12, 16), (px, py, panel_w, panel_h), border_radius=16)
        pygame.draw.rect(surface, COLOR_CORAL_RED, (px, py, panel_w, panel_h), width=2, border_radius=16)

        t_surf = self.font_title.render("MISSION FAILED", True, COLOR_CORAL_RED)
        surface.blit(t_surf, (SCREEN_WIDTH // 2 - t_surf.get_width() // 2, py + 25))

        sub_surf = self.font_label.render(reason.upper(), True, COLOR_AMBER_WARNING)
        surface.blit(sub_surf, (SCREEN_WIDTH // 2 - sub_surf.get_width() // 2, py + 78))

        info_lvl = self.font_data.render(f"Expedition Zone: {level_name}", True, (220, 220, 220))
        surface.blit(info_lvl, (SCREEN_WIDTH // 2 - info_lvl.get_width() // 2, py + 140))

        info_score = self.font_title.render(f"FINAL SCORE: {score:,}", True, COLOR_GOLD)
        surface.blit(info_score, (SCREEN_WIDTH // 2 - info_score.get_width() // 2, py + 180))

        hint_text = self.font_data.render("Tip: Use Sonar (✌️) to avoid explosive sea mines and deceptive fakes!", True, (190, 205, 225))
        surface.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, py + 245))

        self.menu_btn.draw(surface)
        self.retry_btn.draw(surface)


class VictoryScreen:
    """Grand finale celebration screen displayed upon finishing all 5 levels."""

    def __init__(
        self,
        on_play_again: Callable[[], None],
        on_menu: Callable[[], None],
        sound_manager: Optional[SoundManager] = None
    ):
        self.font_title = pygame.font.SysFont("segoeui", 38, bold=True)
        self.font_sub = pygame.font.SysFont("segoeui", 22, bold=True)
        self.font_label = pygame.font.SysFont("segoeui", 18)
        self.on_play_again = on_play_again
        self.on_menu = on_menu
        self.sound_manager = sound_manager

        btn_w, btn_h = 240, 50
        self.again_btn = Button(pygame.Rect(SCREEN_WIDTH // 2 + 20, 480, btn_w, btn_h), "EXPLORE AGAIN ⟳", on_click=self.on_play_again, sound_manager=self.sound_manager, accent_color=COLOR_GOLD)
        self.menu_btn = Button(pygame.Rect(SCREEN_WIDTH // 2 - 260, 480, btn_w, btn_h), "MAIN MENU", on_click=self.on_menu, sound_manager=self.sound_manager, accent_color=COLOR_NEON_TEAL)

    def update(self, cursor_x: int, cursor_y: int, is_clicked: bool, dt: float) -> None:
        self.again_btn.update(cursor_x, cursor_y, is_clicked, dt)
        self.menu_btn.update(cursor_x, cursor_y, is_clicked, dt)

    def draw(self, surface: pygame.Surface, total_score: int) -> None:
        modal_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        modal_surf.fill((6, 20, 36, 240))
        surface.blit(modal_surf, (0, 0))

        # Victory Panel
        panel_w = 680
        panel_h = 470
        px = SCREEN_WIDTH // 2 - panel_w // 2
        py = 70
        pygame.draw.rect(surface, (14, 30, 58), (px, py, panel_w, panel_h), border_radius=18)
        pygame.draw.rect(surface, COLOR_GOLD, (px, py, panel_w, panel_h), width=3, border_radius=18)

        t_surf = self.font_title.render("EXPEDITION VICTORIOUS!", True, COLOR_GOLD)
        surface.blit(t_surf, (SCREEN_WIDTH // 2 - t_surf.get_width() // 2, py + 25))

        sub_surf = self.font_sub.render("All 5 Oceanic Zones Conquered", True, COLOR_NEON_TEAL)
        surface.blit(sub_surf, (SCREEN_WIDTH // 2 - sub_surf.get_width() // 2, py + 75))

        # Title Award
        award_title = "MASTER ABYSSAL ARCHAEOLOGIST"
        aw_surf = self.font_sub.render(f"RANK: {award_title}", True, COLOR_EMERALD)
        surface.blit(aw_surf, (SCREEN_WIDTH // 2 - aw_surf.get_width() // 2, py + 130))

        score_s = self.font_title.render(f"FINAL SCORE: {total_score:,}", True, COLOR_WHITE)
        surface.blit(score_s, (SCREEN_WIDTH // 2 - score_s.get_width() // 2, py + 185))

        desc_lines = [
            "You have recovered the sacred crown from the Sunken Temple of the Ancients.",
            "Your vision-guided precision outsmarted deceptive counterfeits and dangerous naval mines.",
            "A legendary achievement in underwater robotics and computer vision!"
        ]
        for idx, line in enumerate(desc_lines):
            l_s = self.font_label.render(line, True, (200, 225, 245))
            surface.blit(l_s, (SCREEN_WIDTH // 2 - l_s.get_width() // 2, py + 260 + idx * 28))

        self.menu_btn.draw(surface)
        self.again_btn.draw(surface)


class LevelSelectScreen:
    """Attractive level selection screen showing unlocked oceanic zones and objectives."""

    def __init__(
        self,
        on_select_level: Callable[[int], None],
        on_back: Callable[[], None],
        sound_manager: Optional[SoundManager] = None
    ):
        self.on_select_level = on_select_level
        self.on_back = on_back
        self.sound_manager = sound_manager

        self.font_title = pygame.font.SysFont("segoeui", 34, bold=True)
        self.font_sub = pygame.font.SysFont("segoeui", 17)
        self.font_card_title = pygame.font.SysFont("segoeui", 18, bold=True)
        self.font_card_desc = pygame.font.SysFont("segoeui", 12)
        self.font_badge = pygame.font.SysFont("segoeui", 13, bold=True)

        self.buttons = []
        self.card_dwells = {i: 0.0 for i in range(1, 6)}
        self._init_buttons()

    def _init_buttons(self) -> None:
        btn_w, btn_h = 240, 48
        self.back_btn = Button(
            pygame.Rect(SCREEN_WIDTH // 2 - btn_w // 2, SCREEN_HEIGHT - 70, btn_w, btn_h),
            "◀ MAIN MENU",
            on_click=self.on_back,
            sound_manager=self.sound_manager,
            accent_color=COLOR_NEON_TEAL
        )

    def update(self, cursor_x: int, cursor_y: int, is_clicked: bool, dt: float, unlocked_levels: int, completed_levels: set) -> None:
        self.back_btn.update(cursor_x, cursor_y, is_clicked, dt)
        
        # Check level cards click / pinch or hover dwell (0.50s steady point)
        card_w = 215
        card_h = 280
        start_x = 65
        spacing = 235
        card_y = 120

        for lvl_id in range(1, 6):
            cx = start_x + (lvl_id - 1) * spacing
            btn_rect = pygame.Rect(cx + 15, card_y + card_h - 52, card_w - 30, 38)
            card_rect = pygame.Rect(cx, card_y, card_w, card_h)
            is_unlocked = (lvl_id <= unlocked_levels)
            
            is_hovered = is_unlocked and (btn_rect.collidepoint(cursor_x, cursor_y) or card_rect.collidepoint(cursor_x, cursor_y))
            if is_hovered:
                self.card_dwells[lvl_id] += dt
            else:
                self.card_dwells[lvl_id] = max(0.0, self.card_dwells[lvl_id] - dt * 2.0)

            dwell_trigger = (self.card_dwells[lvl_id] >= 0.50)
            
            if is_unlocked and (btn_rect.collidepoint(cursor_x, cursor_y) or card_rect.collidepoint(cursor_x, cursor_y)) and (is_clicked or dwell_trigger):
                if self.sound_manager:
                    self.sound_manager.play('click')
                self.card_dwells[lvl_id] = 0.0
                self.on_select_level(lvl_id)
                break

    def draw(self, surface: pygame.Surface, unlocked_levels: int, completed_levels: set) -> None:
        bg_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        bg_surf.fill((6, 16, 32, 240))
        surface.blit(bg_surf, (0, 0))

        # Title
        t_surf = self.font_title.render("EXPEDITION ZONE SELECT", True, COLOR_GOLD)
        s_surf = self.font_sub.render("Choose an oceanic depth layer to explore and recover ancient relics", True, COLOR_OCEAN_CYAN)
        surface.blit(t_surf, (SCREEN_WIDTH // 2 - t_surf.get_width() // 2, 25))
        surface.blit(s_surf, (SCREEN_WIDTH // 2 - s_surf.get_width() // 2, 70))

        card_w = 215
        card_h = 280
        start_x = 65
        spacing = 235
        card_y = 120

        from config import LEVELS

        for lvl_id in range(1, 6):
            cfg = LEVELS[lvl_id]
            cx = start_x + (lvl_id - 1) * spacing
            card_rect = pygame.Rect(cx, card_y, card_w, card_h)
            
            is_unlocked = (lvl_id <= unlocked_levels)
            is_completed = (lvl_id in completed_levels)

            # Card Background
            c_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            bg_col = (14, 28, 52, 210) if is_unlocked else (15, 20, 28, 180)
            c_surf.fill(bg_col)
            border_col = COLOR_GOLD if is_completed else (COLOR_NEON_TEAL if is_unlocked else (40, 55, 75))
            pygame.draw.rect(c_surf, border_col, (0, 0, card_w, card_h), width=2, border_radius=12)
            surface.blit(c_surf, (cx, card_y))

            # Level Badge
            status_text = "✓ COMPLETED" if is_completed else ("AVAILABLE" if is_unlocked else "🔒 LOCKED")
            status_col = COLOR_EMERALD if is_completed else (COLOR_GOLD if is_unlocked else (120, 140, 160))
            b_surf = self.font_badge.render(status_text, True, status_col)
            surface.blit(b_surf, (cx + card_w // 2 - b_surf.get_width() // 2, card_y + 14))

            # Level Name
            n_surf = self.font_card_title.render(f"LVL {lvl_id}", True, COLOR_WHITE)
            name_s = self.font_card_title.render(cfg.name.upper(), True, border_col)
            surface.blit(n_surf, (cx + card_w // 2 - n_surf.get_width() // 2, card_y + 40))
            surface.blit(name_s, (cx + card_w // 2 - name_s.get_width() // 2, card_y + 64))

            # Objective requirement
            obj_str = f"Goal: Deposit {cfg.required_deposits} Relics"
            o_surf = self.font_badge.render(obj_str, True, COLOR_WHITE if is_unlocked else (100, 115, 130))
            surface.blit(o_surf, (cx + card_w // 2 - o_surf.get_width() // 2, card_y + 105))

            # Description wrapped
            words = cfg.description.split(" ")
            line = ""
            line_y = card_y + 135
            for w in words:
                test_line = f"{line} {w}".strip()
                if self.font_card_desc.size(test_line)[0] < card_w - 24:
                    line = test_line
                else:
                    l_s = self.font_card_desc.render(line, True, (170, 195, 215) if is_unlocked else (90, 105, 120))
                    surface.blit(l_s, (cx + 14, line_y))
                    line_y += 16
                    line = w
            if line:
                l_s = self.font_card_desc.render(line, True, (170, 195, 215) if is_unlocked else (90, 105, 120))
                surface.blit(l_s, (cx + 14, line_y))

            # Action Button
            btn_rect = pygame.Rect(cx + 15, card_y + card_h - 52, card_w - 30, 38)
            if is_unlocked:
                pygame.draw.rect(surface, (20, 50, 85), btn_rect, border_radius=8)
                pygame.draw.rect(surface, border_col, btn_rect, width=2, border_radius=8)
                btn_lbl = self.font_badge.render("DIVE IN ▶", True, COLOR_WHITE)
                surface.blit(btn_lbl, (btn_rect.centerx - btn_lbl.get_width() // 2, btn_rect.centery - btn_lbl.get_height() // 2))

                # Dwell progress meter (filling up when pointing at card)
                if self.card_dwells[lvl_id] > 0:
                    pct = min(1.0, max(0.0, self.card_dwells[lvl_id] / 0.50))
                    bar_w = int((btn_rect.width - 8) * pct)
                    if bar_w > 0:
                        pygame.draw.rect(surface, COLOR_GOLD, (btn_rect.left + 4, btn_rect.bottom - 4, bar_w, 3), border_radius=2)
            else:
                pygame.draw.rect(surface, (20, 25, 35), btn_rect, border_radius=8)
                pygame.draw.rect(surface, (50, 60, 75), btn_rect, width=1, border_radius=8)
                btn_lbl = self.font_badge.render("LOCKED", True, (100, 115, 130))
                surface.blit(btn_lbl, (btn_rect.centerx - btn_lbl.get_width() // 2, btn_rect.centery - btn_lbl.get_height() // 2))

        self.back_btn.draw(surface)


class ChallengeScreen:
    """Displays high-stakes abyssal challenges with glassmorphic cards and hover dwell."""

    def __init__(
        self,
        on_start_challenge: Callable[[int], None],
        on_back: Callable[[], None],
        sound_manager: Optional[SoundManager] = None
    ):
        self.on_start_challenge = on_start_challenge
        self.on_back = on_back
        self.sound_manager = sound_manager

        self.font_title = pygame.font.SysFont("segoeui", 34, bold=True)
        self.font_sub = pygame.font.SysFont("segoeui", 17)
        self.font_card_title = pygame.font.SysFont("segoeui", 18, bold=True)
        self.font_card_sub = pygame.font.SysFont("segoeui", 13, bold=True)
        self.font_card_desc = pygame.font.SysFont("segoeui", 12)
        self.font_badge = pygame.font.SysFont("segoeui", 13, bold=True)
        self.font_icon = pygame.font.SysFont("segoeuiemoji", 28)

        self.card_dwells = {i: 0.0 for i in (1, 2, 3)}
        btn_w, btn_h = 240, 48
        self.back_btn = Button(
            pygame.Rect(SCREEN_WIDTH // 2 - btn_w // 2, SCREEN_HEIGHT - 70, btn_w, btn_h),
            "◀ MAIN MENU",
            on_click=self.on_back,
            sound_manager=self.sound_manager,
            accent_color=COLOR_NEON_TEAL
        )

    def update(self, cursor_x: int, cursor_y: int, is_clicked: bool, dt: float) -> None:
        self.back_btn.update(cursor_x, cursor_y, is_clicked, dt)

        card_w = 340
        card_h = 360
        start_x = (SCREEN_WIDTH - (3 * card_w + 2 * 30)) // 2
        spacing = card_w + 30
        card_y = 135

        for cid in (1, 2, 3):
            cx = start_x + (cid - 1) * spacing
            btn_rect = pygame.Rect(cx + 20, card_y + card_h - 55, card_w - 40, 40)
            card_rect = pygame.Rect(cx, card_y, card_w, card_h)

            is_hovered = (btn_rect.collidepoint(cursor_x, cursor_y) or card_rect.collidepoint(cursor_x, cursor_y))
            if is_hovered:
                self.card_dwells[cid] += dt
            else:
                self.card_dwells[cid] = max(0.0, self.card_dwells[cid] - dt * 2.0)

            dwell_trigger = (self.card_dwells[cid] >= 0.50)
            if is_hovered and (is_clicked or dwell_trigger):
                if self.sound_manager:
                    self.sound_manager.play('click')
                self.card_dwells[cid] = 0.0
                self.on_start_challenge(cid)
                break

    def draw(self, surface: pygame.Surface) -> None:
        bg_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        bg_surf.fill((6, 14, 30, 245))
        surface.blit(bg_surf, (0, 0))

        # Title
        t_surf = self.font_title.render("EXPEDITION CHALLENGES ⚡", True, COLOR_GOLD)
        s_surf = self.font_sub.render("High-stakes abyssal trials testing your computer vision reflexes and precision", True, COLOR_OCEAN_CYAN)
        surface.blit(t_surf, (SCREEN_WIDTH // 2 - t_surf.get_width() // 2, 25))
        surface.blit(s_surf, (SCREEN_WIDTH // 2 - s_surf.get_width() // 2, 72))

        from config import CHALLENGES

        card_w = 340
        card_h = 360
        start_x = (SCREEN_WIDTH - (3 * card_w + 2 * 30)) // 2
        spacing = card_w + 30
        card_y = 135

        for cid in (1, 2, 3):
            cfg = CHALLENGES[cid]
            cx = start_x + (cid - 1) * spacing
            card_rect = pygame.Rect(cx, card_y, card_w, card_h)

            # Card background
            c_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            c_surf.fill((14, 26, 48, 220))
            pygame.draw.rect(c_surf, cfg.accent_color, (0, 0, card_w, card_h), width=2, border_radius=14)
            surface.blit(c_surf, (cx, card_y))

            # Icon & Badge
            icon_s = self.font_icon.render(cfg.badge_icon, True, COLOR_WHITE)
            surface.blit(icon_s, (cx + 20, card_y + 16))

            badge_text = f"TRIAL #{cid}"
            b_s = self.font_badge.render(badge_text, True, cfg.accent_color)
            surface.blit(b_s, (cx + 62, card_y + 22))

            # Title
            t_s = self.font_card_title.render(cfg.title, True, COLOR_WHITE)
            surface.blit(t_s, (cx + 20, card_y + 56))

            sub_s = self.font_card_sub.render(cfg.subtitle, True, COLOR_NEON_TEAL)
            surface.blit(sub_s, (cx + 20, card_y + 82))

            # Description wrapped
            words = cfg.description.split(" ")
            line = ""
            line_y = card_y + 112
            for w in words:
                test_line = f"{line} {w}".strip()
                if self.font_card_desc.size(test_line)[0] < card_w - 40:
                    line = test_line
                else:
                    l_s = self.font_card_desc.render(line, True, (190, 215, 235))
                    surface.blit(l_s, (cx + 20, line_y))
                    line_y += 18
                    line = w
            if line:
                l_s = self.font_card_desc.render(line, True, (190, 215, 235))
                surface.blit(l_s, (cx + 20, line_y))

            # Targets bar
            tgt_text = f"Goal: {cfg.required_deposits} Relics  |  Time: {int(cfg.time_limit)}s"
            tgt_s = self.font_badge.render(tgt_text, True, COLOR_GOLD)
            surface.blit(tgt_s, (cx + 20, card_y + card_h - 90))

            # Action Button
            btn_rect = pygame.Rect(cx + 20, card_y + card_h - 55, card_w - 40, 40)
            pygame.draw.rect(surface, (18, 48, 80), btn_rect, border_radius=8)
            pygame.draw.rect(surface, cfg.accent_color, btn_rect, width=2, border_radius=8)
            btn_lbl = self.font_badge.render("START CHALLENGE ▶", True, COLOR_WHITE)
            surface.blit(btn_lbl, (btn_rect.centerx - btn_lbl.get_width() // 2, btn_rect.centery - btn_lbl.get_height() // 2))

            # Dwell meter
            if self.card_dwells[cid] > 0:
                pct = min(1.0, max(0.0, self.card_dwells[cid] / 0.50))
                bar_w = int((btn_rect.width - 8) * pct)
                if bar_w > 0:
                    pygame.draw.rect(surface, COLOR_GOLD, (btn_rect.left + 4, btn_rect.bottom - 4, bar_w, 3), border_radius=2)

        self.back_btn.draw(surface)


