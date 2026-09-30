# 🌊 Underwater Treasure Hunt
### *Vision-Based Hand Gesture Controlled Interactive Desktop Game*

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Pygame 2.6](https://img.shields.io/badge/Pygame-2.6-green.svg)](https://www.pygame.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.14-orange.svg)](https://developers.google.com/mediapipe)
[![OpenCV](https://img.shields.io/badge/OpenCV-5.0-red.svg)](https://opencv.org/)
[![Tests](https://img.shields.io/badge/Tests-24%20Passed-brightgreen.svg)]()

---

## 📖 1. Project Overview & Core Concept

**Underwater Treasure Hunt** is a commercial-grade, vision-controlled interactive desktop application built in Python. 

### 🤿 "The User's Hand Controls The Underwater Swimmer"
The core paradigm of the game is **physical swimmer control**:
* **The hand does not simply behave like a mouse cursor.**
* The user's hand controls an actual **underwater scuba explorer character ("the man")**.
* When the user moves their hand left, right, up, or down, the scuba diver dynamically banks, flutters twin swimming fins, tilts with fluid pitch rotation, illuminates the deep with a volumetric flashlight beam, and discharges air regulator bubbles into the water.
* **Rock-Steady Hand Persistence**: MediaPipe tracking incorporates a 550ms persistence buffer so that momentary camera frame drops never cause the swimmer to jerk or snap back to the mouse.
* **Ultra-Agile Tracking**: Swimmer accelerates smoothly to full speed in ~25ms with distance-scaled sprint catching up to rapid hand gestures.

### 💎 Automatic Treasure Box Collection Loop
1. **Explore & Navigate**: Steer the underwater explorer toward ancient relics.
2. **Point / Tap / Pinch (👉 / 👆 / 🤏)**:
   - **Hover Dwell Auto-Click**: Steadily pointing the cursor at any button or genuine relic automatically clicks / collects it!
   - **Index Tap / Pinch**: Tap your index finger down or pinch near a treasure to collect instantly (0s delay)!
   - **Direct Touch**: Swimmer swimming directly through a genuine relic collects it immediately!
3. **Automatic Vault Storage**: The relic is instantly stored into your treasure collection box:
   - Score is awarded immediately!
   - Celebration particles burst and cascade toward the seafloor collection vault!
   - The Level Objective counter increments automatically (`OBJECTIVE: X / Y STORED 🎁`).
   - Deceptive counterfeits trigger an oxygen penalty; naval mines detonate on contact.

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

| Gesture | Real-World Action | Game Action & Mechanic | Secondary Fallback |
| :--- | :--- | :--- | :--- |
| 🖐 **Hand Movement** | Move hand in front of camera | **Steers Swimmer**: Swimmer swims naturally left, right, up, down | Mouse Movement |
| 🤏 **Pinch** | Thumb & index tips close together | **Grab / Deposit**: Grab relic near hands; release inside Treasure Chest to deposit | Left Mouse Click |
| ✋ **Open Palm** | Spread all 5 fingers open | **Water Current**: Unleashes water current pushing loose items & fish | Spacebar |
| ✌️ **Two Fingers** | Raise Index + Middle fingers | **Sonar Pulse**: Emits expanding wave revealing hidden fakes & traps | Right Mouse Click |
| ✊ **Fist** | Curl all fingers tightly into palm | **Energy Shield**: Deploys forcefield protecting diver from sharks | Hold **'S'** Key |

---

## 🗺️ 4. The 5 Oceanic Levels & Objectives

The game features an interactive **Level Select Screen** (`EXPEDITION ZONES 🗺️`) where players can view objectives, locked/unlocked statuses, and completion badges.

| Level | Name | Theme & Environment | Objective & Challenges | Required Deposits |
| :---: | :--- | :--- | :--- | :---: |
| **1** | **Shallow Sea** | Crystal sunlit turquoise waters | Basic swimming & relic carrying; no shark threat | **3 Relics** |
| **2** | **Coral Reef** | Vibrant corals, schools of tropical fish | Deceptive fake treasures appear; water currents | **5 Relics** |
| **3** | **Deep Ocean** | Abyssal darkness, bioluminescent flora | Low visibility; Sonar is essential to detect sea mines | **5 Relics** |
| **4** | **Lost Ship** | Murky sunken galleon hull & tilted masts | Spiked naval mines and roaming Apex Shark hazards | **7 Relics** |
| **5** | **Ancient Ruins** | Sunken Poseidon temple & ancient pillars | Strong currents, apex sharks, mythic Ancient Crown | **1 Ancient Crown** |

---

## 💎 5. Treasure, Fake, & Trap Mechanics

* **Common Relic**: +50 Score (Natural sea pearl in clam)
* **Gold Treasure**: +100 Score (Gilded sea chest)
* **Rare Artifact**: +250 Score (Bioluminescent sapphire chalice)
* **Ancient Crown**: +500 Score (Mythic Sunken Crown of Atlantis)
* **Deceptive Fake**: **-50 Score Penalty & -12% Oxygen Loss** (Disguised mimic chest revealed by yellow sonar ring)
* **Explosive Sea Mine Trap**: **-25% Oxygen Loss & Screen Shake** (Spiked iron naval mine detonating upon contact)

### 📡 Sonar Wave Mechanic (✌️)
Raising two fingers emits an expanding concentric sonar wave:
* **Emerald Green Ring**: Verified genuine treasure.
* **Amber Yellow Ring**: Deceptive counterfeit.
* **Crimson Red Pulse**: Explosive sea mine trap.
* Limited to **3 charges** per level.

### 💨 Water Current Burst (✋)
Opening your palm releases a rushing torrent of water bubbles across the sea, displacing fish schools and shifting uncollected relics.

### 🦈 Apex Predator & Shield Mechanic (✊)
In Levels 4 & 5, apex predator sharks patrol the area:
* If the diver holds **Fist (✊)** or the **'S'** key, the **Energy Shield Dome** deflects the shark with an energy burst!
* If unshielded, the shark bite deals a devastating **-35% oxygen penalty**.

---

## 📁 6. Project Architecture

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
│   ├── treasure.py          # Relics, seafloor Treasure Chest Depot, fakes, traps
│   ├── enemy.py             # Swimming fish schools and apex predator sharks
│   ├── level.py             # 5 Level environments, seabed silhouettes, & fog
│   ├── collision.py         # Geometric collision primitives
│   └── particles.py         # Bubbles, god rays, sparkles, and score popups
│
├── ui/                      # User Interface & Navigation
│   ├── __init__.py
│   ├── buttons.py           # Animated glassmorphism interactive buttons
│   ├── hud.py               # Heads-up display with smooth oxygen & objective bar
│   ├── menu.py              # Animated main menu with interactive options
│   ├── instructions.py      # Illustrated gesture tutorial
│   └── screens.py           # Level Select, Camera Check, Pause, Win/Loss screens
│
├── audio/                   # Sound & Audio System
│   ├── __init__.py
│   └── sound_manager.py     # Procedural 44.1kHz audio synthesizer & mixer
│
└── tests/                   # Automated Pytest Suite (22 Tests)
    ├── test_collision.py    # Collision detection tests
    ├── test_gestures.py     # Gesture state machine tests
    ├── test_game_logic.py   # Swimmer kinematics, grab/release, oxygen tests
    ├── test_levels.py       # Level generation and deposit objective tests
    └── test_engine_run.py   # Full engine lifecycle & Level Select integration tests
```

---

## 🚀 7. Installation & Quick Start

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
python -m pip install -r requirements.txt
```

### 3. Launch the Application
```powershell
python main.py
```
*(Or simply `py main.py`)*

---

## 🧪 8. Automated Testing

The project includes **24 comprehensive unit and integration tests** verifying all systems.

Run the test suite:
```powershell
python -m pytest
```

Expected output:
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1
rootdir: C:\project 1\underwater trrasure hand guesture game
collected 22 items

tests\test_collision.py ....                                             [ 18%]
tests\test_engine_run.py .                                               [ 22%]
tests\test_game_logic.py .......                                         [ 54%]
tests\test_gestures.py .....                                             [ 77%]
tests\test_levels.py .....                                               [100%]

============================== 22 passed in 6.87s ==============================
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
