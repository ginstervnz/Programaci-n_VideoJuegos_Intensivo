from typing import TypeVar
import pygame
import settings
from src.powerups.PowerUp import PowerUp
import math

class ElectroPowerUp(PowerUp):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 0)

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(settings.TEXTURES["electro"], (self.x, self.y))

    def take(self, play_state: TypeVar("PlayState")) -> None:
        # If take electro 
        play_state.paddle.has_rockets = False
        play_state.paddle.is_sticky = False
        play_state.rocket_timer = 0
        play_state.sticky_timer = 0
        play_state.rocket_shots_left = 0
        play_state.lightning_rays = []
        play_state.flash_timer = 0
        
        # If I'm sticky shot ball automatic
        for ball in play_state.balls:
            ball.electro_charges = 2
            if getattr(ball, 'stuck', False):
                ball.stuck = False
                speed = 160 
                radian_angle = math.radians(getattr(play_state, 'arrow_angle', 0))
                ball.vx = speed * math.sin(radian_angle)
                ball.vy = -speed * math.cos(radian_angle)

        settings.SOUNDS["take_electro"].stop()
        settings.SOUNDS["take_electro"].play()
        
        self.active = False