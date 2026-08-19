"""
ISPPV1 2023
Study Case: Pong

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class Paddle.
"""

import pygame

import settings


class Paddle:
    def __init__(self, x: float, y: float, width: float, height: float, is_ai: bool = False) -> None:
        self.x: float = x
        self.y: float = y
        self.width: float = width
        self.height: float = height
        self.vy: float = 0.0
        self.is_ai: bool = is_ai # Flag to indicate if the paddle is controlled by AI
        self.color: tuple[int, int, int] = (255, 0, 0) if self.is_ai else (255, 255, 255) #Color red for AI-controlled paddle, white for human-controlled paddle

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def update(self, dt: float) -> None:
        self.y += self.vy * dt
        self.y = max(0, min(self.y, settings.VIRTUAL_HEIGHT - self.height))

    def render(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.color, self.get_rect()) #Changed the color of the paddle based on whether it is controlled by AI or a human player
