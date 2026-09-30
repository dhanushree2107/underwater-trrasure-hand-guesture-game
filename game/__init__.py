"""Game package initialization."""
from game.collision import point_in_circle, point_in_rect, circle_intersect_circle
from game.particles import ParticleSystem
from game.player import Player
from game.treasure import Treasure, TreasureType, TreasureManager
from game.enemy import Fish, Shark, MarineLifeManager
from game.level import Level

__all__ = [
    "point_in_circle",
    "point_in_rect",
    "circle_intersect_circle",
    "ParticleSystem",
    "Player",
    "Treasure",
    "TreasureType",
    "TreasureManager",
    "Fish",
    "Shark",
    "MarineLifeManager",
    "Level",
]
