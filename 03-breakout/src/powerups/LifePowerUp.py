from typing import TypeVar
import pygame
import settings
from src.powerups.PowerUp import PowerUp

class LifePowerUp(PowerUp):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 0)

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(settings.TEXTURES["life_powerup"], (self.x, self.y))

    def take(self, play_state: TypeVar("PlayState")) -> None:
        
        if play_state.lives < 3:
            play_state.lives += 1
            settings.SOUNDS["one_up"].stop()
            settings.SOUNDS["one_up"].play()
        else:
            play_state.score += 150
            settings.SOUNDS["one_up"].stop()
            settings.SOUNDS["one_up"].play()
            
        self.active = False