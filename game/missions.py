"""
Underwater Treasure Hunt - Mission & Objectives System
Defines Main Missions and Optional Side Missions for each level,
evaluating performance, bonus rewards, and 1-3 star expedition achievements.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class MissionType(Enum):
    COLLECT_DEPOSIT = "COLLECT_DEPOSIT"
    MAINTAIN_OXYGEN = "MAINTAIN_OXYGEN"
    ESCAPE_SHARK = "ESCAPE_SHARK"
    SWIM_COMBO = "SWIM_COMBO"
    OPEN_MYSTERY_CRATES = "OPEN_MYSTERY_CRATES"
    NO_DAMAGE = "NO_DAMAGE"
    USE_SONAR = "USE_SONAR"
    HEAVY_TREASURE = "HEAVY_TREASURE"
    SOLVE_PUZZLE = "SOLVE_PUZZLE"


@dataclass
class MissionGoal:
    """An individual mission objective with progress tracking."""
    goal_id: str
    title: str
    description: str
    is_main: bool
    target_count: int = 1
    current_count: int = 0
    completed: bool = False
    reward_score: int = 200

    def record_progress(self, amount: int = 1) -> bool:
        """Increments progress. Returns True if goal just became completed."""
        if self.completed:
            return False
        self.current_count = min(self.target_count, self.current_count + amount)
        if self.current_count >= self.target_count:
            self.completed = True
            return True
        return False


@dataclass
class LevelMissions:
    """Contains main and side missions for a specific level."""
    level_id: int
    main_mission: MissionGoal
    side_missions: List[MissionGoal] = field(default_factory=list)


class MissionManager:
    """Manages active level missions, side objectives, and calculates expedition star ratings."""

    def __init__(self):
        self.active_level_id: int = 1
        self.main_mission: Optional[MissionGoal] = None
        self.side_missions: List[MissionGoal] = []
        self.completed_history: Dict[int, List[str]] = {}

    def start_level(self, level_id: int, required_deposits: int) -> None:
        """Initializes missions for the selected level."""
        self.active_level_id = level_id

        if level_id == 1:
            self.main_mission = MissionGoal(
                goal_id="lvl1_main",
                title="Recover & Deposit 3 Relics",
                description=f"Collect and safely deposit {required_deposits} relics into the Treasure Depot.",
                is_main=True,
                target_count=required_deposits,
                reward_score=300
            )
            self.side_missions = [
                MissionGoal("lvl1_oxy", "Deep Lung Diver", "Finish the shallow sea expedition with >60% oxygen.", False, 1, reward_score=250),
                MissionGoal("lvl1_combo", "Synchronized Rhythm", "Trigger a 2-hand Combo Swim with high rhythm.", False, 1, reward_score=200),
                MissionGoal("lvl1_deposit_clean", "Flawless Haul", "Deposit relics without accidentally grabbing fake loot.", False, 1, reward_score=150),
            ]

        elif level_id == 2:
            self.main_mission = MissionGoal(
                goal_id="lvl2_main",
                title="Navigate Coral Maze & Deposit 5 Relics",
                description=f"Overcome currents and deposit {required_deposits} ocean treasures.",
                is_main=True,
                target_count=required_deposits,
                reward_score=500
            )
            self.side_missions = [
                MissionGoal("lvl2_crates", "Salvage Hunter", "Pinch and open 2 Mystery Crates in the reef.", False, 2, reward_score=300),
                MissionGoal("lvl2_notrap", "Mine Sweeper", "Complete the dive without triggering any sea mine traps.", False, 1, reward_score=350),
                MissionGoal("lvl2_oxy", "Oxygen Conserver", "Finish the coral reef with >55% oxygen.", False, 1, reward_score=250),
            ]

        elif level_id == 3:
            self.main_mission = MissionGoal(
                goal_id="lvl3_main",
                title="Abyssal Descent: Deposit 5 Relics",
                description=f"Explore the pitch-black abyss and recover {required_deposits} relics.",
                is_main=True,
                target_count=required_deposits,
                reward_score=750
            )
            self.side_missions = [
                MissionGoal("lvl3_sonar", "Acoustic Scanner", "Activate 2-finger Sonar wave 3 times.", False, 3, reward_score=300),
                MissionGoal("lvl3_deflect", "Electric Ward", "Deflect an electric jellyfish with Shield [✊ Fist].", False, 1, reward_score=400),
                MissionGoal("lvl3_heavy", "Two-Hand Hauler", "Carry and deposit a heavy sunken relic with both hands.", False, 1, reward_score=500),
            ]

        elif level_id == 4:
            self.main_mission = MissionGoal(
                goal_id="lvl4_main",
                title="Sunken Galleon: Recover 7 Treasures",
                description=f"Plunder the sunken pirate ship and deposit {required_deposits} treasures.",
                is_main=True,
                target_count=required_deposits,
                reward_score=1000
            )
            self.side_missions = [
                MissionGoal("lvl4_shark", "Apex Evader", "Escape a prowling shark chase safely.", False, 1, reward_score=450),
                MissionGoal("lvl4_octopus", "Tentacle Dancer", "Evade all giant octopus ambush tentacles.", False, 1, reward_score=400),
                MissionGoal("lvl4_heavy", "Dual-Hand Strongman", "Carry a heavy treasure chest with both hands without dropping.", False, 1, reward_score=600),
            ]

        else: # Level 5: Ancient Treasure
            self.main_mission = MissionGoal(
                goal_id="lvl5_main",
                title="Sunken Temple: Recover Ancient Crown",
                description="Solve ancient guardian seals and claim the mythical Sunken Crown of Atlantis.",
                is_main=True,
                target_count=required_deposits,
                reward_score=1500
            )
            self.side_missions = [
                MissionGoal("lvl5_puzzle", "Ancient Cryptographer", "Solve an ancient symbol gesture sequence.", False, 1, reward_score=500),
                MissionGoal("lvl5_seal", "Synchronized Seal Breaker", "Break the Two-Handed Ancient Seal door.", False, 1, reward_score=650),
                MissionGoal("lvl5_lives", "Legendary Explorer", "Survive the final ruins expedition with all 3 lives intact.", False, 1, reward_score=800),
            ]

    def record_event(self, event_type: str, count: int = 1) -> List[str]:
        """
        Notifies missions of in-game events.
        Returns list of newly completed mission titles.
        """
        completed_titles = []
        if event_type == "DEPOSIT" and self.main_mission:
            if self.main_mission.record_progress(count):
                completed_titles.append(self.main_mission.title)

        for sm in self.side_missions:
            if sm.completed:
                continue
            matched = False
            if event_type == "OPEN_CRATE" and "crates" in sm.goal_id:
                matched = True
            elif event_type == "SHARK_ESCAPE" and "shark" in sm.goal_id:
                matched = True
            elif event_type == "SONAR_PULSE" and "sonar" in sm.goal_id:
                matched = True
            elif event_type == "DEFLECT_JELLYFISH" and "deflect" in sm.goal_id:
                matched = True
            elif event_type == "COMBO_SWIM" and "combo" in sm.goal_id:
                matched = True
            elif event_type == "HEAVY_DEPOSIT" and "heavy" in sm.goal_id:
                matched = True
            elif event_type == "PUZZLE_SOLVED" and "puzzle" in sm.goal_id:
                matched = True
            elif event_type == "SEAL_OPENED" and "seal" in sm.goal_id:
                matched = True

            if matched and sm.record_progress(count):
                completed_titles.append(sm.title)

        return completed_titles

    def check_end_of_level(self, final_oxygen: float, final_lives: int, had_trap_hit: bool, had_fake_hit: bool) -> List[str]:
        """Checks end-of-level conditions (e.g. oxygen conservation, flawless run)."""
        newly_done = []
        for sm in self.side_missions:
            if sm.completed:
                continue
            if "oxy" in sm.goal_id:
                threshold = 60.0 if "lvl1" in sm.goal_id else 55.0
                if final_oxygen >= threshold:
                    sm.record_progress(1)
                    newly_done.append(sm.title)
            elif "notrap" in sm.goal_id and not had_trap_hit:
                sm.record_progress(1)
                newly_done.append(sm.title)
            elif "deposit_clean" in sm.goal_id and not had_fake_hit:
                sm.record_progress(1)
                newly_done.append(sm.title)
            elif "lives" in sm.goal_id and final_lives >= 3:
                sm.record_progress(1)
                newly_done.append(sm.title)
        return newly_done

    def update_time(self, dt: float) -> None:
        """Updates internal mission clocks and timers."""
        pass

    @property
    def active_side_missions(self) -> List[MissionGoal]:
        return self.side_missions

    def calculate_stars(
        self,
        final_score: int = 0,
        final_oxygen: float = 100.0,
        target_score: int = 500,
        remaining_oxygen: Optional[float] = None,
        time_remaining: Optional[float] = None,
        lives: int = 3,
    ) -> Tuple[int, int]:
        """Calculates 1 to 3 star rating for level performance and completed side count."""
        ox = remaining_oxygen if remaining_oxygen is not None else final_oxygen
        stars = 1  # 1 star for clearing the main mission
        completed_sides = sum(1 for sm in self.side_missions if sm.completed)

        # 2 stars if beat target score OR finished 2+ side missions OR high oxygen
        if final_score >= target_score or completed_sides >= 2 or ox >= 50.0:
            stars = 2

        # 3 stars if beat target score AND completed all side missions AND had >45% oxygen
        if (final_score >= target_score and completed_sides == len(self.side_missions) and ox >= 45.0) or (final_score >= target_score * 1.35) or (lives >= 3 and ox >= 60.0):
            stars = 3

        return max(1, min(3, stars)), completed_sides
