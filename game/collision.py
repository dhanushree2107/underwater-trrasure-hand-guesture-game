"""
Underwater Treasure Hunt - Collision Detection Utilities
Provides high-efficiency geometry checks for cursor interaction,
sonar reveals, and hazard boundaries.
"""

import math
from typing import Tuple
import pygame

def point_in_circle(px: float, py: float, cx: float, cy: float, radius: float) -> bool:
    """Checks whether point (px, py) lies inside circle centered at (cx, cy)."""
    dx = px - cx
    dy = py - cy
    return (dx * dx + dy * dy) <= (radius * radius)

def point_in_rect(px: float, py: float, rect: pygame.Rect) -> bool:
    """Checks whether point (px, py) lies within a Pygame Rect."""
    return rect.collidepoint(int(px), int(py))

def circle_intersect_circle(c1x: float, c1y: float, r1: float, c2x: float, c2y: float, r2: float) -> bool:
    """Checks whether two circles intersect."""
    dx = c1x - c2x
    dy = c1y - c2y
    total_r = r1 + r2
    return (dx * dx + dy * dy) <= (total_r * total_r)

def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculates Euclidean distance between two points."""
    return math.hypot(x1 - x2, y1 - y2)
