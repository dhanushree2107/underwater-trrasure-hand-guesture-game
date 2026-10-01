"""
Underwater Treasure Hunt - Inventory & Underwater Museum System
Tracks diver's carried expedition artifacts, capacity weights, and maintains
the permanent Underwater Museum gallery exhibiting discovered oceanic wonders.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class MuseumExhibit:
    """A permanent museum collection display piece."""
    exhibit_id: str
    name: str
    era: str
    rarity: str
    icon: str
    color_rgb: Tuple[int, int, int]
    lore: str
    is_unlocked: bool = False
    unlocked_in_level: Optional[int] = None


class DiverInventory:
    """Manages carried relics during the dive with weight and capacity limits."""

    def __init__(self, max_capacity: int = 10):
        self.max_capacity = max_capacity
        self.items: Dict[str, int] = {
            "pearl": 0,
            "gold_coin": 0,
            "sapphire_chalice": 0,
            "ancient_vase": 0,
            "ancient_crown": 0,
            "heavy_chest": 0,
            "mystery_gem": 0,
        }

    def clear(self) -> None:
        for k in self.items:
            self.items[k] = 0

    def add_item(self, item_name: str, count: int = 1) -> bool:
        """Adds item if within capacity. Heavy chest occupies 3 capacity slots."""
        weight = 3 if item_name == "heavy_chest" else 1
        current_weight = self.get_current_weight()
        if current_weight + weight * count <= self.max_capacity:
            self.items[item_name] = self.items.get(item_name, 0) + count
            return True
        return False

    def add_treasure(self, treasure) -> bool:
        """Adds a collected treasure to the inventory pouch."""
        t_type = getattr(treasure, "type", None)
        name = getattr(t_type, "value", "pearl") if t_type else "pearl"
        return self.add_item(name.lower(), 1)

    def get_current_weight(self) -> int:
        total = 0
        for k, v in self.items.items():
            w = 3 if k == "heavy_chest" else 1
            total += v * w
        return total

    def get_summary_text(self) -> str:
        parts = []
        labels = {
            "pearl": "🐚 Pearls",
            "gold_coin": "🪙 Gold Coins",
            "sapphire_chalice": "💎 Sapphires",
            "ancient_vase": "🏺 Relic Vases",
            "ancient_crown": "👑 Atlantis Crowns",
            "heavy_chest": "📦 Heavy Relics",
            "mystery_gem": "✨ Mystic Gems",
        }
        for k, label in labels.items():
            qty = self.items.get(k, 0)
            if qty > 0:
                parts.append(f"{label} ×{qty}")
        return " | ".join(parts) if parts else "Empty Pouch"


class UnderwaterMuseum:
    """
    Houses the grand underwater museum gallery of sunken civilization artifacts.
    Expands dynamically as divers discover and deposit ancient treasures.
    """

    def __init__(self):
        self.exhibits: Dict[str, MuseumExhibit] = {
            "pearl": MuseumExhibit(
                exhibit_id="pearl",
                name="Iridescent Luminous Pearl",
                era="Holocene Coral Reef",
                rarity="COMMON",
                icon="🐚",
                color_rgb=(240, 240, 255),
                lore="Harvested from giant abyssal clams in sunlit shallows. Radiates an unearthly bioluminescent glimmer that guides lost divers.",
                is_unlocked=True,
                unlocked_in_level=1
            ),
            "gold_coin": MuseumExhibit(
                exhibit_id="gold_coin",
                name="Spanish Royal Escudo Doubloon",
                era="17th Century Sunken Armada",
                rarity="UNCOMMON",
                icon="🪙",
                color_rgb=(255, 215, 0),
                lore="Minted in Seville and lost aboard the sunken galleon San Pedro. Untarnished by centuries of saltwater and sea currents.",
                is_unlocked=False
            ),
            "sapphire_chalice": MuseumExhibit(
                exhibit_id="sapphire_chalice",
                name="Deep Abyssal Sapphire Chalice",
                era="Classical Hellenic Age",
                rarity="RARE",
                icon="💎",
                color_rgb=(0, 210, 255),
                lore="Carved from a singular massive oceanic sapphire. Legends claim it was blessed by Poseidon to calm tempestuous ocean whirlpools.",
                is_unlocked=False
            ),
            "ancient_vase": MuseumExhibit(
                exhibit_id="ancient_vase",
                name="Minoan Octopod Amphora",
                era="Bronze Age Ruins (1450 BCE)",
                rarity="RARE",
                icon="🏺",
                color_rgb=(210, 140, 60),
                lore="Ceramic vessel painted with ritualistic tentacle motifs. Recovered intact from the submerged corridors of the coral maze.",
                is_unlocked=False
            ),
            "heavy_chest": MuseumExhibit(
                exhibit_id="heavy_chest",
                name="Reinforced Iron Sunken Vault",
                era="Baroque Maritime Era",
                rarity="EPIC",
                icon="📦",
                color_rgb=(185, 120, 50),
                lore="Double-locked nautical strongbox requiring both hands to hoist. Packed with silver bullion and royal astrological navigation charts.",
                is_unlocked=False
            ),
            "ancient_crown": MuseumExhibit(
                exhibit_id="ancient_crown",
                name="Sunken Crown of Atlantis",
                era="Antediluvian Mythic Era",
                rarity="LEGENDARY",
                icon="👑",
                color_rgb=(255, 225, 90),
                lore="The crowning jewel of the lost underwater civilization. Embedded with glowing emeralds and orichalcum that never tarnishes.",
                is_unlocked=False
            ),
            "guardian_seal": MuseumExhibit(
                exhibit_id="guardian_seal",
                name="Talisman of the Ancient Guardian",
                era="Age of Gods",
                rarity="MYTHIC",
                icon="🗿",
                color_rgb=(155, 89, 182),
                lore="Carved from seabed obsidian with pulsing glyphs. Key mechanism used to appease the giant stone guardian of the sunken temple.",
                is_unlocked=False
            ),
            "coral_compass": MuseumExhibit(
                exhibit_id="coral_compass",
                name="Nautilus Treasure Compass",
                era="Age of Exploration",
                rarity="SPECIAL",
                icon="🧭",
                color_rgb=(46, 204, 113),
                lore="Enchanted magnetic lodestone encased in a mother-of-pearl spiral shell. Spins towards hidden oceanic gold and ancient chambers.",
                is_unlocked=False
            ),
        }

    def unlock_exhibit(self, exhibit_id: str, level_id: int) -> bool:
        """Unlocks an exhibit. Returns True if newly unlocked."""
        if exhibit_id in self.exhibits and not self.exhibits[exhibit_id].is_unlocked:
            self.exhibits[exhibit_id].is_unlocked = True
            self.exhibits[exhibit_id].unlocked_in_level = level_id
            return True
        return False

    def register_treasure_deposit(self, treasure, level_id: int = 1) -> Optional[MuseumExhibit]:
        """Registers a deposited relic and unlocks the corresponding museum exhibit if not yet unlocked."""
        t_type = getattr(treasure, "type", None)
        type_val = getattr(t_type, "value", "COMMON") if t_type else "COMMON"
        mapping = {
            "COMMON": "pearl",
            "GOLD": "gold_coin",
            "RARE": "sapphire_chalice",
            "ANCIENT": "ancient_crown",
            "HEAVY": "heavy_chest",
        }
        exhibit_key = mapping.get(type_val, "pearl")
        if self.unlock_exhibit(exhibit_key, level_id):
            return self.exhibits[exhibit_key]
        return None

    def get_unlocked_count(self) -> int:
        return sum(1 for e in self.exhibits.values() if e.is_unlocked)

    def get_total_count(self) -> int:
        return len(self.exhibits)
