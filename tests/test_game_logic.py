"""
Unit tests for core game logic: scoring, oxygen depletion, sonar charges, and player mechanics.
"""

from game.player import Player
from game.treasure import Treasure, TreasureType
from config import (
    INITIAL_OXYGEN,
    SCORE_COMMON,
    SCORE_GOLD,
    SCORE_RARE,
    SCORE_ANCIENT,
    SCORE_FAKE_PENALTY,
    FAKE_TREASURE_OXYGEN_PENALTY,
    TRAP_OXYGEN_PENALTY,
    SONAR_INITIAL_CHARGES,
)

def test_player_initialization():
    player = Player()
    assert player.oxygen == INITIAL_OXYGEN
    assert player.score == 0
    assert player.sonar_charges == SONAR_INITIAL_CHARGES
    assert player.shield_active is False

def test_scoring_system():
    player = Player()
    player.add_score(SCORE_COMMON)
    assert player.score == 50
    player.add_score(SCORE_GOLD)
    assert player.score == 150
    player.add_score(SCORE_RARE)
    assert player.score == 400
    player.add_score(SCORE_ANCIENT)
    assert player.score == 900
    
    # Fake treasure penalty
    player.add_score(SCORE_FAKE_PENALTY)
    assert player.score == 850

def test_oxygen_depletion():
    player = Player()
    # Passive drain
    player.update(dt=1.0, target_x=640, target_y=360, is_pinching=False, shield_active=False)
    assert player.oxygen < INITIAL_OXYGEN

    # Fake treasure penalty
    prev_ox = player.oxygen
    player.reduce_oxygen(FAKE_TREASURE_OXYGEN_PENALTY)
    assert abs(player.oxygen - (prev_ox - FAKE_TREASURE_OXYGEN_PENALTY)) < 0.01

    # Trap penalty
    prev_ox = player.oxygen
    player.reduce_oxygen(TRAP_OXYGEN_PENALTY)
    assert abs(player.oxygen - (prev_ox - TRAP_OXYGEN_PENALTY)) < 0.01

def test_sonar_charge_depletion():
    player = Player()
    assert player.sonar_charges == 3
    assert player.activate_sonar() is True
    assert player.sonar_charges == 2
    assert player.activate_sonar() is True
    assert player.sonar_charges == 1
    assert player.activate_sonar() is True
    assert player.sonar_charges == 0
    # Out of charges
    assert player.activate_sonar() is False
    assert player.sonar_charges == 0

def test_water_current_activation():
    player = Player()
    assert player.current_active_timer == 0.0
    assert player.activate_water_current() is True
    assert player.current_active_timer > 0.0
    # Second immediate activation rejected while current active
    assert player.activate_water_current() is False

def test_treasure_grab_and_release():
    player = Player()
    assert player.carried_treasure is None
    
    treasure = Treasure(x=200, y=300, treasure_type=TreasureType.GOLD)
    assert treasure.is_carried is False
    
    # Grab
    player.grab_treasure(treasure)
    assert player.carried_treasure is treasure
    assert treasure.is_carried is True
    
    # Release
    released = player.release_carried_treasure()
    assert released is treasure
    assert player.carried_treasure is None
    assert treasure.is_carried is False

def test_swimmer_kinematics():
    player = Player()
    start_x, start_y = player.x, player.y
    # Move target to the right
    player.update(dt=0.1, target_x=start_x + 200, target_y=start_y, is_pinching=False, shield_active=False)
    # Velocity should increase towards the right
    assert player.vx > 0
    assert player.x > start_x
    assert player.facing_right is True
