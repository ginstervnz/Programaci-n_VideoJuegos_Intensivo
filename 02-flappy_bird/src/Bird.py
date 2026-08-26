"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class Bird.
"""

import pygame

import settings
from src.strategies.BirdStrategies import NormalMovementStrategy

class Bird:
    def __init__(self, x: float, y: float, width: float, height: float, strategy=None) -> None:
        self.x: float = x
        self.y: float = y
        self.width: float = width
        self.height: float = height
        self.vy: float = 0.0
        self.jumping: bool = False
        self.is_ghost = False
        self.ghost_timer = 0.0
        self.strategy = strategy if strategy is not None else NormalMovementStrategy()

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x) + 4, round(self.y) + 4, self.width - 8, self.height - 8)

    def jump(self) -> None:
        self.jumping = True

    def update(self, dt: float) -> None:
       self.strategy.update(self, dt)

    def render(self, surface: pygame.Surface) -> None:
        if self.is_ghost and self.ghost_timer < 2.0:
            if int(pygame.time.get_ticks() / 100) % 2 == 0:
                return
        texture_name = "bird_fantasma" if self.is_ghost else "bird"
        surface.blit(settings.TEXTURES[texture_name], (round(self.x), round(self.y)))
