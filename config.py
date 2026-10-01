"""
Underwater Treasure Hunt - Global Configuration
Defines all screen, game, gesture, level, and audio parameters.
"""

from dataclasses import dataclass
from typing import Dict, Tuple

# Display Settings
SCREEN_WIDTH: int = 1280
SCREEN_HEIGHT: int = 720
TARGET_FPS: int = 60
FULLSCREEN: bool = True  # Start in immersive full screen mode (Press F11 to toggle)
TITLE: str = "Underwater Treasure Hunt"
SUBTITLE: str = "Vision-Based Hand Gesture Controlled Interactive Game"

# Camera Settings
CAMERA_INDEX: int = 0
CAMERA_WIDTH: int = 640
CAMERA_HEIGHT: int = 480
CAMERA_FPS: int = 30
CAMERA_FLIP_HORIZONTAL: bool = True  # Mirror camera for natural movement

# Hand Tracking & Gesture Parameters
MAX_NUM_HANDS: int = 1
MIN_DETECTION_CONFIDENCE: float = 0.5
MIN_TRACKING_CONFIDENCE: float = 0.5

# Gesture Thresholds
PINCH_THRESHOLD: float = 0.082          # Distance between thumb and index tips (normalized)
PINCH_RELEASE_THRESHOLD: float = 0.112  # Threshold to reset click state
INDEX_TAP_BEND_RATIO: float = 1.32      # Ratio when index finger bends/taps down to click
PINCH_COOLDOWN: float = 0.28            # Seconds between allowed clicks

PALM_OPEN_MIN_EXTENDED: int = 4       # Number of extended fingers for open palm
PALM_COOLDOWN: float = 2.5            # Seconds cooldown for water current

TWO_FINGER_COOLDOWN: float = 2.0      # Seconds cooldown for sonar activation
FIST_THRESHOLD: float = 0.12          # Average distance from finger tips to wrist when curled

# Position Smoothing
SMOOTHING_ALPHA: float = 0.35         # Higher = more responsive, lower = smoother (0.0 - 1.0)
CURSOR_MARGIN: int = 20               # Inset border to keep cursor within playable screen area

# Gameplay Rules & Mechanics
INITIAL_OXYGEN: float = 100.0
PASSIVE_OXYGEN_DEPLETION_RATE: float = 0.85  # % lost per second passively
FAKE_TREASURE_OXYGEN_PENALTY: float = 12.0  # % lost on fake treasure interaction
TRAP_OXYGEN_PENALTY: float = 25.0           # % lost on sea mine/trap hit
SHARK_OXYGEN_PENALTY: float = 35.0          # % lost on shark bite without shield

# Sonar Parameters
SONAR_INITIAL_CHARGES: int = 3
SONAR_WAVE_SPEED: float = 420.0       # Pixels per second expansion
SONAR_MAX_RADIUS: float = 750.0
SONAR_REVEAL_DURATION: float = 4.0    # Seconds highlights remain visible

# Water Current Parameters
WATER_CURRENT_DURATION: float = 2.2   # Seconds of current burst
WATER_CURRENT_FORCE: float = 180.0    # Drift displacement force on objects

# Treasure Score Values
SCORE_COMMON: int = 50
SCORE_GOLD: int = 100
SCORE_RARE: int = 250
SCORE_ANCIENT: int = 500
SCORE_FAKE_PENALTY: int = -50

# Color Palette (Rich RGB)
COLOR_DEEP_BLUE: Tuple[int, int, int] = (8, 22, 48)
COLOR_OCEAN_CYAN: Tuple[int, int, int] = (0, 180, 216)
COLOR_NEON_TEAL: Tuple[int, int, int] = (0, 245, 212)
COLOR_GOLD: Tuple[int, int, int] = (255, 215, 0)
COLOR_EMERALD: Tuple[int, int, int] = (46, 204, 113)
COLOR_CORAL_RED: Tuple[int, int, int] = (231, 76, 60)
COLOR_AMBER_WARNING: Tuple[int, int, int] = (243, 156, 18)
COLOR_PURPLE_MYSTIC: Tuple[int, int, int] = (155, 89, 182)
COLOR_WHITE: Tuple[int, int, int] = (255, 255, 255)
COLOR_DARK_OVERLAY: Tuple[int, int, int] = (5, 12, 28)

