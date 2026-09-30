"""
Unit tests for collision detection utilities.
"""

import pygame
from game.collision import point_in_circle, point_in_rect, circle_intersect_circle, distance

def test_point_in_circle():
    assert point_in_circle(10, 10, 10, 10, 5) is True
    assert point_in_circle(13, 14, 10, 10, 5) is True  # 3^2 + 4^2 = 25 <= 25
    assert point_in_circle(14, 14, 10, 10, 5) is False # 4^2 + 4^2 = 32 > 25

def test_point_in_rect():
    rect = pygame.Rect(50, 50, 100, 100)
    assert point_in_rect(75, 75, rect) is True
    assert point_in_rect(40, 75, rect) is False
    assert point_in_rect(160, 75, rect) is False

def test_circle_intersect_circle():
    # Overlapping circles
    assert circle_intersect_circle(0, 0, 10, 15, 0, 10) is True # dist 15 <= 20
    # Tangent circles
    assert circle_intersect_circle(0, 0, 10, 20, 0, 10) is True # dist 20 <= 20
    # Separated circles
    assert circle_intersect_circle(0, 0, 10, 25, 0, 10) is False # dist 25 > 20

def test_distance():
    assert distance(0, 0, 3, 4) == 5.0
    assert distance(10, 20, 10, 20) == 0.0
