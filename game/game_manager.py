"""
Underwater Treasure Hunt - Master Game Engine
Orchestrates computer vision tracking, the underwater swimmer character,
relic grab/carry/deposit mechanics, level progression, and UI state machines.
"""

from enum import Enum
import math
import sys
import time
from typing import Optional, Tuple, Set
import pygame

from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    TARGET_FPS,
    FULLSCREEN,
    TITLE,
    LEVELS,
    COLOR_OCEAN_CYAN,
    COLOR_NEON_TEAL,
    COLOR_GOLD,
    COLOR_CORAL_RED,
    COLOR_AMBER_WARNING,
    COLOR_WHITE,
    COLOR_EMERALD,
)
from audio.sound_manager import SoundManager
from hand_tracking.hand_detector import HandDetector
from hand_tracking.gesture_detector import GestureDetector, GestureType
from game.particles import ParticleSystem
from game.player import Player
from game.level import Level
from game.treasure import TreasureType
from ui.hud import HUD
from ui.menu import MainMenu
from ui.instructions import HowToPlayScreen
from ui.screens import (
    CameraCheckScreen,
    PauseScreen,
    LevelCompleteScreen,
    GameOverScreen,
    VictoryScreen,
    LevelSelectScreen,
)

class GameState(Enum):
    MAIN_MENU = "MAIN_MENU"
    LEVEL_SELECT = "LEVEL_SELECT"
    HOW_TO_PLAY = "HOW_TO_PLAY"
    CAMERA_CHECK = "CAMERA_CHECK"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    LEVEL_COMPLETE = "LEVEL_COMPLETE"
    GAME_OVER = "GAME_OVER"
    VICTORY = "VICTORY"

