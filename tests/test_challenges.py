"""
Unit and integration tests for Abyssal Challenges, Electric Jellyfish hazards,
and Combo Multiplier streaks.
"""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pytest
from config import CHALLENGES, ChallengeConfig, COLOR_CORAL_RED, COLOR_GOLD, COLOR_PURPLE_MYSTIC
from game.enemy import Jellyfish, MarineLifeManager
from game.game_manager import GameManager, GameState
from game.treasure import Treasure, TreasureType

def test_challenge_configs_validity():
    """Validates parameters for all 3 expedition challenges."""
    assert len(CHALLENGES) == 3
    
    # Challenge 1: Apex Predator Gauntlet
    c1 = CHALLENGES[1]
    assert c1.challenge_id == 1
    assert "PREDATOR" in c1.title
    assert c1.required_deposits == 4
    assert c1.shark_interval == 10.0
    assert c1.level_config.shark_enabled is True

    # Challenge 2: Abyssal Blitz Rush
    c2 = CHALLENGES[2]
    assert c2.challenge_id == 2
    assert "BLITZ" in c2.title
    assert c2.oxygen_drain_mult > 1.5
    assert c2.relic_oxygen_restore >= 15.0

    # Challenge 3: Electric Jellyfish Abyss
    c3 = CHALLENGES[3]
    assert c3.challenge_id == 3
    assert "JELLYFISH" in c3.title
    assert c3.jellyfish_count == 6

def test_jellyfish_hazard_mechanics():
    """Tests jellyfish drifting and shield deflection collision resolution."""
    jelly = Jellyfish(x=400.0, y=300.0)
    assert jelly.check_collision(400.0, 300.0) is True
    assert jelly.check_collision(800.0, 800.0) is False

    # Movement update
    init_y = jelly.y
    jelly.update(0.1, current_active=False)
    assert jelly.y != init_y

    # Test MarineLifeManager interaction without shield -> takes damage
    mgr = MarineLifeManager(fish_count=2)
    mgr.jellyfish = [Jellyfish(x=200.0, y=200.0)]
    hit, deflected = mgr.check_jellyfish_interaction(200.0, 200.0, shield_active=False)
    assert hit is True
    assert deflected is False

    # Test interaction with Shield active -> safely deflects!
    mgr.jellyfish = [Jellyfish(x=500.0, y=500.0)]
    hit, deflected = mgr.check_jellyfish_interaction(500.0, 500.0, shield_active=True)
    assert hit is False
    assert deflected is True

def test_start_challenge_expeditions():
    """Tests that GameManager starts challenges with customized hazards and timers."""
    gm = GameManager()
    
    # 1. Start Challenge 1: Apex Predator Gauntlet
    gm.start_challenge(1)
    assert gm.current_state == GameState.PLAYING
    assert gm.active_challenge_id == 1
    assert gm.current_level.required_deposits == 4
    assert gm.current_level.config.shark_enabled is True

    # 2. Start Challenge 2: Abyssal Blitz
    gm.start_challenge(2)
    assert gm.active_challenge_id == 2
    assert gm.current_level.time_remaining == 55.0

    # 3. Start Challenge 3: Electric Jellyfish Abyss
    gm.start_challenge(3)
    assert gm.active_challenge_id == 3
    assert len(gm.current_level.marine_manager.jellyfish) == 6

def test_combo_multiplier_streak_progression():
    """Tests that grabbing and depositing genuine relics builds a combo streak, and damage resets it."""
    gm = GameManager()
    gm.start_new_expedition()
    assert gm.combo_count == 0
    assert gm.combo_multiplier == 1.0

    chest = gm.current_level.treasure_manager.chest

    # 1. Grab Relic 1 and deposit into chest
    relic_1 = Treasure(200.0, 200.0, TreasureType.GOLD)
    gm.current_level.treasure_manager.treasures.append(relic_1)
    gm.player.x = 200.0
    gm.player.y = 200.0
    gm._update_gameplay(0.016, 200, 200, pinch_triggered=True, palm_triggered=False, sonar_triggered=False, shield_active=False)
    assert gm.player.carried_treasure == relic_1

    # Carry to chest and deposit
    gm.player.x = chest.x
    gm.player.y = chest.y
    gm._update_gameplay(0.016, int(chest.x), int(chest.y), pinch_triggered=False, palm_triggered=False, sonar_triggered=False, shield_active=False)
    assert gm.combo_count == 1
    assert gm.combo_multiplier == 1.0

    # 2. Grab Relic 2 and deposit into chest
    relic_2 = Treasure(300.0, 300.0, TreasureType.RARE)
    gm.current_level.treasure_manager.treasures.append(relic_2)
    gm.player.x = 300.0
    gm.player.y = 300.0
    gm._update_gameplay(0.016, 300, 300, pinch_triggered=True, palm_triggered=False, sonar_triggered=False, shield_active=False)
    assert gm.player.carried_treasure == relic_2

    # Carry to chest and deposit
    gm.player.x = chest.x
    gm.player.y = chest.y
    gm._update_gameplay(0.016, int(chest.x), int(chest.y), pinch_triggered=False, palm_triggered=False, sonar_triggered=False, shield_active=False)
    assert gm.combo_count == 2
    assert gm.combo_multiplier == 1.5

    # 3. Trigger damage (trap detonation resets combo)
    trap = Treasure(200.0, 200.0, TreasureType.TRAP)
    gm.current_level.treasure_manager.treasures.append(trap)
    gm.player.x = 200.0
    gm.player.y = 200.0
    gm._update_gameplay(0.016, 200, 200, pinch_triggered=True, palm_triggered=False, sonar_triggered=False, shield_active=False)
    assert gm.combo_count == 0
    assert gm.combo_multiplier == 1.0