# Swimmer Character Physics
SWIMMER_SPEED: float = 460.0
SWIMMER_ACCEL: float = 1200.0
SWIMMER_FRICTION: float = 0.86
DEPOSIT_ZONE_RADIUS: float = 85.0

# Level Configurations
@dataclass
class LevelConfig:
    level_id: int
    name: str
    description: str
    target_score: int
    required_deposits: int # Number of treasures needed to complete level
    time_limit: float  # Seconds
    common_treasures: int
    gold_treasures: int
    rare_treasures: int
    ancient_treasures: int
    fake_treasures: int
    traps: int
    ambient_color: Tuple[int, int, int]
    deep_color: Tuple[int, int, int]
    visibility: float   # 1.0 = clear, 0.4 = murky/deep
    shark_enabled: bool
    shark_interval: float  # Mean seconds between shark spawns


LEVELS: Dict[int, LevelConfig] = {
    1: LevelConfig(
        level_id=1,
        name="Shallow Sea",
        description="Sunlit crystal waters. Swim with your hand, grab relics, and deposit them into the treasure chest.",
        target_score=150,
        required_deposits=3,
        time_limit=85.0,
        common_treasures=6,
        gold_treasures=2,
        rare_treasures=0,
        ancient_treasures=0,
        fake_treasures=1,
        traps=0,
        ambient_color=(12, 65, 110),
        deep_color=(4, 28, 55),
        visibility=1.0,
        shark_enabled=False,
        shark_interval=999.0
    ),
    2: LevelConfig(
        level_id=2,
        name="Coral Reef",
        description="A bustling biome rich in treasure. Water currents introduced. Deposit 5 relics to advance.",
        target_score=350,
        required_deposits=5,
        time_limit=90.0,
        common_treasures=5,
        gold_treasures=4,
        rare_treasures=1,
        ancient_treasures=0,
        fake_treasures=3,
        traps=1,
        ambient_color=(10, 52, 98),
        deep_color=(3, 20, 48),
        visibility=0.9,
        shark_enabled=False,
        shark_interval=999.0
    ),
    3: LevelConfig(
        level_id=3,
        name="Deep Ocean",
        description="Abyssal depth with low light. Use two-finger Sonar to uncover hidden traps and deposit 5 relics.",
        target_score=600,
        required_deposits=5,
        time_limit=95.0,
        common_treasures=4,
        gold_treasures=4,
        rare_treasures=3,
        ancient_treasures=0,
        fake_treasures=4,
        traps=3,
        ambient_color=(5, 30, 68),
        deep_color=(2, 10, 28),
        visibility=0.65,
        shark_enabled=False,
        shark_interval=999.0
    ),
    4: LevelConfig(
        level_id=4,
        name="Lost Ship",
        description="A sunken galleon haunted by sea mines and prowling sharks. Recover and deposit 7 treasures.",
        target_score=900,
        required_deposits=7,
        time_limit=105.0,
        common_treasures=3,
        gold_treasures=5,
        rare_treasures=4,
        ancient_treasures=1,
        fake_treasures=5,
        traps=4,
        ambient_color=(6, 38, 58),
        deep_color=(2, 14, 25),
        visibility=0.55,
        shark_enabled=True,
        shark_interval=20.0
    ),
    5: LevelConfig(
        level_id=5,
        name="Ancient Treasure",
        description="The Sunken Temple of the Ancients. Find and deposit the mythical Ancient Crown while evading sharks!",
        target_score=1200,
        required_deposits=1,
        time_limit=110.0,
        common_treasures=2,
        gold_treasures=4,
        rare_treasures=3,
        ancient_treasures=2,
        fake_treasures=5,
        traps=5,
        ambient_color=(8, 20, 45),
        deep_color=(1, 6, 16),
        visibility=0.5,
        shark_enabled=True,
        shark_interval=16.0
    )
}

