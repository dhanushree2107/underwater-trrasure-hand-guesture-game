"""
Comprehensive integration and unit test suite verifying the complete
Underwater Treasure Hunt systems:
- Two-Hand Motion Tracker (directions, stroke rhythm, sync level 0-100%)
- Swim Physics Engine (fluid kinematics, propulsion, deceleration)
- 3-Life Survival & Invulnerability System
- Two-Hand Heavy Treasure Lifting & Distance Instability
- Underwater Museum & Lore Exhibit Unlocks
- Level Missions & 1-3 Star Ratings
- Dynamic Ocean Events, Ancient Seal, and Ancient Guardian
"""

import time
import math
import pytest
from hand_tracking.hand_motion import (
    HandMotionTracker,
    SwimTrackingStatus,
    DualSwimMotionResult,
)
from game.swimming import SwimPhysicsEngine
from game.player import Player
from game.treasure import Treasure, TreasureType
from game.inventory import DiverInventory, UnderwaterMuseum
from game.missions import MissionManager
from game.events import (
    OceanEventManager,
    OceanCondition,
    AncientGesturePuzzle,
    TwoHandAncientSeal,
    AncientGuardian,
)
from ui.tutorial import SmartTutorial


# ============================================================
# 1. TWO-HAND MOTION TRACKING & SWIMMING KINEMATICS
# ============================================================

def test_motion_tracker_directional_detection():
    tracker = HandMotionTracker(history_len=10)
    base_t = time.time()

    # Simulate both hands moving LEFT over 5 frames
    for i in range(5):
        t = base_t + i * 0.03
        x = 600.0 - i * 60.0 # moving left by 60px per 30ms
        y = 350.0
        tracker.record_frame(t, (x - 80.0, y, x - 80.0, y, 0.95), (x + 80.0, y, x + 80.0, y, 0.95))

    res = tracker.update(0.03)
    assert res.status == SwimTrackingStatus.TWO_HANDS
    assert res.combined_vector[0] < -50.0  # Strongly moving left
    assert res.direction_label.startswith("SWIM LEFT")
    assert res.sync_level > 0.70

    # Reset and simulate both hands moving RIGHT
    tracker.reset()
    base_t = time.time()
    for i in range(5):
        t = base_t + i * 0.03
        x = 400.0 + i * 60.0 # moving right
        y = 350.0
        tracker.record_frame(t, (x - 80.0, y, x - 80.0, y, 0.95), (x + 80.0, y, x + 80.0, y, 0.95))

    res = tracker.update(0.03)
    assert res.combined_vector[0] > 50.0
    assert res.direction_label.startswith("SWIM RIGHT")


def test_motion_tracker_vertical_swimming():
    tracker = HandMotionTracker(history_len=10)
    base_t = time.time()

    # Both hands moving UP
    for i in range(5):
        t = base_t + i * 0.03
        y = 500.0 - i * 50.0
        tracker.record_frame(t, (300.0, y, 300.0, y, 0.95), (600.0, y, 600.0, y, 0.95))

    res = tracker.update(0.03)
    assert res.combined_vector[1] < -40.0
    assert res.direction_label.startswith("SWIM UP")

    # Both hands moving DOWN
    tracker.reset()
    base_t = time.time()
    for i in range(5):
        t = base_t + i * 0.03
        y = 200.0 + i * 50.0
        tracker.record_frame(t, (300.0, y, 300.0, y, 0.95), (600.0, y, 600.0, y, 0.95))

    res = tracker.update(0.03)
    assert res.combined_vector[1] > 40.0
    assert res.direction_label.startswith("SWIM DOWN")


def test_motion_tracker_single_hand_and_absent_fallback():
    tracker = HandMotionTracker(history_len=10)
    now = time.time()

    # Only Left hand detected
    tracker.record_frame(now, (400.0, 300.0, 400.0, 300.0, 0.92), None)
    res = tracker.update(0.03)
    assert res.status in (SwimTrackingStatus.ONE_HAND, SwimTrackingStatus.NO_HANDS)

    # No hands detected
    tracker.reset()
    res = tracker.update(0.03)
    assert res.status == SwimTrackingStatus.NO_HANDS
    assert res.status_message.startswith("HANDS NOT DETECTED")


# ============================================================
# 2. SWIM PHYSICS ENGINE
# ============================================================

