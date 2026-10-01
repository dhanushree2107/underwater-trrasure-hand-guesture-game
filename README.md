# 🌊 Underwater Treasure Hunt
### *Vision-Based Hand Gesture Controlled Interactive Desktop Game*

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Pygame 2.6](https://img.shields.io/badge/Pygame-2.6-green.svg)](https://www.pygame.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.14-orange.svg)](https://developers.google.com/mediapipe)
[![OpenCV](https://img.shields.io/badge/OpenCV-5.0-red.svg)](https://opencv.org/)
[![Tests](https://img.shields.io/badge/Tests-35%20Passed-brightgreen.svg)]()

---

## 📖 1. Project Overview & Core Concept

**Underwater Treasure Hunt** is a commercial-grade, vision-controlled interactive desktop adventure built in Python. 

### 🤿 "The User's Hand Controls Both The Swimmer & The Underwater Cursor"
The core paradigm of the game is **physical underwater embodiment**:
* **The hand is NOT just a mouse replacement**: It controls both the physical scuba explorer navigation AND a permanent, custom glowing underwater hand cursor.
* **Always-Visible Underwater Hand Cursor**: The game renders a bespoke, illuminated underwater hand cursor with dynamic glowing halos, targeting crosshairs, and a bubble particle trail. The OS mouse is completely hidden.
* **Contextual Cursor States**: The cursor dynamically shifts appearance based on target:
  - 💠 **NORMAL**: Glowing cyan/blue underwater cursor.
  - 👑 **TREASURE TARGET**: Glowing gold cursor when hovering over relics or mystery crates.
  - ⚠️ **DANGER**: Crimson red warning cursor when targeting mines, counterfeits, or predators.
  - 🤏 **PINCH / GRAB**: Cursor contracts with a vibrant grab halo.
  - ✌️ **SONAR / ✋ CURRENT / ✊ SHIELD**: Custom kinetic pulses matching active gestures.
  - ⚠️ **HAND NOT DETECTED**: Floating warning banner when the hand leaves camera view, safely slowing the swimmer.
* **Natural Swimmer Kinematics**: Moving your hand left, right, up, or down guides the scuba diver, who dynamically banks, flutters twin swimming fins, tilts with fluid pitch rotation, illuminates the deep with a volumetric flashlight beam, and discharges air regulator bubbles.

### 💎 Tactile Grab, Carry & Deposit Loop
1. **Explore & Navigate**: Steer the underwater explorer toward ancient relics.
2. **Aim & Pinch (🤏)**: Move the visible hand cursor over the relic and pinch your thumb and index finger together to **GRAB** the treasure!
3. **Carry**: The treasure visibly attaches to the swimmer's hands and follows as you swim through obstacles, currents, and predators.
4. **Deposit**: Swim to the seafloor Treasure Chest Vault and release your pinch to securely deposit the treasure:
   - Score is credited immediately with celebration burst particles!
   - The Combo Multiplier advances (`🔥 COMBO x2`, `x3`, etc.)!
   - Objective counter updates (`OBJECTIVE: X / Y STORED 🎁`).
   - If pinch is released outside the chest vault, the relic safely drops back to the seabed.

```
       [Webcam Feed @ 30 FPS]
                 │
                 ▼
    [MediaPipe Neural Landmark Pipeline] (Async Background Thread)
                 │
                 ▼
      [Gesture State Machine & EMA Smoothing]
                 │
                 ▼
  [Dynamic Swimmer Kinematics & Hydrodynamic Physics]
                 │
                 ▼
   [Pygame Core Engine @ Locked 60 FPS]
 (Levels • Grab/Carry/Deposit • Oxygen • Sharks • Procedural Audio)
```

---

## 🎯 2. Problem Statement & Proposed Solution

### The Problem
Traditional interactive gaming relies on physical peripherals (mice, keyboards, joysticks). In touchless public installations, interactive exhibits, and modern HCI applications, physical controls are often unhygienic or unintuitive. Furthermore, naive vision implementations suffer from cursor jitter, input lag, duplicate event spamming, and camera frame rate drops.

### The Solution
*Underwater Treasure Hunt* delivers an end-to-end computer vision gaming architecture featuring:
1. **Swimmer Physical Kinematics**: Natural hand movement mapped to an animated scuba diver with fluttering fins, directional headlamp torch, and regulator bubble exhausts.
2. **Multithreaded Camera Decoupling**: Computer vision runs on a dedicated background capture thread (30 FPS), while the Pygame renderer maintains a locked **60 FPS**.
3. **Jitter-Free Exponential Smoothing (EMA) with Dynamic Deadzones**: Eradicates micro-hand tremors while preserving responsive swimmer control.
4. **Strict Gesture State Machine**: Enforces discrete single-trigger semantics (e.g., pinch grab triggers exactly once; release detection resets the state).
5. **Resilient Hardware Fallbacks**: Automatically provides transparent keyboard/mouse controls if a webcam is unavailable or permissions are restricted.
6. **Zero-Dependency Procedural Audio**: Synthesizes rich 44.1kHz sound effects programmatically, guaranteeing the app never crashes due to missing audio assets.

---

## 🖐️ 3. Hand Gesture Controls & Mapping

The entire game (gameplay and all UI menus) is **100% controlled via webcam hand tracking**. The system OS mouse is completely hidden.

| Gesture | Real-World Action | Game Action & In-Game Mechanic | Menu Selection Mechanic |
| :--- | :--- | :--- | :--- |
| 🖐 **Hand Movement** | Move hand in front of camera | **Steers Swimmer & Moves Hand Cursor**: Swimmer swims naturally left, right, up, down; glowing underwater cursor tracks hand | **Moves Cursor**: Moves illuminated hand cursor over buttons |
| 🤏 **Pinch** | Thumb & index tips close together | **Tactile Grab / Deposit**: Grab relic near cursor/hands; release inside Seafloor Vault to deposit; open mystery crates | **Click / Select**: Activates hovered button with glassmorphic press animation |
| ✋ **Open Palm** | Spread all 5 fingers open | **Water Current Burst**: Unleashes surging current pushing loose items, fish, and solving ancient puzzle step | Clears selection / navigates back |
| ✌️ **Two Fingers** | Raise Index + Middle fingers | **Sonar Recon Pulse**: Emits expanding circular wave revealing hidden relics, traps, and solving puzzle step | Quick preview |
| ✊ **Fist** | Curl all fingers tightly into palm | **Energy Shield**: Deploys forcefield dome protecting diver from sharks and jellyfish electric shocks | Pause / Cancel |

---

## 🎯 4. Underwater Hand Cursor (`ui/cursor.py`)

A bespoke, permanently visible underwater cursor renders atop all scenes:
* **Dual Glowing Halos**: Cyan bioluminescent halo with trailing hydrodynamic bubble particles.
* **Contextual State Switching**:
  - `NORMAL`: Ambient cyan halo with subtle crosshair ring.
  - `TREASURE_TARGET`: Gilded gold aura when hovering over relics or mystery crates.
  - `DANGER`: Flashing crimson warning aura when hovering near mines, mimic fakes, or sharks.
  - `PINCH`: Contracted glowing grab ring confirming tactile hold.
  - `SONAR / CURRENT / SHIELD`: Dynamic pulsing waveforms.
* **Hand Loss Safety**: If hand tracking is momentarily lost, a prominent floating `"HAND NOT DETECTED"` warning appears, safely damping swimmer velocity to avoid collision drift.

---

## 🗺️ 5. The 5 Oceanic Levels & Exploration System

The game features an interactive **Level Select Screen** (`EXPEDITION ZONES 🗺️`) where players navigate with their hand cursor, viewing objectives, locked/unlocked statuses, and completion stars.

| Level | Name | Theme & Environment | Unique Mechanics & Hazards | Objective |
| :---: | :--- | :--- | :--- | :---: |
| **1** | **Shallow Sea** | Crystal sunlit turquoise waters | Basic swimming, relic carrying, air bubble station; no major threats | **3 Relics** |
| **2** | **Coral Reef** | Vibrant corals, schools of tropical fish | Coral maze, water currents, mystery crates, mimic counterfeits | **5 Relics** |
| **3** | **Deep Ocean** | Abyssal pitch darkness, bioluminescence | Circular flashlight beam, Sonar reconnaissance, electric jellyfish swarms, naval mines | **5 Relics** |
| **4** | **Lost Ship** | Murky sunken galleon hull & tilted masts | Apex Shark chases, octopus tentacle ambush, random swirling whirlpools, tight corridors | **7 Relics** |
| **5** | **Ancient Ruins** | Sunken Poseidon temple & ancient pillars | Flashlight darkness, apex sharks, whirlpools, Atlantean Gesture Puzzle, Mythic Crown | **Mythic Crown** |

### 🧭 Exploration Fog of War & Seabed Minimap
* **32x18 Seabed Grid**: Areas are initially shrouded in uncharted deep sea fog.
* **Exploration Tracking**: Swimming through coordinates illuminates tiles and tracks your exploration percentage.
* **Corner Radar Minimap**: Displayed in the bottom-left HUD, rendering explored terrain contours, real-time player position, and the seafloor treasure vault depot.
* **Deep Sea Flashlight Beam**: Levels 3, 4, and 5 immerse the player in dark waters where only a focused circular spotlight around the diver pierces the gloom, making Sonar reconnaissance vital!

---

## ⚡ 5.1 Abyssal Challenge Trials (Dedicated Mode)

Accessible directly from the Main Menu (`ABYSSAL CHALLENGES ⚡`), this mode tests mastery of gesture timing and deep-sea survival across three unique gauntlets:

| Trial | Name | Badge | Objective & Modifiers | Win Condition |
| :---: | :--- | :---: | :--- | :---: |
| **#1** | **Apex Predator Gauntlet** | 🦈 GAUNTLET | Relentless Great White sharks charge diver every **10s**. Holding **Fist (✊) / 'S'** deflects charges and awards **+150 DEFLECTION BONUS**! | Retrieve **4 Relics** |
| **#2** | **Abyssal Blitz Rush** | ⏱️ SPEEDRUN | Rapid oxygen depletion (**2.2x speed**, 55s limit). Depositing genuine relics restores **+20% Oxygen** to keep diver alive! | Store **5 Relics** |
| **#3** | **Electric Jellyfish Abyss** | ⚡ MINEFIELD | **6 Pulsating Bioluminescent Jellyfish** drift through the dark. Diver must maneuver smoothly or deploy Shield to deflect electric shocks! | Secure **4 Relics** |

---

## 💎 6. Relics, Hazards & Dynamic Adventure Systems

### 📦 Relic Economy & Mystery Crates
* **Common Relic**: +50 Score (Natural sea pearl in clam)
* **Gold Treasure**: +100 Score (Gilded sea chest)
* **Rare Artifact**: +250 Score (Bioluminescent sapphire chalice)
* **Ancient Crown**: +500 Score (Mythic Sunken Crown of Atlantis)
* **Mystery Crates**: Sunken cargo crates marked with glowing `?`. Pinching the crate cracks it open to reveal random rewards:
  - 🫧 **Oxygen Tank**: +30% Oxygen restore
  - 📡 **Sonar Cell**: +2 Sonar charges
  - 💰 **Gold Ingot**: +150 to +300 bonus score
  - 👑 **Rare Relic**: High-value artifact
  - ⚠️ **Naval Trap**: Disguised explosive penalty!
* **Deceptive Fake**: **-50 Score & -12% Oxygen** (Mimic chest revealed by yellow sonar ring)
* **Naval Sea Mine**: **-25% Oxygen & Screen Shake** (Spiked iron mine detonating on contact)

### 🫧 Air Bubble Stations
Geothermal ocean vents emitting continuous streams of air bubbles. Swimming close restores **+25% Oxygen** with a circular cooldown ring recharging every 12 seconds.

### 🌀 Dynamic Whirlpools
Violent ocean vortexes pulling the diver inward with fluid suction forces. Actively swimming against the vortex breaks the gravitational pull, earning a **"ESCAPED WHIRLPOOL! 🌀 +50"** bonus!

### 🐙 Octopus Ambush (Level 4)
Giant deep-sea cephalopod extending segmented undulating tentacles across the shipwreck corridors. Touching a tentacle deals **-12% Oxygen shock**.

### 🏛️ Ancient Atlantean Gesture Puzzle (Level 5)
A glowing stone pedestal in the Sunken Ruins requiring a mystical three-gesture invocation sequence:
$$\text{✌️ (Sonar Scan)} \longrightarrow \text{✋ (Current Burst)} \longrightarrow \text{🤏 (Pinch Touch)}$$
Executing the correct sequence illuminates ancient Atlantean glyphs, unlocking the secret chamber containing the **Ancient Crown (+500 points)**!

### 🔥 Relic Combo Multiplier Streak
Depositing genuine relics in sequence without taking damage builds a thrilling score multiplier:
* **Streak 1**: `1.0x` Multiplier
* **Streak 2**: `1.5x` Multiplier (+50% bonus points)
* **Streak 3**: `2.0x` Multiplier (Double points)
* **Streak 4+**: `3.0x` Multiplier (Triple points!)
* Taking damage from sharks, jellyfish, sea mines, or counterfeit mimics resets the combo back to `1.0x`.

---

## 📁 7. Project Architecture

```
underwater_treasure_hunt/
│
├── main.py                  # Application entry point & loop runner
├── config.py                # Global parameters, level data, & thresholds
├── requirements.txt         # Pinned production dependencies
├── README.md                # Comprehensive documentation
├── COMPANY_DEMO.md          # Executive company presentation
│
├── hand_tracking/           # Computer Vision & Gesture Recognition
│   ├── __init__.py
│   ├── hand_detector.py     # Multithreaded MediaPipe camera capture (30 FPS)
│   └── gesture_detector.py  # Discrete gesture state machine & EMA smoothing
│
├── game/                    # Game Engine & Kinematics
│   ├── __init__.py
│   ├── game_manager.py      # Master game loop & state coordinator
│   ├── player.py            # Animated scuba diver swimmer character & vitals
│   ├── treasure.py          # Relics, Crates, Air Stations, Vault Depot
│   ├── enemy.py             # Fish schools, Apex Sharks, Whirlpools, Octopus
│   ├── level.py             # 5 Levels, Minimap, Exploration Fog, Ancient Puzzles
│   ├── collision.py         # Geometric collision primitives
│   └── particles.py         # Bubbles, god rays, sparkles, and score popups
│
├── ui/                      # User Interface & Navigation
│   ├── __init__.py
│   ├── cursor.py            # Always-visible glowing underwater hand cursor
│   ├── buttons.py           # Animated glassmorphism interactive buttons
│   ├── hud.py               # Heads-up display with minimap & oxygen meter
│   ├── menu.py              # Animated main menu with hand cursor interaction
│   ├── instructions.py      # Illustrated gesture tutorial
│   └── screens.py           # Level Select, Camera Check, Pause, Win/Loss screens
│
├── audio/                   # Sound & Audio System
│   ├── __init__.py
│   └── sound_manager.py     # Procedural 44.1kHz audio synthesizer & mixer
│
└── tests/                   # Automated Pytest Suite (35 Tests)
    ├── test_adventure_systems.py # Crates, air stations, whirlpools, octopus, puzzles
    ├── test_challenges.py        # Challenge trials, jellyfish, combo streaks
    ├── test_collision.py         # Geometric collision primitives
    ├── test_engine_run.py        # Full engine lifecycle & state machine
    ├── test_game_logic.py        # Swimmer kinematics, grab/release, oxygen
    ├── test_gestures.py          # Gesture state machine & debouncing
    └── test_levels.py            # Level generation & deposit objectives
```

---

## 🚀 8. Installation & Quick Start

### Prerequisites
* Windows 10/11, macOS, or Linux
* Python 3.11 or 3.12 (Python 3.12 recommended)
* Standard USB or integrated webcam

### 1. Clone or Open Workspace
```powershell
cd "c:\project 1\underwater trrasure hand guesture game"
```

### 2. Install Dependencies
```powershell
py -3.12 -m pip install -r requirements.txt
```

### 3. Launch the Application
```powershell
py -3.12 main.py
```

---

## 🧪 9. Automated Testing

The project includes **35 comprehensive unit and integration tests** verifying all systems.

Run the test suite:
```powershell
py -3.12 -m pytest
```

Expected output:
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1
rootdir: C:\project 1\underwater trrasure hand guesture game
collected 35 items

tests\test_adventure_systems.py .......                                  [ 20%]
tests\test_challenges.py ....                                            [ 31%]
tests\test_collision.py ....                                             [ 42%]
tests\test_engine_run.py .                                               [ 45%]
tests\test_game_logic.py .......                                         [ 65%]
tests\test_gestures.py .......                                           [ 85%]
tests\test_levels.py .....                                               [100%]

======================= 35 passed, 6 warnings in 10.00s =======================
```

---

## ⌨️ 9. Keyboard Shortcuts & Accessibility

| Key | Function |
| :---: | :--- |
| **F11** / **F** | Toggle **Full Screen** / Windowed Mode |
| **ESC** | Pause / Resume active mission, or return to Main Menu |
| **D** / **F1** | Toggle **Debug Telemetry Overlay** (FPS, landmarks, gesture state) |
| **M** | Toggle Master Audio Mute |
| **Left Click** | Fallback Pinch (Grab relic / Deposit in chest / Click button) |
| **Right Click** | Fallback Two-Finger Sonar Pulse |
| **Spacebar** | Fallback Open Palm Water Current |
| **S** (Hold) | Fallback Fist Energy Shield |

---

## 🔧 10. Troubleshooting

1. **Webcam Not Detected?**
   * Ensure another app (Teams, Zoom, etc.) isn't holding exclusive lock on the camera.
   * If camera is unavailable, click **"Use Accessibility Controls"** to test with mouse & keyboard seamlessly.
2. **Swimmer Feels Jittery?**
   * Ensure adequate room lighting for clear hand landmark detection.
   * Adjust `SMOOTHING_ALPHA` in `config.py` (e.g., lower to `0.25` for even smoother interpolation).
3. **No Audio Device?**
   * The `SoundManager` features safe hardware fallback: if no audio output device is detected, all audio calls safely become no-ops with zero crashes.

---

## 🔮 11. Future Roadmap
* **Two-Handed Interactions**: Dual-hand cooperative relics requiring simultaneous coordination.
* **Custom VR/AR Projection**: Integration with OpenXR or projection mapping for museum installations.
* **Deep Sea Boss Encounters**: Giant Kraken tentacle hazards requiring timed water currents and shield blocks.
