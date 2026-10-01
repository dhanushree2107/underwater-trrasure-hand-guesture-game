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
    CHALLENGES,
    PASSIVE_OXYGEN_DEPLETION_RATE,
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
from hand_tracking.hand_motion import HandMotionTracker, DualSwimMotionResult, SwimTrackingStatus
from game.particles import ParticleSystem
from game.player import Player
from game.level import Level
from game.treasure import TreasureType
from game.missions import MissionManager
from game.inventory import DiverInventory, UnderwaterMuseum
from game.events import OceanEventManager, OceanCondition
from ui.tutorial import SmartTutorial
from ui.hud import HUD
from ui.menu import MainMenu
from ui.instructions import HowToPlayScreen
from ui.cursor import HandCursor, CursorTargetState
from ui.screens import (
    CameraCheckScreen,
    PauseScreen,
    LevelCompleteScreen,
    GameOverScreen,
    VictoryScreen,
    LevelSelectScreen,
    ChallengeScreen,
    MuseumScreen,
)

class GameState(Enum):
    MAIN_MENU = "MAIN_MENU"
    LEVEL_SELECT = "LEVEL_SELECT"
    MUSEUM = "MUSEUM"
    CHALLENGES = "CHALLENGES"
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
        
        # Hide standard desktop OS cursor in favor of custom vision hand cursor
        pygame.mouse.set_visible(False)
        
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

        # Custom Glowing Vision Hand Cursor
        self.hand_cursor = HandCursor()

        # Input & Cursor Tracking
        self.last_mouse_time: float = 0.0
        self.last_mouse_move_time: float = 0.0
        self.last_cursor_pos: Tuple[int, int] = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.is_hand_detected: bool = False
        self.treasure_hover_dwell: float = 0.0

        # Challenges, Combos, and Dynamic Events
        self.active_challenge_id: Optional[int] = None
        self.combo_count: int = 0
        self.combo_multiplier: float = 1.0
        self.whirlpool_timer: float = 0.0
        self.octopus_timer: float = 0.0

        # Diagnostics & Options
        self.debug_mode = False
        self.current_state = GameState.MAIN_MENU

        # Core Subsystems
        self.sound_manager = SoundManager()
        self.hand_detector = HandDetector()
        self.gesture_detector = GestureDetector()
        self.motion_tracker = HandMotionTracker()
        self.mission_manager = MissionManager()
        self.inventory = DiverInventory()
        self.museum = UnderwaterMuseum()
        self.ocean_events = OceanEventManager()
        self.tutorial = SmartTutorial()
        self.particles = ParticleSystem()
        self.player = Player()

        self.last_motion_result: Optional[DualSwimMotionResult] = None
        self.last_stars: int = 3
        self.last_side_missions_done: int = 0

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
            on_challenges=lambda: self.set_state(GameState.CHALLENGES),
            on_instructions=lambda: self.set_state(GameState.HOW_TO_PLAY),
            on_camera_check=lambda: self.set_state(GameState.CAMERA_CHECK),
            on_quit=self.quit_game,
            on_museum=lambda: self.set_state(GameState.MUSEUM),
            sound_manager=self.sound_manager
        )
        self.level_select_screen = LevelSelectScreen(
            on_select_level=self.select_level_and_play,
            on_back=lambda: self.set_state(GameState.MAIN_MENU),
            sound_manager=self.sound_manager
        )
        self.challenge_screen = ChallengeScreen(
            on_start_challenge=self.start_challenge,
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
        self.museum_screen = MuseumScreen(
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
            on_replay=self.restart_current_level,
            on_museum=lambda: self.set_state(GameState.MUSEUM),
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
        self.active_challenge_id = None
        self.combo_count = 0
        self.combo_multiplier = 1.0
        self.current_level_id = 1
        self.player = Player()
        self.load_level(1)
        self.set_state(GameState.PLAYING)

    def select_level_and_play(self, level_id: int) -> None:
        """Jumps directly to selected unlocked level."""
        self.active_challenge_id = None
        self.combo_count = 0
        self.combo_multiplier = 1.0
        self.current_level_id = level_id
        self.load_level(level_id)
        self.set_state(GameState.PLAYING)

    def start_challenge(self, challenge_id: int) -> None:
        """Launches a high-stakes abyssal challenge trial."""
        self.active_challenge_id = challenge_id
        cfg = CHALLENGES[challenge_id]
        self.current_level_id = cfg.level_config.level_id
        self.player = Player()
        self.current_level = Level(1)
        # Apply custom challenge parameters
        self.current_level.config = cfg.level_config
        self.current_level.level_id = cfg.level_config.level_id
        self.current_level.time_remaining = cfg.time_limit
        self.current_level.required_deposits = cfg.required_deposits
        self.current_level.deposited_count = 0
        
        # Spawn tailored challenge treasures & hazards
        self.current_level.treasure_manager.spawn_level_treasures(
            common_count=cfg.level_config.common_treasures,
            gold_count=cfg.level_config.gold_treasures,
            rare_count=cfg.level_config.rare_treasures,
            ancient_count=cfg.level_config.ancient_treasures,
            fake_count=cfg.level_config.fake_treasures,
            trap_count=cfg.level_config.traps,
            screen_w=SCREEN_WIDTH,
            screen_h=SCREEN_HEIGHT
        )
        if cfg.jellyfish_count > 0:
            self.current_level.marine_manager.spawn_jellyfish(cfg.jellyfish_count)

        self.particles = ParticleSystem()
        self.gesture_detector.reset()
        self.combo_count = 0
        self.combo_multiplier = 1.0
        self.set_state(GameState.PLAYING)

    def restart_current_level(self) -> None:
        """Restarts the active level or challenge with full oxygen."""
        if self.active_challenge_id is not None:
            self.start_challenge(self.active_challenge_id)
        else:
            self.combo_count = 0
            self.combo_multiplier = 1.0
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
        """Initializes game level environment, missions, and ocean events."""
        self.current_level = Level(level_id)
        self.player.reset_for_level()
        self.particles = ParticleSystem()
        self.gesture_detector.reset()
        self.motion_tracker.reset()
        self.whirlpool_timer = 0.0
        self.octopus_timer = 0.0
        self.mission_manager.start_level(level_id, self.current_level.required_deposits)
        self.inventory.clear()
        self.ocean_events.start_level(level_id)
        if level_id == 1:
            self.tutorial.start_tutorial()
        else:
            self.tutorial.active = False

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
                    elif self.current_state in (GameState.HOW_TO_PLAY, GameState.CAMERA_CHECK, GameState.LEVEL_SELECT, GameState.CHALLENGES):
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
            if hand_data.has_second_hand:
                gesture_output = self.gesture_detector.process_dual_landmarks(
                    hand1_landmarks=hand_data.landmarks,
                    hand1_x=hand_data.screen_x,
                    hand1_y=hand_data.screen_y,
                    hand1_label=hand_data.handedness,
                    hand2_landmarks=hand_data.second_landmarks,
                    hand2_x=hand_data.second_screen_x,
                    hand2_y=hand_data.second_screen_y,
                    hand2_label=hand_data.second_handedness,
                    swim_target_x=hand_data.swim_target_x,
                    swim_target_y=hand_data.swim_target_y,
                    paddle_speed=hand_data.paddle_stroke_speed,
                )
            else:
                gesture_output = self.gesture_detector.process_landmarks(
                    hand_data.landmarks,
                    hand_data.screen_x,
                    hand_data.screen_y
                )
            # Physical mouse clicks and keyboard shortcuts still assist seamlessly
            if lmb:
                gesture_output["pinch_triggered"] = True
                gesture_output["is_pinching"] = True
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
        current_gesture = gesture_output["current_gesture"]
        is_pinching_active = gesture_output.get("is_pinching", (current_gesture == GestureType.PINCH or pinch_triggered))
        palm_triggered = gesture_output["palm_triggered"]
        sonar_triggered = gesture_output["sonar_triggered"]
        shield_active = gesture_output["shield_active"]
        is_mega_palm = gesture_output.get("is_mega_palm", False)
        has_dual_hands = gesture_output.get("has_dual_hands", False)
        is_dual_swimming = gesture_output.get("is_dual_hand_swimming", False)
        paddle_boost = gesture_output.get("paddle_boost", 1.0)
        second_cursor_pos = gesture_output.get("second_cursor_pos", None)
        second_gesture = gesture_output.get("second_gesture", GestureType.NONE)

        # Temporal Hand Motion Tracking (Velocities, Rhythm, Sync Level)
        now_ts = time.time()
        l_snap = None
        r_snap = None
        if hand_data.is_detected:
            h1_wx = hand_data.landmarks[0][0] * SCREEN_WIDTH if hand_data.landmarks else float(hand_data.screen_x)
            h1_wy = hand_data.landmarks[0][1] * SCREEN_HEIGHT if hand_data.landmarks else float(hand_data.screen_y)
            h1_data = (h1_wx, h1_wy, float(hand_data.screen_x), float(hand_data.screen_y), float(hand_data.confidence if hand_data.confidence > 0 else 0.95))
            if hand_data.has_second_hand:
                h2_wx = hand_data.second_landmarks[0][0] * SCREEN_WIDTH if hand_data.second_landmarks else float(hand_data.second_screen_x)
                h2_wy = hand_data.second_landmarks[0][1] * SCREEN_HEIGHT if hand_data.second_landmarks else float(hand_data.second_screen_y)
                h2_data = (h2_wx, h2_wy, float(hand_data.second_screen_x), float(hand_data.second_screen_y), 0.92)
                if hand_data.handedness == "Left":
                    l_snap, r_snap = h1_data, h2_data
                else:
                    r_snap, l_snap = h1_data, h2_data
            else:
                if hand_data.handedness == "Left":
                    l_snap = h1_data
                else:
                    r_snap = h1_data

        self.motion_tracker.record_frame(now_ts, l_snap, r_snap)
        self.last_motion_result = self.motion_tracker.update(dt)

        self.last_cursor_pos = (cursor_x, cursor_y)

        # 2. State-Specific Updates
        if self.current_state == GameState.MAIN_MENU:
            self.menu_screen.update(cursor_x, cursor_y, pinch_triggered, dt)

        elif self.current_state == GameState.LEVEL_SELECT:
            self.level_select_screen.update(cursor_x, cursor_y, pinch_triggered, dt, self.unlocked_levels, self.completed_levels)

        elif self.current_state == GameState.CHALLENGES:
            self.challenge_screen.update(cursor_x, cursor_y, pinch_triggered, dt)

        elif self.current_state == GameState.HOW_TO_PLAY:
            self.instructions_screen.update(cursor_x, cursor_y, pinch_triggered, dt)

        elif self.current_state == GameState.CAMERA_CHECK:
            self.camera_check_screen.update(cursor_x, cursor_y, pinch_triggered, dt)

        elif self.current_state == GameState.MUSEUM:
            self.museum_screen.update(cursor_x, cursor_y, pinch_triggered, dt)

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
                shield_active,
                is_dual_swimming=is_dual_swimming,
                paddle_boost=paddle_boost,
                second_target_x=second_cursor_pos[0] if second_cursor_pos else None,
                second_target_y=second_cursor_pos[1] if second_cursor_pos else None,
                is_mega_palm=is_mega_palm,
                is_pinching_active=is_pinching_active,
                has_dual_hands=has_dual_hands,
                second_gesture=second_gesture,
            )

        # 3. Update Swimmer Kinematics, Cursor & Particles
        is_pinching = is_pinching_active or pinch_triggered
        current_force = 260.0 if (self.player.current_active_timer > 0 and is_mega_palm) else (180.0 if self.player.current_active_timer > 0 else 0.0)
        emit_regulator_bubble = self.player.update(
            dt,
            cursor_x,
            cursor_y,
            is_pinching,
            shield_active,
            current_force,
            is_dual_hand_swimming=is_dual_swimming,
            paddle_boost=paddle_boost
        )
        
        # Scuba regulator bubble trail
        if emit_regulator_bubble:
            self.particles.emit_cursor_trail(self.player.x, self.player.y - 10)

        self.particles.update(dt, current_active=(self.player.current_active_timer > 0))

        # Update Custom Vision Hand Cursor
        is_hover_t = False
        is_hover_d = False
        if self.current_level and self.current_state == GameState.PLAYING:
            is_hover_t = (
                self.current_level.treasure_manager.get_hovered_treasure(cursor_x, cursor_y) is not None
                or self.current_level.treasure_manager.get_hovered_crate(cursor_x, cursor_y) is not None
                or (second_cursor_pos is not None and self.current_level.treasure_manager.get_hovered_treasure(second_cursor_pos[0], second_cursor_pos[1]) is not None)
            )
            is_hover_d = (
                self.player.is_hovering_danger
                or (self.current_level.marine_manager.current_shark is not None and self.current_level.marine_manager.current_shark.check_cursor_collision(cursor_x, cursor_y))
            )
        self.hand_cursor.update(
            raw_x=cursor_x,
            raw_y=cursor_y,
            is_detected=self.is_hand_detected,
            current_gesture=current_gesture,
            is_hovering_treasure=is_hover_t,
            is_hovering_danger=is_hover_d,
            sonar_active=(current_gesture == GestureType.TWO_FINGERS or sonar_triggered),
            dt=dt,
            has_dual_hands=has_dual_hands,
            second_x=second_cursor_pos[0] if second_cursor_pos else None,
            second_y=second_cursor_pos[1] if second_cursor_pos else None,
            second_gesture=second_gesture,
            is_dual_swimming=is_dual_swimming,
            paddle_boost=paddle_boost,
        )

    def _update_gameplay(
        self,
        dt: float,
        target_x: int,
        target_y: int,
        pinch_triggered: bool,
        palm_triggered: bool,
        sonar_triggered: bool,
        shield_active: bool,
        is_dual_swimming: bool = False,
        paddle_boost: float = 1.0,
        second_target_x: Optional[int] = None,
        second_target_y: Optional[int] = None,
        is_mega_palm: bool = False,
        is_pinching_active: bool = False,
        has_dual_hands: bool = False,
        second_gesture: GestureType = GestureType.NONE,
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
                self.mission_manager.record_event("SONAR_PULSE")

        # Water Current Trigger
        if palm_triggered:
            if self.player.activate_water_current():
                self.sound_manager.play('current')
                if is_mega_palm:
                    self.particles.emit_water_current()
                    self.particles.emit_water_current()
                    self.particles.emit_score_popup(self.player.x, self.player.y - 40, "🌊 MEGA TIDAL CURRENT!", COLOR_OCEAN_CYAN)
                else:
                    self.particles.emit_water_current()

        # Update Level Environment, Fish, Hazards, Timers
        lvl_complete, time_expired, shark_hit, shark_deflected, jelly_hit, jelly_deflected = self.current_level.update(
            dt,
            current_active,
            swimmer_pos,
            shield_active
        )

        # Shark Interaction Handling
        if shark_deflected:
            self.sound_manager.play('bubble')
            self.particles.emit_treasure_burst(self.player.x, self.player.y, count=10, color=COLOR_NEON_TEAL)
            self.mission_manager.record_event("SHARK_ESCAPE")
            if self.active_challenge_id == 1:
                self.player.add_score(150)
                self.particles.emit_score_popup(self.player.x, self.player.y - 30, "+150 SHARK DEFLECTION! 🦈", COLOR_GOLD)
        elif shark_hit:
            self.sound_manager.play('trap')
            self.combo_count = 0
            self.combo_multiplier = 1.0
            self.particles.emit_trap_explosion(self.player.x, self.player.y)
            still_alive = self.player.lose_life()
            if not still_alive:
                self.sound_manager.play('game_over')
                self.game_over_reason = "Out of Lives (Shark Attack!)"
                self.set_state(GameState.GAME_OVER)
                return
            self.particles.emit_score_popup(self.player.x, self.player.y - 30, f"💔 1 LIFE LOST! ({self.player.lives} REMAINING)", COLOR_CORAL_RED)

        # Electric Jellyfish Interaction Handling
        if jelly_deflected:
            self.sound_manager.play('bubble')
            self.particles.emit_treasure_burst(self.player.x, self.player.y, count=12, color=(210, 120, 255))
            self.particles.emit_score_popup(self.player.x, self.player.y - 20, "JELLY DEFLECTED! ⚡", (220, 160, 255))
            self.player.add_score(75)
            self.mission_manager.record_event("DEFLECT_JELLYFISH")
        elif jelly_hit:
            self.sound_manager.play('jellyfish_zap')
            self.combo_count = 0
            self.combo_multiplier = 1.0
            self.player.reduce_oxygen(15.0, shake_duration=0.45, shake_power=10.0)
            self.particles.emit_score_popup(self.player.x, self.player.y, "-15% OXYGEN [ELECTRIC SHOCK!]", (220, 100, 255))

        # Check Air Bubble Stations
        air_restored = self.current_level.treasure_manager.check_air_stations(self.player.x, self.player.y)
        if air_restored > 0:
            self.player.oxygen = min(100.0, self.player.oxygen + air_restored)
            self.sound_manager.play('bubble')
            self.particles.emit_score_popup(self.player.x, self.player.y - 35, "+25% OXYGEN! 🫧", COLOR_EMERALD)

        # Check Mystery Crates (Opened via pinch)
        hovered_crate = (
            self.current_level.treasure_manager.get_hovered_crate(target_x, target_y)
            or self.current_level.treasure_manager.get_hovered_crate(self.player.x, self.player.y)
        )
        if pinch_triggered and hovered_crate and not hovered_crate.is_opened:
            rtype, rscore, rox, rsonar = hovered_crate.open_crate()
            self.mission_manager.record_event("OPEN_CRATE")
            if rscore > 0:
                self.player.add_score(rscore)
            if rox > 0:
                self.player.oxygen = min(100.0, self.player.oxygen + rox)
            elif rox < 0:
                self.player.reduce_oxygen(abs(rox), shake_duration=0.4, shake_power=8.0)
                self.combo_count = 0
                self.combo_multiplier = 1.0
                self.sound_manager.play('trap')
            if rsonar > 0:
                self.player.sonar_charges += rsonar

            if rtype != "TRAP":
                self.sound_manager.play('treasure')
                self.particles.emit_treasure_burst(hovered_crate.x, hovered_crate.y, count=22, color=COLOR_GOLD)
                self.particles.emit_score_popup(hovered_crate.x, hovered_crate.y - 30, f"CRATE: {rtype}! 📦 +{rscore}", COLOR_GOLD)
            else:
                self.particles.emit_trap_explosion(hovered_crate.x, hovered_crate.y)
                self.particles.emit_score_popup(hovered_crate.x, hovered_crate.y - 30, "CRATE TRAP! 💥", COLOR_CORAL_RED)

        # Check Whirlpools
        if self.current_level_id >= 2 and len(self.current_level.marine_manager.active_whirlpools) == 0:
            self.whirlpool_timer += dt
            if self.whirlpool_timer >= 22.0:
                self.whirlpool_timer = 0.0
                self.current_level.marine_manager.trigger_whirlpool()
                self.sound_manager.play('current')

        w_fx, w_fy, w_dmg, w_esc = self.current_level.marine_manager.apply_whirlpools(self.player.x, self.player.y)
        if w_fx != 0 or w_fy != 0:
            self.player.x += w_fx * dt
            self.player.y += w_fy * dt

        if w_dmg:
            self.player.reduce_oxygen(15.0, shake_duration=0.5, shake_power=12.0)
            self.combo_count = 0
            self.combo_multiplier = 1.0
            self.sound_manager.play('whirlpool')
            self.particles.emit_score_popup(self.player.x, self.player.y, "-15% OXYGEN [WHIRLPOOL!]", COLOR_CORAL_RED)

        if w_esc:
            self.player.add_score(50)
            self.sound_manager.play('bubble')
            self.particles.emit_score_popup(self.player.x, self.player.y - 25, "ESCAPED WHIRLPOOL! 🌀 +50", COLOR_NEON_TEAL)

        # Check Octopus Ambush (Level 4)
        if self.current_level_id == 4 and not self.current_level.marine_manager.current_octopus:
            self.octopus_timer += dt
            if self.octopus_timer >= 24.0:
                self.octopus_timer = 0.0
                self.current_level.marine_manager.trigger_octopus_ambush()
                self.sound_manager.play('trap')
                self.particles.emit_score_popup(SCREEN_WIDTH // 2, 120, "OCTOPUS AMBUSH! 🐙 DODGE TENTACLES!", COLOR_CORAL_RED)

        if self.current_level.marine_manager.check_octopus_interaction(self.player.x, self.player.y):
            self.player.reduce_oxygen(12.0, shake_duration=0.4, shake_power=10.0)
            self.combo_count = 0
            self.combo_multiplier = 1.0
            self.sound_manager.play('trap')
            self.particles.emit_score_popup(self.player.x, self.player.y, "-12% OXYGEN [TENTACLE HIT!]", COLOR_CORAL_RED)

        # Check Ancient Gesture Puzzle (Level 5)
        if self.current_level.puzzle:
            solved, step_done = self.current_level.puzzle.check_gesture(self.gesture_detector.current_gesture, self.player.x, self.player.y)
            if step_done and not solved:
                self.sound_manager.play('bubble')
                self.particles.emit_treasure_burst(self.current_level.puzzle.x, self.current_level.puzzle.y, count=14, color=COLOR_NEON_TEAL)
            if solved:
                self.player.add_score(500)
                self.sound_manager.play('rare_treasure')
                self.particles.emit_treasure_burst(self.current_level.puzzle.x, self.current_level.puzzle.y, count=35, color=COLOR_GOLD)
                self.particles.emit_score_popup(self.current_level.puzzle.x, self.current_level.puzzle.y - 45, "ANCIENT VAULT UNLOCKED! 🏆 +500", COLOR_GOLD)

        # Extra challenge passive oxygen drain (e.g. Abyssal Blitz 2.2x drain)
        if self.active_challenge_id is not None:
            c_cfg = CHALLENGES[self.active_challenge_id]
            if c_cfg.oxygen_drain_mult > 1.0:
                extra_drain = PASSIVE_OXYGEN_DEPLETION_RATE * (c_cfg.oxygen_drain_mult - 1.0) * dt
                self.player.oxygen = max(0.0, self.player.oxygen - extra_drain)

        # Hovered Object Detection (Near Swimmer, Hand 1, or Hand 2 Aim Target)
        hovered_item = (
            self.current_level.treasure_manager.get_hovered_treasure(self.player.x, self.player.y)
            or self.current_level.treasure_manager.get_hovered_treasure(target_x, target_y)
            or (self.current_level.treasure_manager.get_hovered_treasure(second_target_x, second_target_y) if second_target_x is not None else None)
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
        # TACTILE GRAB, CARRY & DEPOSIT INTO SEAFLOOR VAULT
        # ============================================================
        chest = self.current_level.treasure_manager.chest
        in_chest_zone = chest.is_in_deposit_zone(self.player.x, self.player.y)

        # CASE A: Player is currently carrying a treasure
        if self.player.carried_treasure is not None:
            # Check heavy treasure instability (Section 9)
            if self.player.carried_treasure.type == TreasureType.HEAVY and second_target_x is not None and second_target_y is not None:
                hand_dist = math.hypot(target_x - second_target_x, target_y - second_target_y)
                if hand_dist > 440.0 or hand_dist < 60.0:
                    dropped_item = self.player.release_carried_treasure()
                    dropped_item.drop(self.player.x, self.player.y)
                    self.sound_manager.play('heavy_drop')
                    self.particles.emit_score_popup(self.player.x, self.player.y - 35, "⚠️ HANDS UNSTABLE! CHEST DROPPED!", COLOR_CORAL_RED)

            # Reached the treasure chest depot -> Deposit safely into vault!
            if self.player.carried_treasure is not None and in_chest_zone:
                deposited_item = self.player.release_carried_treasure()
                deposited_item.collected = True
                self.current_level.deposited_count += 1
                self.inventory.add_treasure(deposited_item)

                unlocked_artifact = self.museum.register_treasure_deposit(deposited_item)
                if unlocked_artifact:
                    self.sound_manager.play('puzzle_success')
                    self.particles.emit_score_popup(self.player.x, self.player.y - 50, f"MUSEUM UNLOCKED: {unlocked_artifact.name}! 🏛️", COLOR_GOLD)

                if deposited_item.type == TreasureType.HEAVY:
                    self.mission_manager.record_event("HEAVY_DEPOSIT")
                else:
                    self.mission_manager.record_event("DEPOSIT")

                # Dynamic combo streak multiplier!
                self.combo_count += 1
                self.combo_multiplier = min(3.0, 1.0 + (self.combo_count - 1) * 0.5)
                earned_score = int(deposited_item.score_value * self.combo_multiplier)
                self.player.add_score(earned_score)

                # Challenge 2 (Abyssal Blitz) relic oxygen recharge
                if self.active_challenge_id == 2:
                    self.player.oxygen = min(100.0, self.player.oxygen + 20.0)
                    self.particles.emit_score_popup(self.player.x, self.player.y - 45, "+20% OXYGEN RECHARGE! 🔋", COLOR_EMERALD)

                if deposited_item.type in (TreasureType.RARE, TreasureType.ANCIENT, TreasureType.HEAVY):
                    self.sound_manager.play('rare_treasure')
                else:
                    self.sound_manager.play('treasure')

                # Celebration visual burst at chest vault
                self.particles.emit_treasure_burst(chest.x, chest.y - 12, count=24, color=deposited_item.base_color)
                combo_str = f" [x{self.combo_multiplier:.1f} COMBO! 🔥]" if self.combo_multiplier > 1.0 else ""
                self.particles.emit_score_popup(chest.x, chest.y - 30, f"+{earned_score} DEPOSITED! 🎁{combo_str}", COLOR_GOLD)

        # CASE B: Player is NOT currently carrying a treasure
        else:
            if (pinch_triggered or direct_touch or dwell_collect) and hovered_item and not hovered_item.collected:
                if hovered_item.type == TreasureType.TRAP:
                    # Sea Mine Trap Detonates Immediately!
                    hovered_item.collected = True
                    self.combo_count = 0
                    self.combo_multiplier = 1.0
                    self.sound_manager.play('trap')
                    self.particles.emit_trap_explosion(hovered_item.x, hovered_item.y)
                    still_alive = self.player.lose_life()
                    if not still_alive:
                        self.sound_manager.play('game_over')
                        self.game_over_reason = "Out of Lives (Sea Mine Explosion!)"
                        self.set_state(GameState.GAME_OVER)
                        return
                    self.particles.emit_score_popup(hovered_item.x, hovered_item.y, f"💔 MINE DETONATION! ({self.player.lives} LIVES)", COLOR_CORAL_RED)

                elif hovered_item.type == TreasureType.FAKE:
                    # Deceptive Counterfeit Penalty!
                    hovered_item.collected = True
                    self.combo_count = 0
                    self.combo_multiplier = 1.0
                    self.sound_manager.play('fake_warning')
                    self.player.add_score(hovered_item.score_value)
                    self.player.reduce_oxygen(hovered_item.oxygen_penalty, shake_duration=0.4, shake_power=8.0)
                    self.particles.emit_score_popup(hovered_item.x, hovered_item.y, f"{hovered_item.score_value} FAKE PENALTY!", COLOR_AMBER_WARNING)

                elif hovered_item.type == TreasureType.HEAVY:
                    # Heavy Relic: Requires Both Hands to Lift (Section 9)
                    can_lift = has_dual_hands and (is_pinching_active or pinch_triggered) and (second_gesture in (GestureType.PINCH, GestureType.FIST) or pinch_triggered)
                    if not can_lift:
                        self.sound_manager.play('fake_warning')
                        self.particles.emit_score_popup(hovered_item.x, hovered_item.y - 35, "HEAVY TREASURE! USE BOTH HANDS 👐", COLOR_GOLD)
                    else:
                        self.player.grab_treasure(hovered_item)
                        self.sound_manager.play('treasure')
                        self.particles.emit_score_popup(self.player.x, self.player.y - 20, "HEAVY RELIC LIFTED! 👐 SWIM TO CHEST", COLOR_GOLD)

                else:
                    # Genuine Relic: Grab and Carry!
                    if in_chest_zone:
                        hovered_item.collected = True
                        self.current_level.deposited_count += 1
                        self.inventory.add_treasure(hovered_item)
                        unlocked_artifact = self.museum.register_treasure_deposit(hovered_item)
                        if unlocked_artifact:
                            self.sound_manager.play('puzzle_success')
                            self.particles.emit_score_popup(self.player.x, self.player.y - 50, f"MUSEUM UNLOCKED: {unlocked_artifact.name}! 🏛️", COLOR_GOLD)
                        self.mission_manager.record_event("DEPOSIT")

                        self.combo_count += 1
                        self.combo_multiplier = min(3.0, 1.0 + (self.combo_count - 1) * 0.5)
                        earned_score = int(hovered_item.score_value * self.combo_multiplier)
                        self.player.add_score(earned_score)
                        self.sound_manager.play('treasure')
                        self.particles.emit_treasure_burst(chest.x, chest.y - 12, count=24, color=hovered_item.base_color)
                        combo_str = f" [x{self.combo_multiplier:.1f} COMBO! 🔥]" if self.combo_multiplier > 1.0 else ""
                        self.particles.emit_score_popup(chest.x, chest.y - 30, f"+{earned_score} DEPOSITED! 🎁{combo_str}", COLOR_GOLD)
                    else:
                        self.player.grab_treasure(hovered_item)
                        self.sound_manager.play('treasure')
                        self.particles.emit_score_popup(self.player.x, self.player.y - 20, "GRABBED! 🤏 SWIM TO CHEST", COLOR_GOLD)

        # Update Mission Manager, Dynamic Ocean Events, and Smart Tutorial
        self.mission_manager.update_time(dt)
        self.ocean_events.update(dt, swimmer_pos=(self.player.x, self.player.y), is_dual_swimming=is_dual_swimming)

        if self.tutorial.active:
            self.tutorial.update(
                dt,
                is_hand_detected=self.is_hand_detected,
                is_moving=(abs(self.player.vx) > 30.0 or abs(self.player.vy) > 30.0),
                motion_result=self.last_motion_result,
                is_pinching=is_pinching_active or pinch_triggered,
                is_carrying=(self.player.carried_treasure is not None),
                deposited_count=self.current_level.deposited_count,
                sonar_used=sonar_triggered
            )

        # Check Level Completion (Objective Reached)
        if lvl_complete:
            self.completed_levels.add(self.current_level_id)
            self.unlocked_levels = max(self.unlocked_levels, self.current_level_id + 1)
            self.sound_manager.play('level_complete')
            stars, side_done = self.mission_manager.calculate_stars(
                remaining_oxygen=self.player.oxygen,
                time_remaining=self.current_level.time_remaining,
                lives=self.player.lives
            )
            self.last_stars = stars
            self.last_side_missions_done = side_done
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

        elif self.current_state == GameState.CHALLENGES:
            self.challenge_screen.draw(scene_surf)

        elif self.current_state == GameState.HOW_TO_PLAY:
            self.instructions_screen.draw(scene_surf)

        elif self.current_state == GameState.CAMERA_CHECK:
            hand_data = self.hand_detector.get_latest_data()
            annotated_frame = None
            if hand_data.raw_frame is not None:
                lms_to_draw = []
                if hand_data.landmarks:
                    lms_to_draw.append(hand_data.landmarks)
                if hand_data.has_second_hand and hand_data.second_landmarks:
                    lms_to_draw.append(hand_data.second_landmarks)
                annotated_frame = self.hand_detector.render_debug_overlay(hand_data.raw_frame, lms_to_draw)
            
            self.camera_check_screen.draw(
                scene_surf,
                raw_frame=annotated_frame,
                camera_available=self.hand_detector.is_camera_available,
                hand_detected=hand_data.is_detected,
                current_gesture=self.gesture_detector.current_gesture,
                pinch_dist=self.gesture_detector.pinch_distance,
                camera_fps=self.hand_detector.actual_fps,
                num_hands=hand_data.num_hands,
                second_gesture=self.gesture_detector.second_current_gesture if hand_data.has_second_hand else None,
            )

        elif self.current_state == GameState.MUSEUM:
            self.museum_screen.draw(scene_surf, self.museum)

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
                
                # Dynamic Ancient Entities / Guardian / Seals (Level 5)
                self.ocean_events.draw(scene_surf)

                # Active Underwater Swimmer Explorer
                self.player.draw_swimmer(scene_surf)

                # Depth Fog with Flashlight Illumination around Diver
                self.current_level.draw_fog(
                    scene_surf,
                    player_pos=(self.player.x, self.player.y),
                    sonar_active=(self.gesture_detector.current_gesture == GestureType.TWO_FINGERS)
                )

                # Foreground Visual Effects & Streams
                self.particles.draw_foreground(scene_surf)

                # Smart Progressive Tutorial Overlay (Level 1)
                if self.tutorial.active:
                    self.tutorial.draw(scene_surf)

                # Subtle Treasure Compass Target
                compass_target = None
                if self.player.carried_treasure is not None:
                    compass_target = (self.current_level.treasure_manager.chest.x, self.current_level.treasure_manager.chest.y, "DEPOSIT VAULT")
                else:
                    nearest_t = None
                    min_d = float('inf')
                    for t in self.current_level.treasure_manager.treasures:
                        if not t.collected and t.type not in (TreasureType.TRAP, TreasureType.FAKE):
                            d = math.hypot(t.x - self.player.x, t.y - self.player.y)
                            if d < min_d:
                                min_d = d
                                nearest_t = t
                    if nearest_t:
                        compass_target = (nearest_t.x, nearest_t.y, nearest_t.type.value)

                # In-Game HUD with Objective Progress, Minimap, Lives, Sync Meter & Compass
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
                    carried_treasure_type=carried_name,
                    combo_multiplier=self.combo_multiplier,
                    is_challenge=(self.active_challenge_id is not None),
                    player_pos=(self.player.x, self.player.y),
                    chest_pos=(self.current_level.treasure_manager.chest.x, self.current_level.treasure_manager.chest.y),
                    exploration_ratio=self.current_level.get_exploration_ratio(),
                    explored_grid=self.current_level.explored_grid,
                    lives=self.player.lives,
                    sync_level=self.last_motion_result.sync_level if self.last_motion_result else 0.85,
                    is_combo_swim=self.last_motion_result.is_combo_swim if self.last_motion_result else False,
                    left_confidence=self.last_motion_result.left_confidence if self.last_motion_result else 0.95,
                    right_confidence=self.last_motion_result.right_confidence if self.last_motion_result else 0.92,
                    compass_target=compass_target,
                    ocean_condition=self.ocean_events.get_current_condition().name
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
                    remaining_oxygen=self.player.oxygen,
                    best_combo=self.combo_multiplier,
                    side_missions_done=self.last_side_missions_done,
                    total_side_missions=len(self.mission_manager.active_side_missions) if self.mission_manager.active_side_missions else 3,
                    stars=self.last_stars
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

        # 2. Render Custom Glowing Vision Hand Cursor (ALWAYS visible)
        self.hand_cursor.draw(scene_surf)

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
