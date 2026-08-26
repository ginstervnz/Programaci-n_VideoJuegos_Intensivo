"""
ISPPV1 2023
Study Case: Breakout

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Paddle.
"""

import pygame

import settings


class Paddle:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.width = 64
        self.height = 16

        # By default, the blue paddle
        self.skin = 0

        # By default, the 64-pixels-width paddle.
        self.size = 1

        self.texture = settings.TEXTURES["spritesheet"]
        self.frames = settings.FRAMES["paddles"]

        # The paddle only move horizontally
        self.vx = 0

        #Flag is Sticky
        self.is_sticky = False

        #Flag is Rocket
        self.has_rockets = False

    def resize(self, size: int) -> None:
        self.size = size
        self.width = (self.size + 1) * 32

    def dec_size(self):
        self.resize(max(0, self.size - 1))

    def inc_size(self):
        self.resize(min(3, self.size + 1))

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, dt: float) -> None:
        next_x = self.x + self.vx * dt

        if self.vx < 0:
            self.x = max(0, next_x)
        else:
            self.x = min(settings.VIRTUAL_WIDTH - self.width, next_x)

    def render(self, surface: pygame.Surface) -> None:

        #Change skin paddle
        if getattr(self, 'has_rockets', False):
            current_texture = settings.TEXTURES["paddle_rocket"]
        elif getattr(self, 'is_sticky', False):
            current_texture = settings.TEXTURES["paddle_sticky"]
        else:
            current_texture = self.texture

        surface.blit(current_texture, (self.x, self.y), self.frames[self.skin][self.size]) 

        #Render torrets
        if getattr(self, 'has_rockets', False):
            left_cannon = settings.TEXTURES["rocket_left"]
            right_cannon = settings.TEXTURES["rocket_right"]
            
            left_x = self.x
            left_y = self.y - left_cannon.get_height() + 4
            
            right_x = self.x + self.width - right_cannon.get_width()
            right_y = self.y - right_cannon.get_height() + 4

            surface.blit(left_cannon, (left_x, left_y))
            surface.blit(right_cannon, (right_x, right_y))
        