def test_swim_physics_fluid_glide_and_drag():
    engine = SwimPhysicsEngine()
    engine.vx = 400.0
    engine.vy = 200.0

    # Empty motion result (no hands)
    empty_res = DualSwimMotionResult(
        status=SwimTrackingStatus.NO_HANDS,
        status_message="NO HANDS",
        left_velocity=(0.0, 0.0),
        right_velocity=(0.0, 0.0),
        combined_vector=(0.0, 0.0),
        motion_intensity=0.0,
        sync_level=0.0,
        is_synchronized=False,
        is_combo_swim=False,
        combo_mult=1.0,
        turning_torque=0.0,
        left_confidence=0.0,
        right_confidence=0.0,
        direction_label="IDLE",
    )

    # Apply 10 frames of hydrodynamic drag
    x, y = 500.0, 350.0
    for _ in range(10):
        x, y, vx, vy, is_moving = engine.apply_motion(
            0.016, x, y, empty_res, target_midpoint=(x, y)
        )

    # Velocities should decay smoothly under fluid drag
    assert engine.vx < 400.0
    assert engine.vy < 200.0
    assert is_moving is False


# ============================================================
# 3. THREE-LIFE SYSTEM
# ============================================================

def test_three_life_system_damage_and_invulnerability():
    player = Player()
    assert player.lives == 3
    assert player.invulnerability_timer == 0.0

    # Collision 1
    alive = player.lose_life()
    assert alive is True
    assert player.lives == 2
    assert player.invulnerability_timer > 1.5

    # During invulnerability window, damage is ignored
    alive = player.lose_life()
    assert player.lives == 2  # still 2!

    # Expire invulnerability
    player.invulnerability_timer = 0.0

    # Collision 2
    alive = player.lose_life()
    assert alive is True
    assert player.lives == 1

    player.invulnerability_timer = 0.0

    # Collision 3 (Fatal)
    alive = player.lose_life()
    assert alive is False
    assert player.lives == 0


# ============================================================
# 4. TWO-HAND HEAVY TREASURE & INSTABILITY
# ============================================================

def test_heavy_treasure_properties_and_attributes():
    heavy = Treasure(400.0, 400.0, TreasureType.HEAVY)
    assert heavy.type == TreasureType.HEAVY
    assert heavy.is_heavy is True
    assert heavy.requires_both_hands is True
    assert heavy.score_value == 750
    assert heavy.instability == 0.0


# ============================================================
# 5. UNDERWATER MUSEUM & EXHIBITS
# ============================================================

def test_underwater_museum_collection():
    museum = UnderwaterMuseum()
    assert museum.get_total_count() == 8
    # Pearl is unlocked by default in Shallow Sea
    assert museum.exhibits["pearl"].is_unlocked is True
    assert museum.get_unlocked_count() >= 1

    # Deposit Gold Coin
    gold_treasure = Treasure(100.0, 100.0, TreasureType.GOLD)
    unlocked = museum.register_treasure_deposit(gold_treasure, level_id=2)
    assert unlocked is not None
    assert unlocked.exhibit_id == "gold_coin"
    assert museum.exhibits["gold_coin"].is_unlocked is True

    # Depositing again does not duplicate unlock
    unlocked_again = museum.register_treasure_deposit(gold_treasure, level_id=2)
    assert unlocked_again is None


# ============================================================
# 6. MISSIONS & 1-3 STAR EVALUATION
# ============================================================

def test_mission_system_progression_and_stars():
    mm = MissionManager()
    mm.start_level(level_id=1, required_deposits=3)

    assert mm.main_mission is not None
    assert len(mm.active_side_missions) == 3

    # Deposit 3 items
    for _ in range(3):
        mm.record_event("DEPOSIT")

    assert mm.main_mission.completed is True

    # Calculate performance stars with high oxygen
    stars, sides = mm.calculate_stars(
        final_score=600,
        final_oxygen=75.0,
        target_score=300,
        lives=3
    )
    assert stars == 3


# ============================================================
# 7. DYNAMIC OCEAN EVENTS, ANCIENT SEAL & GUARDIAN
# ============================================================

def test_ocean_conditions_and_ancient_mechanisms():
    oem = OceanEventManager()
    oem.start_level(level_id=1)
    assert oem.get_current_condition() == OceanCondition.CALM_WATER

    oem.start_level(level_id=5)
    assert oem.get_current_condition() == OceanCondition.TURBULENT_WATER
    assert oem.guardian is not None
    assert oem.guardian.is_pacified is False

    # Ancient seal pull-apart mechanic
    seal = TwoHandAncientSeal()
    assert seal.is_opened is False

    # Synchronized pull apart: hand 1 moves left, hand 2 moves right
    success = seal.check_pull_apart(
        hand1_pos=(540.0, 360.0),
        hand2_pos=(740.0, 360.0),
        h1_dx=-45.0,
        h2_dx=45.0
    )
    assert seal.is_opened is True

    # Ancient gesture sequence (✌️ -> ✋ -> 🤏)
    puzzle = AncientGesturePuzzle()
    s1, c1 = puzzle.input_gesture("TWO_FINGERS")
    assert s1 is True and c1 is False
    s2, c2 = puzzle.input_gesture("OPEN_PALM")
    assert s2 is True and c2 is False
    s3, c3 = puzzle.input_gesture("PINCH")
    assert s3 is True and c3 is True
    assert puzzle.is_solved is True
