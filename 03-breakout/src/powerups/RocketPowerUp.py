from typing import TypeVar
import pygame
import settings
import math
from src.powerups.PowerUp import PowerUp

class RocketPowerUp(PowerUp):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 0)

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(settings.TEXTURES["rocket_powerup"], (self.x, self.y))

    def take(self, play_state: TypeVar("PlayState")) -> None:
        #When take rocket powerup
        play_state.paddle.is_sticky = False
        play_state.sticky_timer = 0
       
        
        for ball in play_state.balls:
            if getattr(ball, 'stuck', False):
                ball.stuck = False
                speed = 160 
                radian_angle = math.radians(play_state.arrow_angle)
                ball.vx = speed * math.sin(radian_angle)
                ball.vy = -speed * math.cos(radian_angle)

        #I'm in rocket state
        play_state.paddle.has_rockets = True
        play_state.rocket_timer = settings.ROCKET_TIME
        play_state.rocket_shots_left = 4 #Four shot
        settings.SOUNDS["rocket"].stop()
        settings.SOUNDS["rocket"].play()
        
        self.active = False