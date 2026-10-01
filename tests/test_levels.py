"""
Unit tests for level generation, difficulty tuning, and progression conditions.
"""

from game.level import Level
from game.treasure import TreasureType
from config import LEVELS

def test_all_five_levels_exist():
    assert len(LEVELS) == 5
    for lvl_id in range(1, 6):
        assert lvl_id in LEVELS
        level = Level(lvl_id)
        assert level.level_id == lvl_id
        assert len(level.treasure_manager.treasures) > 0
        assert level.time_remaining > 0

def test_level_1_shallow_sea():
    lvl = Level(1)
    assert lvl.config.name == "Shallow Sea"
    assert lvl.config.shark_enabled is False
    # Check that treasures were spawned
    assert len(lvl.treasure_manager.treasures) == (
        lvl.config.common_treasures +
        lvl.config.gold_treasures +
        lvl.config.rare_treasures +
        lvl.config.ancient_treasures +
        lvl.config.fake_treasures +
        lvl.config.traps
    )

def test_level_4_shark_hazard():
    lvl = Level(4)
    assert lvl.config.name == "Lost Ship"
    assert lvl.config.shark_enabled is True

def test_level_completion_condition():
    lvl = Level(1)
    # Level is not complete before meeting deposit requirement
    assert lvl.deposited_count < lvl.required_deposits
    is_complete, is_over, *rest = lvl.update(
        dt=0.1,
        current_active=False,
        cursor_pos=(640, 360),
        shield_active=False
    )
    assert is_complete is False

    # Once required deposits are placed into chest vault, level completes
    lvl.deposited_count = lvl.required_deposits
    is_complete, is_over, *rest = lvl.update(
        dt=0.1,
        current_active=False,
        cursor_pos=(640, 360),
        shield_active=False
    )
    assert is_complete is True
    assert is_over is False

def test_level_timeout_game_over():
    lvl = Level(1)
    lvl.time_remaining = 0.05
    is_complete, is_over, *rest = lvl.update(
        dt=0.1,
        current_active=False,
        cursor_pos=(640, 360),
        shield_active=False
    )
    assert is_over is True
