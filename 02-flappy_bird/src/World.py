"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class World: the scrolling
background/ground, and the log pairs the bird must fly through.
"""

import random
from typing import List

import pygame

from gale.factory import Factory
from gale.factory import AbstractFactory

import settings
from src.LogPair import LogPair
from src.MovingLogPair import MovingLogPair
from src.ShiftingLogPair import ShiftingLogPair
from src.strategies.WorldStrategies import NormalSpawnStrategy

import src.powerups

class World:
    def __init__(self, generate_logs: bool = False, spawn_strategy=None) -> None:
        self.generate_logs: bool = generate_logs
        self.spawn_strategy = spawn_strategy if spawn_strategy is not None else NormalSpawnStrategy() #Strategy change
        self.background_x: float = 0.0
        self.ground_x: float = 0.0
        self.logs: List[LogPair] = []
        #For new logic 
        self.logs_spawn_timer: float = 0.0
        self.last_log_y: float = -settings.LOG_HEIGHT + random.randint(0, 80) + 20
        self.log_pair_factory: Factory = Factory(LogPair)
        self.moving_log_factory: Factory = Factory(MovingLogPair)
        self.shifting_log_factory: Factory = Factory(ShiftingLogPair)
        self.powerups_abstract_factory = AbstractFactory("src.powerups")
        self.powerups = []
       
    def reset(self, generate_logs: bool) -> None:
        self.generate_logs = generate_logs

    def collides(self, rect: pygame.Rect) -> bool:
        if rect.bottom >= settings.VIRTUAL_HEIGHT:
            return True

        return any(log_pair.collides(rect) for log_pair in self.logs)

    def update_scored(self, rect: pygame.Rect) -> bool:
        return any(log_pair.update_scored(rect) for log_pair in self.logs)

    def update(self, dt: float) -> None:
       #Spawn for new logs if we are in hardmode
       if self.generate_logs:
            self.spawn_strategy.update(self, dt)

       
       speed_mult = getattr(self.spawn_strategy, 'speed_multiplier', 1.0)
       scaled_dt = dt * speed_mult

       self.background_x += -settings.BACK_SCROLL_SPEED * scaled_dt
       if self.background_x <= -settings.BACKGROUND_LOOPING_POINT:
            self.background_x = 0
       self.ground_x += -settings.MAIN_SCROLL_SPEED * scaled_dt
       if self.ground_x <= -settings.VIRTUAL_WIDTH:
            self.ground_x = 0
       for log_pair in self.logs:
            log_pair.update(scaled_dt)
       self.logs = [log_pair for log_pair in self.logs if not log_pair.is_out_of_game()]

       #Clean powerups 
       for pu in self.powerups:
            pu.update(scaled_dt)
       self.powerups = [pu for pu in self.powerups if pu.active]

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(settings.TEXTURES["background"], (round(self.background_x), 0))

        for log_pair in self.logs:
            log_pair.render(surface)
        for pu in self.powerups:
            pu.render(surface)

        surface.blit(
            settings.TEXTURES["ground"],
            (round(self.ground_x), settings.VIRTUAL_HEIGHT - settings.GROUND_HEIGHT),
        )
