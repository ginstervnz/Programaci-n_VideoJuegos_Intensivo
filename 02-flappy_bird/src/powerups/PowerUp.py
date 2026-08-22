
"""
Class for Power-Ups.
"""
from typing import TypeVar, Any
import pygame
import settings

class PowerUp:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.active = True

    def get_rect(self) -> pygame.Rect:
        raise NotImplementedError

    def collides(self, rect: pygame.Rect) -> bool:
        return self.get_rect().colliderect(rect)

    def update(self, dt: float) -> None:
        self.x += -settings.MAIN_SCROLL_SPEED * dt
        if self.x < -100: 
            self.active = False

    def render(self, surface: pygame.Surface) -> None:
        raise NotImplementedError

    def take(self, play_state: TypeVar("PlayingState")) -> None:
        raise NotImplementedError