# Abyssal Challenge Expeditions Configuration
@dataclass
class ChallengeConfig:
    challenge_id: int
    title: str
    subtitle: str
    description: str
    target_score: int
    required_deposits: int
    time_limit: float
    shark_interval: float
    jellyfish_count: int
    oxygen_drain_mult: float
    relic_oxygen_restore: float
    badge_icon: str
    accent_color: Tuple[int, int, int]
    level_config: LevelConfig

CHALLENGES: Dict[int, ChallengeConfig] = {
    1: ChallengeConfig(
        challenge_id=1,
        title="APEX PREDATOR GAUNTLET",
        subtitle="Shield Timing & Predator Deflection",
        description="Prowling Great White Sharks patrol the abyss every 10 seconds! Deflect charging sharks with your Shield [✊ Fist / 'S'] while gathering 4 rare oceanic relics! Deflections award +150 bonus points!",
        target_score=800,
        required_deposits=4,
        time_limit=85.0,
        shark_interval=10.0,
        jellyfish_count=0,
        oxygen_drain_mult=1.0,
        relic_oxygen_restore=0.0,
        badge_icon="🦈",
        accent_color=COLOR_CORAL_RED,
        level_config=LevelConfig(
            level_id=101,
            name="Apex Gauntlet",
            description="Predator Hunt Challenge",
            target_score=800,
            required_deposits=4,
            time_limit=85.0,
            common_treasures=3,
            gold_treasures=4,
            rare_treasures=4,
            ancient_treasures=1,
            fake_treasures=3,
            traps=2,
            ambient_color=(6, 25, 48),
            deep_color=(2, 10, 22),
            visibility=0.7,
            shark_enabled=True,
            shark_interval=10.0
        )
    ),
    2: ChallengeConfig(
        challenge_id=2,
        title="ABYSSAL BLITZ RUSH",
        subtitle="Rapid Speed Trial & Oxygen Combos",
        description="Oxygen drains 2.2x faster! Every genuine relic collected instantly restores +20% oxygen and stacks combo multipliers (up to 3x)! Chain rapid pickups to survive the deep!",
        target_score=1100,
        required_deposits=6,
        time_limit=55.0,
        shark_interval=999.0,
        jellyfish_count=2,
        oxygen_drain_mult=2.2,
        relic_oxygen_restore=20.0,
        badge_icon="⏱️",
        accent_color=COLOR_GOLD,
        level_config=LevelConfig(
            level_id=102,
            name="Abyssal Blitz",
            description="Rapid Oxygen Rush Challenge",
            target_score=1100,
            required_deposits=6,
            time_limit=55.0,
            common_treasures=6,
            gold_treasures=5,
            rare_treasures=3,
            ancient_treasures=1,
            fake_treasures=2,
            traps=1,
            ambient_color=(12, 45, 80),
            deep_color=(4, 18, 40),
            visibility=0.85,
            shark_enabled=False,
            shark_interval=999.0
        )
    ),
    3: ChallengeConfig(
        challenge_id=3,
        title="ELECTRIC JELLYFISH ABYSS",
        subtitle="Precision Navigation & Swarm Avoidance",
        description="A bioluminescent field of 6 electric jellyfish drifts through the darkness. Touching jellyfish zaps oxygen unless safely deflected with your Forcefield Shield [✊ Fist / 'S']!",
        target_score=1000,
        required_deposits=5,
        time_limit=90.0,
        shark_interval=24.0,
        jellyfish_count=6,
        oxygen_drain_mult=1.1,
        relic_oxygen_restore=5.0,
        badge_icon="⚡",
        accent_color=COLOR_PURPLE_MYSTIC,
        level_config=LevelConfig(
            level_id=103,
            name="Jellyfish Abyss",
            description="Electric Minefield Challenge",
            target_score=1000,
            required_deposits=5,
            time_limit=90.0,
            common_treasures=4,
            gold_treasures=4,
            rare_treasures=4,
            ancient_treasures=2,
            fake_treasures=4,
            traps=3,
            ambient_color=(8, 18, 52),
            deep_color=(3, 8, 25),
            visibility=0.6,
            shark_enabled=True,
            shark_interval=24.0
        )
    ),
}

