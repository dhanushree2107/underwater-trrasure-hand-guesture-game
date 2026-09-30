"""
==============================================================================
                      UNDERWATER TREASURE HUNT
        Vision-Based Hand Gesture Controlled Interactive Game
==============================================================================
Entry point for the application. Initializes the game engine, vision tracker,
and runs the interactive desktop game loop.
"""

import sys
import traceback

def main():
    try:
        from game.game_manager import GameManager
        app = GameManager()
        app.run()
    except KeyboardInterrupt:
        print("\n[Application] Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n[Fatal Error] An unhandled exception occurred: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
