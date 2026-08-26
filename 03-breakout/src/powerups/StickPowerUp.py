from typing import TypeVar
from gale.timer import Timer
import settings
from src.powerups.PowerUp import PowerUp
import pygame
import math

class StickPowerUp(PowerUp):
    """
    Power-up StickPowerUp

    """
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 4)

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(settings.TEXTURES["sticky_up"], (self.x, self.y))

    def take(self, play_state: TypeVar("PlayState")) -> None:
        #If I take sticky change
        play_state.paddle.has_rockets = False
        play_state.rocket_timer = 0
        play_state.rocket_shots_left = 0

        play_state.paddle.is_sticky = True
        play_state.sticky_timer = settings.TIME_POWERUP_STICKY
        
        settings.SOUNDS["sticky"].stop()
        settings.SOUNDS["sticky"].play()
        
        self.active = False

    def remove_effect(self, play_state) -> None:
        play_state.paddle.is_sticky = False
        
        for ball in play_state.balls:
            if getattr(ball, 'stuck', False):
                ball.stuck = False
                speed = 160 
                radian_angle = math.radians(play_state.arrow_angle)
                ball.vx = speed * math.sin(radian_angle)
                ball.vy = -speed * math.cos(radian_angle)