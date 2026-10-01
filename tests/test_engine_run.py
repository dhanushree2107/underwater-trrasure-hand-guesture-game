"""
Integration test verifying GameManager initialization, state changes,
level loading, frame updates, and rendering integrity.
"""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from game.game_manager import GameManager, GameState
from game.treasure import TreasureType

def test_game_manager_full_lifecycle():
    # Initialize game manager in headless dummy mode
    gm = GameManager()
    assert gm.running is True
    assert gm.current_state == GameState.MAIN_MENU

    # 1. Test Menu update & render
    gm._update(0.016)
    gm._render()

    # 2. Test State Transitions
    gm.set_state(GameState.LEVEL_SELECT)
    gm._update(0.016)
    gm._render()

    gm.set_state(GameState.HOW_TO_PLAY)
    gm._update(0.016)
    gm._render()

    gm.set_state(GameState.CAMERA_CHECK)
    gm._update(0.016)
    gm._render()

    # 3. Test Starting Game
    gm.start_new_expedition()
    assert gm.current_state == GameState.PLAYING
    assert gm.current_level_id == 1
    assert gm.current_level is not None

    # 4. Simulate active gameplay frames
    for _ in range(30):
        gm._update(0.016)
        gm._render()

    # 5. Simulate Sonar Wave
    gm._update_gameplay(
        dt=0.016,
        target_x=640,
        target_y=360,
        pinch_triggered=False,
        palm_triggered=False,
        sonar_triggered=True,
        shield_active=False
    )
    assert gm.player.sonar_charges == 2

    # 6. Simulate Water Current
    gm._update_gameplay(
        dt=0.016,
        target_x=640,
        target_y=360,
        pinch_triggered=False,
        palm_triggered=True,
        sonar_triggered=False,
        shield_active=False
    )
    assert gm.player.current_active_timer > 0

    # 7. Simulate Treasure Pickup: Automatically stored into treasure box & score
    # 7. Simulate Treasure Grab, Carry, and Deposit into Vault
    genuine_treasures = [
        t for t in gm.current_level.treasure_manager.treasures
        if t.type not in (TreasureType.TRAP, TreasureType.FAKE) and not t.collected
    ]
    first_treasure = genuine_treasures[0]
    initial_score = gm.player.score
    initial_deposited = gm.current_level.deposited_count
    gm.player.x = first_treasure.x
    gm.player.y = first_treasure.y
    gm._update_gameplay(
        dt=0.016,
        target_x=int(first_treasure.x),
        target_y=int(first_treasure.y),
        pinch_triggered=True,
        palm_triggered=False,
        sonar_triggered=False,
        shield_active=False
    )
    # Treasure is grabbed and carried
    assert gm.player.carried_treasure is not None
    carried = gm.player.carried_treasure

    # Swimmer carries to chest vault and deposits
    chest = gm.current_level.treasure_manager.chest
    gm.player.x = chest.x
    gm.player.y = chest.y
    gm._update_gameplay(
        dt=0.016,
        target_x=int(chest.x),
        target_y=int(chest.y),
        pinch_triggered=False,
        palm_triggered=False,
        sonar_triggered=False,
        shield_active=False
    )
    assert carried.collected is True
    assert gm.current_level.deposited_count == initial_deposited + 1
    assert gm.player.score > initial_score

    # 8. Test All 5 Levels can load and render without fault
    for lvl in range(1, 6):
        gm.load_level(lvl)
        assert gm.current_level.level_id == lvl
        for _ in range(10):
            gm._update(0.016)
            gm._render()

    # 9. Test Pause & Resume
    gm.set_state(GameState.PAUSED)
    gm._update(0.016)
    gm._render()

    gm.set_state(GameState.PLAYING)
    assert gm.current_state == GameState.PLAYING

    # 10. Test Hand Tracking Reticle Rendering for all gesture states
    from hand_tracking.gesture_detector import GestureType
    gm.is_hand_detected = True
    for g_type in (GestureType.NONE, GestureType.PINCH, GestureType.TWO_FINGERS, GestureType.OPEN_PALM, GestureType.FIST):
        gm.gesture_detector.current_gesture = g_type
        gm._render()

    # 10. Clean shutdown
    gm.hand_detector.stop()
    pygame.quit()
