"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class PlayingState.
"""

from typing import Optional

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings
from src.Bird import Bird
from src.World import World
from src.strategies.BirdStrategies import HardMovementStrategy, NormalMovementStrategy
from src.strategies.WorldStrategies import HardSpawnStrategy, NormalSpawnStrategy

class PlayingState(BaseState):
    def enter(self, **enter_params: dict) -> None:

        self.mode = enter_params.get("mode", "hard") #Change mode to "hard" or "normal" based on the input parameter
        if self.mode == "hard":
            bird_strategy = HardMovementStrategy()
            spawn_strategy = HardSpawnStrategy()
        else:
            bird_strategy = NormalMovementStrategy()
            spawn_strategy = NormalSpawnStrategy()

        self.world = enter_params.get("world")
        if self.world is None:
            self.world = World()

        if hasattr(self.world.spawn_strategy, 'speed_multiplier') and self.mode == "hard":
            spawn_strategy.speed_multiplier = self.world.spawn_strategy.speed_multiplier
            spawn_strategy.next_spawn_time = self.world.spawn_strategy.next_spawn_time
        
        self.world.spawn_strategy = spawn_strategy
        self.world.reset(True)
        self.bird = enter_params.get("bird")
        if self.bird is None:
            self.bird = Bird(
                settings.VIRTUAL_WIDTH / 2 - settings.BIRD_WIDTH / 2,
                settings.VIRTUAL_HEIGHT / 2 - settings.BIRD_HEIGHT / 2,
                settings.BIRD_WIDTH,
                settings.BIRD_HEIGHT,
                strategy=bird_strategy
            )
        self.score = enter_params.get("score", 0)
        self.grace_timer = enter_params.get("grace_timer", 0.0)
        self.ghost_timer = enter_params.get("ghost_timer", 0.0)
        self.bird.is_ghost = self.ghost_timer > 0
        self.bird.ghost_timer = self.ghost_timer

    def update(self, dt: float) -> None:
        self.bird.update(dt)
        self.world.update(dt)

        if self.bird.is_ghost:
            self.ghost_timer -= dt
            self.bird.ghost_timer = self.ghost_timer 
            
            if self.ghost_timer <= 0:
                self.bird.is_ghost = False
                self.grace_timer = settings.TIME_INVULNERABLE
                settings.SOUNDS["ghost_form"].stop()
                pygame.mixer.music.unpause()
        if self.grace_timer > 0:
            self.grace_timer -= dt        

        for pu in self.world.powerups:
            if pu.in_play and pu.collides(self.bird.get_rect()):
                pu.in_play = False 
                settings.SOUNDS["powerup"].play()
                if not self.bird.is_ghost:
                    pygame.mixer.music.pause()
                    settings.SOUNDS["ghost_form"].play(loops=-1)
                self.bird.is_ghost = True
                self.ghost_timer = settings.TIME_BIRD_FORM 
                self.bird.ghost_timer = settings.TIME_BIRD_FORM

        self.world.powerups = [pu for pu in self.world.powerups if pu.in_play]

        is_dead = False
        sonido_muerte = "explosion"
        if self.bird.get_rect().bottom >= settings.VIRTUAL_HEIGHT - settings.GROUND_HEIGHT or self.bird.y <= - 30:
            is_dead = True
        if not self.bird.is_ghost and self.grace_timer <= 0:
            for log_pair in self.world.logs:
                if log_pair.collides(self.bird.get_rect()):
                    is_dead = True
                    if type(log_pair).__name__ == "MovingLogPair":
                        sonido_muerte = "dead_log_bit"
                    
                    break 
        if is_dead:
            settings.SOUNDS[sonido_muerte].play() 
            settings.SOUNDS["hurt"].play()
            settings.SOUNDS["ghost_form"].stop() 
            pygame.mixer.music.unpause()         
            self.state_machine.change("count_down")
            return
        
        if self.world.update_scored(self.bird.get_rect()):
            self.score += 1
            settings.SOUNDS["score"].play()

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
        self.bird.render(surface)
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["flappy"],
            20,
            10,
            settings.COLOR_WHITE,
            shadowed=True,
        )
        render_text(
            surface,
            f" {self.mode.capitalize()}",
            settings.FONTS["flappy"],
            settings.VIRTUAL_WIDTH - 100, 
            10,
            settings.COLOR_WHITE,
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "jump" and input_data.pressed:
            self.bird.jump()
        if input_id == "confirm" and input_data.pressed:
            self.state_machine.change(
                "pause",
                bird=self.bird,
                world=self.world,     
                score=self.score,
                mode=self.mode,
                ghost_timer=self.ghost_timer,
            )