class GameManager:
    """Central engine controlling vision tracking, swimmer physics, game logic, and UI."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        
        # Ensure mouse cursor is visible at all times
        pygame.mouse.set_visible(True)
        
        # Display setup: start in full screen with aspect-ratio auto-scaling
        self.is_fullscreen: bool = FULLSCREEN
        flags = (pygame.FULLSCREEN | pygame.SCALED) if self.is_fullscreen else 0
        try:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
        except Exception:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.is_fullscreen = False

        self.clock = pygame.time.Clock()
        self.running = True

        # Input & Cursor Tracking
        self.last_mouse_time: float = 0.0
        self.last_mouse_move_time: float = 0.0
        self.last_cursor_pos: Tuple[int, int] = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.is_hand_detected: bool = False
        self.treasure_hover_dwell: float = 0.0

        # Diagnostics & Options
        self.debug_mode = False
        self.current_state = GameState.MAIN_MENU

        # Core Subsystems
        self.sound_manager = SoundManager()
        self.hand_detector = HandDetector()
        self.gesture_detector = GestureDetector()
        self.particles = ParticleSystem()
        self.player = Player()

        # Levels & Progression
        self.current_level_id = 1
        self.unlocked_levels = 1
        self.completed_levels = set()
        self.current_level: Optional[Level] = None
        self.game_over_reason = "Oxygen Depleted"

        # Vision Pipeline initialization
        self.hand_detector.start()

        # UI Subsystems
        self.hud = HUD()
        self._init_screens()

    def _init_screens(self) -> None:
        """Instantiates all menu and modal screens."""
        self.menu_screen = MainMenu(
            on_play=self.start_new_expedition,
            on_level_select=lambda: self.set_state(GameState.LEVEL_SELECT),
            on_instructions=lambda: self.set_state(GameState.HOW_TO_PLAY),
            on_camera_check=lambda: self.set_state(GameState.CAMERA_CHECK),
            on_quit=self.quit_game,
            sound_manager=self.sound_manager
        )
        self.level_select_screen = LevelSelectScreen(
            on_select_level=self.select_level_and_play,
            on_back=lambda: self.set_state(GameState.MAIN_MENU),
            sound_manager=self.sound_manager
        )
        self.instructions_screen = HowToPlayScreen(
            on_back=lambda: self.set_state(GameState.MAIN_MENU),
            sound_manager=self.sound_manager
        )
        self.camera_check_screen = CameraCheckScreen(
            on_start_game=self.start_new_expedition,
            on_back=lambda: self.set_state(GameState.MAIN_MENU),
            sound_manager=self.sound_manager
        )
        self.pause_screen = PauseScreen(
            on_resume=lambda: self.set_state(GameState.PLAYING),
            on_restart=self.restart_current_level,
            on_menu=lambda: self.set_state(GameState.MAIN_MENU),
            sound_manager=self.sound_manager
        )
        self.level_complete_screen = LevelCompleteScreen(
            on_next_level=self.advance_to_next_level,
            on_menu=lambda: self.set_state(GameState.MAIN_MENU),
            sound_manager=self.sound_manager
        )
        self.game_over_screen = GameOverScreen(
            on_retry=self.restart_current_level,
            on_menu=lambda: self.set_state(GameState.MAIN_MENU),
            sound_manager=self.sound_manager
        )
        self.victory_screen = VictoryScreen(
            on_play_again=self.start_new_expedition,
            on_menu=lambda: self.set_state(GameState.MAIN_MENU),
            sound_manager=self.sound_manager
        )

    def set_state(self, new_state: GameState) -> None:
        """Transitions between game states."""
        self.current_state = new_state
        self.gesture_detector.reset()

    def start_new_expedition(self) -> None:
        """Starts game from Level 1 with full vitals."""
        self.current_level_id = 1
        self.player = Player()
        self.load_level(1)
        self.set_state(GameState.PLAYING)

    def select_level_and_play(self, level_id: int) -> None:
        """Jumps directly to selected unlocked level."""
        self.current_level_id = level_id
        self.load_level(level_id)
        self.set_state(GameState.PLAYING)

    def restart_current_level(self) -> None:
        """Restarts the active level with full oxygen."""
        self.load_level(self.current_level_id)
        self.set_state(GameState.PLAYING)

    def advance_to_next_level(self) -> None:
        """Advances to next level or triggers final victory screen."""
        if self.current_level_id < len(LEVELS):
            self.current_level_id += 1
            self.unlocked_levels = max(self.unlocked_levels, self.current_level_id)
            self.load_level(self.current_level_id)
            self.set_state(GameState.PLAYING)
        else:
            self.sound_manager.play('level_complete', volume_mult=1.0)
            self.set_state(GameState.VICTORY)

    def load_level(self, level_id: int) -> None:
        """Initializes game level environment and entities."""
        self.current_level = Level(level_id)
        self.player.reset_for_level()
        self.particles = ParticleSystem()
        self.gesture_detector.reset()

    def toggle_fullscreen(self) -> None:
        """Toggles between immersive fullscreen and windowed display mode."""
        self.is_fullscreen = not self.is_fullscreen
        try:
            flags = (pygame.FULLSCREEN | pygame.SCALED) if self.is_fullscreen else 0
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
        except Exception:
            pygame.display.toggle_fullscreen()

    def quit_game(self) -> None:
        """Cleans up threads and closes application."""
        self.running = False
        self.hand_detector.stop()
        pygame.quit()
        sys.exit(0)

    def run(self) -> None:
        """Master application loop running at target 60 FPS."""
        while self.running:
            dt = self.clock.tick(TARGET_FPS) / 1000.0
            dt = min(0.1, dt)  # Cap maximum delta time step

            self._handle_events()
            self._update(dt)
            self._render()

            pygame.display.flip()

    def _handle_events(self) -> None:
        """Dispatches Pygame keyboard and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_state == GameState.PLAYING:
                        self.set_state(GameState.PAUSED)
                    elif self.current_state == GameState.PAUSED:
                        self.set_state(GameState.PLAYING)
                    elif self.current_state in (GameState.HOW_TO_PLAY, GameState.CAMERA_CHECK, GameState.LEVEL_SELECT):
                        self.set_state(GameState.MAIN_MENU)
                elif event.key in (pygame.K_F11, pygame.K_f):
                    self.toggle_fullscreen()
                elif event.key == pygame.K_d:
                    self.debug_mode = not self.debug_mode
                elif event.key == pygame.K_m:
                    self.sound_manager.toggle_mute()

            elif event.type == pygame.MOUSEMOTION:
                if event.rel[0] != 0 or event.rel[1] != 0:
                    self.last_mouse_move_time = time.time()
                self.last_mouse_time = time.time()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.last_mouse_move_time = time.time()
                self.last_mouse_time = time.time()

    def _update(self, dt: float) -> None:
        """Executes computer vision gesture resolution and game world physics."""
        # 1. Vision Pipeline Update
        hand_data = self.hand_detector.get_latest_data()
        
        # Read fallback keyboard/mouse inputs
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed(3)
        lmb = mouse_buttons[0]
        rmb = mouse_buttons[2]
        keys = pygame.key.get_pressed()
        space_key = keys[pygame.K_SPACE]
        s_key = keys[pygame.K_s]

        # Prioritize Hand Tracking:
        # If webcam detects hand (including 550ms persistence buffer), hand controls the diver!
        # Mouse fallback engages ONLY when no hand has been detected AND user physically moved the mouse.
        mouse_active = (time.time() - self.last_mouse_move_time < 0.8)

        if hand_data.is_detected:
            gesture_output = self.gesture_detector.process_landmarks(
                hand_data.landmarks,
                hand_data.screen_x,
                hand_data.screen_y
            )
            # Physical mouse clicks and keyboard shortcuts still assist seamlessly
            if lmb:
                gesture_output["pinch_triggered"] = True
            if rmb:
                gesture_output["sonar_triggered"] = True
            if space_key:
                gesture_output["palm_triggered"] = True
            if s_key:
                gesture_output["shield_active"] = True
            self.is_hand_detected = True
        elif mouse_active:
            gesture_output = self.gesture_detector.update_fallback_mouse(
                mouse_x, mouse_y, lmb, rmb, space_key, s_key
            )
            self.is_hand_detected = False
        else:
            gesture_output = self.gesture_detector.maintain_position(
                lmb, rmb, space_key, s_key
            )
            self.is_hand_detected = False

        cursor_x, cursor_y = gesture_output["cursor_pos"]
        pinch_triggered = gesture_output["pinch_triggered"]
        palm_triggered = gesture_output["palm_triggered"]
        sonar_triggered = gesture_output["sonar_triggered"]
        shield_active = gesture_output["shield_active"]
        current_gesture = gesture_output["current_gesture"]

        self.last_cursor_pos = (cursor_x, cursor_y)

        # 2. State-Specific Updates
        if self.current_state == GameState.MAIN_MENU:
            self.menu_screen.update(cursor_x, cursor_y, pinch_triggered, dt)

        elif self.current_state == GameState.LEVEL_SELECT:
            self.level_select_screen.update(cursor_x, cursor_y, pinch_triggered, dt, self.unlocked_levels, self.completed_levels)

        elif self.current_state == GameState.HOW_TO_PLAY:
            self.instructions_screen.update(cursor_x, cursor_y, pinch_triggered, dt)

        elif self.current_state == GameState.CAMERA_CHECK:
            self.camera_check_screen.update(cursor_x, cursor_y, pinch_triggered, dt)

        elif self.current_state == GameState.PAUSED:
            self.pause_screen.update(cursor_x, cursor_y, pinch_triggered, dt)

        elif self.current_state == GameState.LEVEL_COMPLETE:
            self.level_complete_screen.update(cursor_x, cursor_y, pinch_triggered, dt)

        elif self.current_state == GameState.GAME_OVER:
            self.game_over_screen.update(cursor_x, cursor_y, pinch_triggered, dt)

        elif self.current_state == GameState.VICTORY:
            self.victory_screen.update(cursor_x, cursor_y, pinch_triggered, dt)

        elif self.current_state == GameState.PLAYING and self.current_level:
            self._update_gameplay(
                dt,
                cursor_x,
                cursor_y,
                pinch_triggered,
                palm_triggered,
                sonar_triggered,
                shield_active
            )

        # 3. Update Swimmer Kinematics & Particles
        is_pinching = (current_gesture == GestureType.PINCH or pinch_triggered)
        current_force = 180.0 if (self.player.current_active_timer > 0) else 0.0
        emit_regulator_bubble = self.player.update(dt, cursor_x, cursor_y, is_pinching, shield_active, current_force)
        
        # Scuba regulator bubble trail
        if emit_regulator_bubble:
            self.particles.emit_cursor_trail(self.player.x, self.player.y - 10)

        self.particles.update(dt, current_active=(self.player.current_active_timer > 0))

    def _update_gameplay(
        self,
        dt: float,
        target_x: int,
        target_y: int,
        pinch_triggered: bool,
        palm_triggered: bool,
        sonar_triggered: bool,
        shield_active: bool
    ) -> None:
        """Core interactive swimming, grabbing, carrying, and depositing logic."""
        current_active = (self.player.current_active_timer > 0)
        swimmer_pos = (self.player.x, self.player.y)
        
        # Sonar Trigger
        if sonar_triggered:
            if self.player.activate_sonar():
                self.sound_manager.play('sonar')
                self.particles.emit_sonar_pulse(self.player.x, self.player.y)
                self.current_level.treasure_manager.trigger_sonar_wave(self.player.x, self.player.y, 750.0)

        # Water Current Trigger
        if palm_triggered:
            if self.player.activate_water_current():
                self.sound_manager.play('current')
                self.particles.emit_water_current()

        # Update Level Environment, Fish, Hazards, Timers
        lvl_complete, time_expired, shark_hit, shark_deflected = self.current_level.update(
            dt,
            current_active,
            swimmer_pos,
            shield_active
        )

        # Shark Interaction Handling
        if shark_deflected:
            self.sound_manager.play('bubble')
            self.particles.emit_treasure_burst(self.player.x, self.player.y, count=10, color=COLOR_NEON_TEAL)
        elif shark_hit:
            self.sound_manager.play('trap')
            self.player.reduce_oxygen(35.0, shake_duration=0.5, shake_power=14.0)
            self.particles.emit_trap_explosion(self.player.x, self.player.y)
            self.particles.emit_score_popup(self.player.x, self.player.y, "-35% OXYGEN [SHARK BITE!]", COLOR_CORAL_RED)

        # Hovered Object Detection (Near Swimmer or Aim Target)
        hovered_item = (
            self.current_level.treasure_manager.get_hovered_treasure(self.player.x, self.player.y)
            or self.current_level.treasure_manager.get_hovered_treasure(target_x, target_y)
        )
        self.player.is_hovering_interactable = (hovered_item is not None)
        self.player.is_hovering_danger = (hovered_item is not None and hovered_item.revealed_timer > 0 and hovered_item.type in (TreasureType.FAKE, TreasureType.TRAP))

        # Hover dwell auto-click: holding cursor steadily over a genuine relic auto-collects it
        is_hovering_relic = (
            hovered_item is not None
            and not hovered_item.collected
            and hovered_item.type not in (TreasureType.TRAP, TreasureType.FAKE)
        )
        if is_hovering_relic:
            self.treasure_hover_dwell += dt
        else:
            self.treasure_hover_dwell = 0.0

        dwell_collect = (self.treasure_hover_dwell >= 0.45)
        if dwell_collect:
            self.treasure_hover_dwell = 0.0

        # Direct touch collection (swimmer swims directly onto a genuine relic)
        direct_touch = (
            hovered_item is not None
            and not hovered_item.collected
            and hovered_item.type not in (TreasureType.TRAP, TreasureType.FAKE)
            and math.hypot(self.player.x - hovered_item.x, self.player.y - hovered_item.y) <= (hovered_item.radius + 24.0)
        )

        # ============================================================
        # INSTANT PICKUP & AUTOMATIC TREASURE BOX STORAGE
        # ============================================================
        if (pinch_triggered or direct_touch or dwell_collect) and hovered_item and not hovered_item.collected:
            if hovered_item.type == TreasureType.TRAP:
                # Sea Mine Trap Detonates Immediately!
                hovered_item.collected = True
                self.sound_manager.play('trap')
                self.player.reduce_oxygen(hovered_item.oxygen_penalty, shake_duration=0.6, shake_power=16.0)
                self.particles.emit_trap_explosion(hovered_item.x, hovered_item.y)
                self.particles.emit_score_popup(hovered_item.x, hovered_item.y, "-25% OXYGEN [MINE!]", COLOR_CORAL_RED)

            elif hovered_item.type == TreasureType.FAKE:
                # Deceptive Counterfeit Penalty!
                hovered_item.collected = True
                self.sound_manager.play('fake_warning')
                self.player.add_score(hovered_item.score_value)
                self.player.reduce_oxygen(hovered_item.oxygen_penalty, shake_duration=0.4, shake_power=8.0)
                self.particles.emit_score_popup(hovered_item.x, hovered_item.y, f"{hovered_item.score_value} FAKE PENALTY!", COLOR_AMBER_WARNING)

            else:
                # Genuine Relic: Automatically Stored into the Treasure Box & Score!
                hovered_item.collected = True
                self.current_level.deposited_count += 1
                self.player.add_score(hovered_item.score_value)

                if hovered_item.type in (TreasureType.RARE, TreasureType.ANCIENT):
                    self.sound_manager.play('rare_treasure')
                else:
                    self.sound_manager.play('treasure')

                # Celebration visual burst at item location
                self.particles.emit_treasure_burst(hovered_item.x, hovered_item.y, count=24, color=hovered_item.base_color)
                self.particles.emit_score_popup(hovered_item.x, hovered_item.y - 25, f"+{hovered_item.score_value} IN TREASURE BOX! 🎁", COLOR_GOLD)

                # Visual spark cascade towards the seafloor collection vault
                chest = self.current_level.treasure_manager.chest
                self.particles.emit_treasure_burst(chest.x, chest.y - 10, count=10, color=COLOR_GOLD)

        # Check Level Completion (Objective Reached)
        if lvl_complete:
            self.completed_levels.add(self.current_level_id)
            self.unlocked_levels = max(self.unlocked_levels, self.current_level_id + 1)
            self.sound_manager.play('level_complete')
            self.set_state(GameState.LEVEL_COMPLETE)

        # Check Loss Conditions
        if self.player.oxygen <= 0:
            self.sound_manager.play('game_over')
            self.game_over_reason = "Oxygen Depleted"
            self.set_state(GameState.GAME_OVER)
        elif time_expired:
            self.sound_manager.play('game_over')
            self.game_over_reason = "Mission Time Expired"
            self.set_state(GameState.GAME_OVER)

    def _render(self) -> None:
        """Draws current game scene, overlays, and underwater swimmer."""
        shake_dx, shake_dy = self.player.get_screen_shake_offset()
        
        if shake_dx != 0 or shake_dy != 0:
            scene_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            scene_surf = self.screen

        # 1. State-Specific Rendering
        if self.current_state == GameState.MAIN_MENU:
            self.menu_screen.draw(scene_surf)

        elif self.current_state == GameState.LEVEL_SELECT:
            self.level_select_screen.draw(scene_surf, self.unlocked_levels, self.completed_levels)

        elif self.current_state == GameState.HOW_TO_PLAY:
            self.instructions_screen.draw(scene_surf)

        elif self.current_state == GameState.CAMERA_CHECK:
            hand_data = self.hand_detector.get_latest_data()
            annotated_frame = None
            if hand_data.raw_frame is not None:
                annotated_frame = self.hand_detector.render_debug_overlay(hand_data.raw_frame, hand_data.landmarks)
            
            self.camera_check_screen.draw(
                scene_surf,
                raw_frame=annotated_frame,
                camera_available=self.hand_detector.is_camera_available,
                hand_detected=hand_data.is_detected,
                current_gesture=self.gesture_detector.current_gesture,
                pinch_dist=self.gesture_detector.pinch_distance,
                camera_fps=self.hand_detector.actual_fps
            )

        elif self.current_state in (GameState.PLAYING, GameState.PAUSED, GameState.LEVEL_COMPLETE, GameState.GAME_OVER, GameState.VICTORY):
            if self.current_level:
                # Level Scenery & Sea Floor
                self.current_level.draw_background(scene_surf, current_active=(self.player.current_active_timer > 0))
                # Ambient Bubbles & Volumetric God Rays
                self.particles.draw_ambient(scene_surf)
                # Marine Life (Fish & Sharks)
                self.current_level.marine_manager.draw(scene_surf)
                # Interactive Treasures & Treasure Chest Depot
                self.current_level.treasure_manager.draw(scene_surf)
                
                # Active Underwater Swimmer Explorer
                self.player.draw_swimmer(scene_surf)

                # Depth Fog
                self.current_level.draw_fog(scene_surf)
                # Foreground Visual Effects & Streams
                self.particles.draw_foreground(scene_surf)

                # In-Game HUD with Objective Progress & Carry status
                carried_name = self.player.carried_treasure.type.value if self.player.carried_treasure else None
                self.hud.draw(
                    scene_surf,
                    level_id=self.current_level.level_id,
                    level_name=self.current_level.config.name,
                    deposited_count=self.current_level.deposited_count,
                    required_deposits=self.current_level.required_deposits,
                    score=self.player.score,
                    display_oxygen=self.player.display_oxygen,
                    time_remaining=self.current_level.time_remaining,
                    sonar_charges=self.player.sonar_charges,
                    current_gesture=self.gesture_detector.current_gesture,
                    is_shield_active=self.player.shield_active,
                    water_current_active=(self.player.current_active_timer > 0),
                    carried_treasure_type=carried_name
                )

            # State Modals
            if self.current_state == GameState.PAUSED:
                self.pause_screen.draw(scene_surf)
            elif self.current_state == GameState.LEVEL_COMPLETE:
                self.level_complete_screen.draw(
                    scene_surf,
                    level_name=self.current_level.config.name,
                    level_score=self.player.level_score,
                    total_score=self.player.score,
                    remaining_oxygen=self.player.oxygen
                )
            elif self.current_state == GameState.GAME_OVER:
                self.game_over_screen.draw(
                    scene_surf,
                    reason=self.game_over_reason,
                    score=self.player.score,
                    level_name=self.current_level.config.name
                )
            elif self.current_state == GameState.VICTORY:
                self.victory_screen.draw(scene_surf, total_score=self.player.score)

        # 2. Render Hand Tracking Reticle (if hand is detected by webcam)
        if self.is_hand_detected:
            hx, hy = self.last_cursor_pos
            pulse = math.sin(time.time() * 6.0) * 3.0
            r = int(16 + pulse)
            reticle_surf = pygame.Surface((r * 2 + 30, r * 2 + 30), pygame.SRCALPHA)
            rcx, rcy = r + 15, r + 15
            
            # Gesture color and label
            cur_g = self.gesture_detector.current_gesture
            if cur_g == GestureType.PINCH:
                ring_col = (*COLOR_GOLD[:3], 220)
                pip_col = COLOR_GOLD
                label_text = "INDEX CLICK 👆"
            elif cur_g == GestureType.TWO_FINGERS:
                ring_col = (*COLOR_OCEAN_CYAN[:3], 220)
                pip_col = COLOR_OCEAN_CYAN
                label_text = "SONAR ✌️"
            elif cur_g == GestureType.OPEN_PALM:
                ring_col = (*COLOR_WHITE[:3], 230)
                pip_col = COLOR_WHITE
                label_text = "CURRENT ✋"
            elif cur_g == GestureType.FIST:
                ring_col = (*COLOR_NEON_TEAL[:3], 230)
                pip_col = COLOR_NEON_TEAL
                label_text = "SHIELD ✊"
            else:
                ring_col = (*COLOR_NEON_TEAL[:3], 160)
                pip_col = COLOR_NEON_TEAL
                label_text = "HAND 🖐️"

            # Outer ring & pips
            pygame.draw.circle(reticle_surf, ring_col, (rcx, rcy), r, 2)
            pygame.draw.circle(reticle_surf, (*pip_col[:3], 200), (rcx, rcy), 3)
            pygame.draw.line(reticle_surf, pip_col, (rcx - r - 4, rcy), (rcx - r + 3, rcy), 2)
            pygame.draw.line(reticle_surf, pip_col, (rcx + r - 3, rcy), (rcx + r + 4, rcy), 2)
            pygame.draw.line(reticle_surf, pip_col, (rcx, rcy - r - 4), (rcx, rcy - r + 3), 2)
            pygame.draw.line(reticle_surf, pip_col, (rcx, rcy + r - 3), (rcx, rcy + r + 4), 2)
            
            # Blit reticle
            scene_surf.blit(reticle_surf, (hx - rcx, hy - rcy))

            # Small floating label next to hand reticle
            g_font = pygame.font.SysFont("segoeui", 11, bold=True)
            lbl = g_font.render(label_text, True, pip_col)
            scene_surf.blit(lbl, (hx + r + 8, hy - 8))

        # 3. Blit Screen Shake if active
        if shake_dx != 0 or shake_dy != 0:
            self.screen.fill((0, 0, 0))
            self.screen.blit(scene_surf, (shake_dx, shake_dy))

        # 4. Optional Debug Diagnostics Overlay
        if self.debug_mode:
            self._render_debug_overlay()

    def _render_debug_overlay(self) -> None:
        """Renders technical diagnostics overlay when 'D' key is active."""
        debug_surf = pygame.Surface((340, 240), pygame.SRCALPHA)
        debug_surf.fill((5, 10, 20, 210))
        pygame.draw.rect(debug_surf, COLOR_GOLD, (0, 0, 340, 240), width=2, border_radius=8)

        font = pygame.font.SysFont("consolas", 13)
        fps = self.clock.get_fps()
        cam_fps = self.hand_detector.actual_fps
        g_name = self.gesture_detector.current_gesture.value
        p_dist = self.gesture_detector.pinch_distance
        hand_detected = self.hand_detector.get_latest_data().is_detected
        carrying = self.player.carried_treasure.type.value if self.player.carried_treasure else "None"

        lines = [
            f"=== VISION & ENGINE DEBUG ===",
            f"Render FPS   : {fps:.1f} / 60.0",
            f"Camera FPS   : {cam_fps:.1f}",
            f"Hand Detected: {hand_detected}",
            f"Gesture State: {g_name}",
            f"Pinch Dist   : {p_dist:.4f}",
            f"Carrying Item: {carrying}",
            f"Swimmer Pos  : ({int(self.player.x)}, {int(self.player.y)})",
            f"Active State : {self.current_state.value}",
            f"Press 'D' to hide debug overlay",
        ]

        for i, l in enumerate(lines):
            col = COLOR_GOLD if i == 0 else COLOR_WHITE
            s = font.render(l, True, col)
            debug_surf.blit(s, (12, 10 + i * 20))

        self.screen.blit(debug_surf, (20, 95))
