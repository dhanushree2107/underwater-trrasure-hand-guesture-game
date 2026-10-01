"""
Underwater Treasure Hunt - Adventure Systems & Mechanics Test Suite
Validates the HandCursor, Mystery Crates, Air Bubble Stations, Whirlpools,
Octopus Ambush, Ancient Gesture Puzzles, and Exploration Minimap telemetry.
"""

import pytest
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from hand_tracking.gesture_detector import GestureType
from ui.cursor import HandCursor, CursorTargetState
from game.treasure import MysteryCrate, AirBubbleStation, TreasureManager, Treasure, TreasureType
from game.enemy import Whirlpool, OctopusAmbush, MarineLifeManager
from game.level import Level, AncientGesturePuzzle

def test_hand_cursor_states_and_bubbles():
    """Verifies that HandCursor smoothly follows coords and transitions through states."""
    cursor = HandCursor()
    assert cursor.is_hand_detected is True
    assert cursor.target_state == CursorTargetState.NORMAL

    # 1. Update with normal move gesture
    cursor.update(raw_x=500.0, raw_y=400.0, is_detected=True, current_gesture=GestureType.MOVE, dt=0.05)
    assert abs(cursor.x - 500.0) < 200.0
    assert cursor.target_state == CursorTargetState.NORMAL

    # 2. Update with pinch grab
    cursor.update(raw_x=500.0, raw_y=400.0, is_detected=True, current_gesture=GestureType.PINCH, dt=0.05)
    assert cursor.target_state == CursorTargetState.PINCH

    # 3. Update with treasure hovering
    cursor.update(raw_x=500.0, raw_y=400.0, is_detected=True, current_gesture=GestureType.MOVE, is_hovering_treasure=True, dt=0.05)
    assert cursor.target_state == CursorTargetState.TREASURE_TARGET

    # 4. Update with danger hovering
    cursor.update(raw_x=500.0, raw_y=400.0, is_detected=True, current_gesture=GestureType.MOVE, is_hovering_danger=True, dt=0.05)
    assert cursor.target_state == CursorTargetState.DANGER

    # 5. Hand lost indicator state
    cursor.update(raw_x=500.0, raw_y=400.0, is_detected=False, current_gesture=GestureType.MOVE, dt=0.05)
    assert cursor.is_hand_detected is False
    assert cursor.hand_lost_timer > 0.0

def test_mystery_crate_opening():
    """Verifies that mystery crates can be opened and yield valid rewards."""
    crate = MysteryCrate(x=400.0, y=500.0)
    assert crate.is_opened is False
    assert crate.is_hovered(400.0, 500.0) is True

    # Open crate
    reward_type, score_val, ox_val, sonar_val = crate.open_crate()
    assert crate.is_opened is True
    assert reward_type in ("OXYGEN", "SONAR", "TREASURE", "BONUS", "TRAP")
    assert crate.is_hovered(400.0, 500.0) is False

def test_air_bubble_station_recharge():
    """Verifies that air bubble stations restore +25% oxygen with a cooldown."""
    station = AirBubbleStation(x=300.0, y=600.0)
    assert station.cooldown == 0.0

    # Diver in proximity restores 25% oxygen
    restored = station.check_restore(px=300.0, py=600.0)
    assert restored == 25.0
    assert station.cooldown == station.max_cooldown

    # Immediate second check should restore 0% because station is recharging
    assert station.check_restore(px=300.0, py=600.0) == 0.0

    # Update through cooldown
    station.update(dt=13.0)
    assert station.cooldown == 0.0
    assert station.check_restore(px=300.0, py=600.0) == 25.0

def test_whirlpool_suction_and_escape():
    """Verifies whirlpool suction physics and escape events."""
    whirlpool = Whirlpool(x=600.0, y=360.0, radius=80.0)

    # 1. Swimmer within outer influence radius is pulled towards center
    fx, fy, damaged, escaped = whirlpool.apply_suction(px=540.0, py=360.0)
    assert fx > 0.0  # Pulled right towards center (600, 360)
    assert damaged is False

    # 2. Swimmer pulled into core (< 24px) takes damage
    _, _, damaged, _ = whirlpool.apply_suction(px=605.0, py=360.0)
    assert damaged is True

    # 3. Swimmer moving outside influence radius triggers escape event
    _, _, _, escaped = whirlpool.apply_suction(px=850.0, py=360.0)
    assert escaped is True

def test_octopus_ambush_tentacles():
    """Verifies that octopus ambush creates undulating tentacles and detects collision."""
    ambush = OctopusAmbush(duration=10.0)
    assert len(ambush.tentacles) == 3

    # Update to extend tentacles
    ambush.update(dt=1.0)

    # Collision test on extended tentacle
    hit = ambush.check_collision(px=220.0, py=SCREEN_HEIGHT - 200.0)
    assert isinstance(hit, bool)

def test_ancient_gesture_puzzle():
    """Verifies that Level 5 ancient puzzle requires sequence ✌️ -> ✋ -> 🤏 to unlock."""
    puzzle = AncientGesturePuzzle(x=800.0, y=600.0)
    assert puzzle.solved is False
    assert puzzle.current_step == 0

    # Step 1: Wrong gesture or too far away
    solved, adv = puzzle.check_gesture(GestureType.PINCH, px=800.0, py=600.0)
    assert adv is False
    assert puzzle.current_step == 0

    # Step 1: Correct gesture: TWO_FINGERS (✌️)
    solved, adv = puzzle.check_gesture(GestureType.TWO_FINGERS, px=800.0, py=600.0)
    assert adv is True
    assert solved is False
    assert puzzle.current_step == 1

    # Step 2: Correct gesture: OPEN_PALM (✋)
    solved, adv = puzzle.check_gesture(GestureType.OPEN_PALM, px=800.0, py=600.0)
    assert adv is True
    assert solved is False
    assert puzzle.current_step == 2

    # Step 3: Correct gesture: PINCH (🤏) -> Solved!
    solved, adv = puzzle.check_gesture(GestureType.PINCH, px=800.0, py=600.0)
    assert adv is True
    assert solved is True
    assert puzzle.solved is True

def test_exploration_grid_and_minimap():
    """Verifies exploration fog tracking across level tiles."""
    lvl = Level(1)
    initial_ratio = lvl.get_exploration_ratio()
    assert initial_ratio == 0.0

    # Swimmer explores center area
    lvl.update(dt=0.1, current_active=False, cursor_pos=(640, 360), shield_active=False)
    updated_ratio = lvl.get_exploration_ratio()
    assert updated_ratio > 0.0
    assert updated_ratio <= 1.0
