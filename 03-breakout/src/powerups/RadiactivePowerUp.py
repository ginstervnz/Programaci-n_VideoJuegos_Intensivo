from typing import TypeVar
import pygame
import settings
from src.powerups.PowerUp import PowerUp

class RadiactivePowerUp(PowerUp):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 0)

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(settings.TEXTURES["radiactive"], (self.x, self.y))

    def take(self, play_state: TypeVar("PlayState")) -> None:
        for ball in play_state.balls:
            ball.is_radiactive = True
        play_state.radiactive_timer = 5
        
        settings.SOUNDS["radiactive"].stop()
        settings.SOUNDS["radiactive"].play()
        
        self.active = False