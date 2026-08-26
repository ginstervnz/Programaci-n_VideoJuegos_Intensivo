"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class CountDownState.
"""

import pygame

from gale.state import BaseState
from gale.text import render_text

import settings
from src.World import World


class CountDownState(BaseState):
    def enter(self, **enter_params: dict) -> None:
        self.mode = enter_params.get("mode", "hard")
        self.world = enter_params.get("world", World(generate_logs=False))
        self.bird = enter_params.get("bird", None)
        self.score = enter_params.get("score", 0)
        self.counter = 3
        self.timer = 0.0
        self.ghost_timer = enter_params.get("ghost_timer", 0.0)
        self.grace_timer = enter_params.get("grace_timer", 0.0)
        

    def update(self, dt: float) -> None:
        self.timer += dt
        if self.timer >= 1.0:
            self.timer = 0.0
            self.counter -= 1
            if self.counter == 0:
                self.state_machine.change(
                    "playing", 
                    world=self.world, 
                    bird=self.bird, 
                    score=self.score,
                    mode=self.mode,
                    ghost_timer=self.ghost_timer,
                    grace_timer=self.grace_timer,
                )
                return
        if self.bird is None and self.world is not None:
            self.world.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        if self.world is not None:
            self.world.render(surface)
        else:
            surface.blit(settings.TEXTURES["background"], (0, 0))
            surface.blit(settings.TEXTURES["ground"], (0, settings.VIRTUAL_HEIGHT - settings.GROUND_HEIGHT))
        if self.bird:
            self.bird.render(surface)
        
        render_text(
            surface,
            str(self.counter),
            settings.FONTS["huge"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 2,
            settings.COLOR_WHITE,
            center=True,
            shadowed=True,
        )
