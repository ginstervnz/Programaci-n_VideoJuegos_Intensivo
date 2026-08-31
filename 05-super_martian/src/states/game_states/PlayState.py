"""
ISPPV1 2023
Study Case: Super Martian (Platformer)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState.
"""

from typing import Dict, Any

import pygame

from gale.camera import Camera
from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text
from gale.timer import Timer

import settings
from src.Clock import Clock
from src.GameLevel import GameLevel
from src.Player import Player
from src.states.entities.creatures_states.SnailDieState import SnailDieState


class PlayState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.level = enter_params.get("level", 1)
        self.game_level = enter_params.get("game_level")

        # Always initialize this variable using the passed params
        self.special_event_triggered = enter_params.get("special_event_triggered", False)

        if self.game_level is None:
            self.game_level = GameLevel(self.level)
            music_track = "level3_music.mp3" if self.level == 3 else "music_grassland.ogg"
            pygame.mixer.music.load(
                settings.BASE_DIR / "assets" / "sounds" / music_track
            )
            pygame.mixer.music.play(loops=-1)
            
        self.tilemap = self.game_level.tilemap
        self.player = enter_params.get("player")
        if self.player is None:
            # Resting exactly on the ground tile's surface (row 9, one tile
            # below the platform's top edge) rather than a few pixels into
            # it, so gale.tilemap's one-way platform collision (which
            # requires the entity to already be at/above the surface) picks
            # it up on the very first frame instead of falling through.
            spawn_y = 9 * self.tilemap.tile_height - 20
            self.player = Player(0, spawn_y, self.game_level)
            self.player.change_state("idle")

            # Restore previous level data
            self.player.score = enter_params.get("saved_score", 0)
            saved_coins = enter_params.get("saved_coins")
            if saved_coins is not None:
                self.player.coins_counter = saved_coins
            
        self.camera = enter_params.get("camera")

        if self.camera is None:
            self.camera = Camera(settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
            self.camera.follow(self.player, rate=settings.CAMERA_FOLLOW_RATE)
            self.camera.bounds = self.game_level.get_rect()
            self.camera.x, self.camera.y = self.player.x, self.player.y
            self.camera.update(0)

        self.clock = enter_params.get("clock")

        if self.clock is None:
            self.clock = Clock(settings.TIME_LEVELS)
            self.timer_stopped = False

            def countdown_timer():
                if not getattr(self.player, "game_frozen", False):
                    self.clock.count_down()
                    if 0 < self.clock.time <= 5:
                        settings.SOUNDS["timer"].play()
                    if self.clock.time == 0:
                        self.player.change_state("dead")
                        
            Timer.every(1, countdown_timer)
        else:
            Timer.resume()
        
        for item in self.game_level.items:
            if getattr(item, "frame_index", None) == 10:
                item.active = False

        self.target_scores = {1: settings.TARGET_SCORE, 2: settings.TARGET_SCORE2, 3: settings.TARGET_SCORE3}
        self.current_target = self.target_scores.get(self.level, settings.TARGET_SCORE)
        

    def update(self, dt: float) -> None:
        if self.player.is_dead:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            Timer.clear()
            self.state_machine.change("game_over", self.player)

        if self.player.score >= self.current_target and not self.special_event_triggered:
            self.special_event_triggered = True
            for item in self.game_level.items:
                if getattr(item, "frame_index", None) == 10:
                    item.active = True 
                    settings.SOUNDS["reveal"].play()
                else:
                    item.active = False
                    item.collidable = False
            self.player.game_frozen = True
           
            pygame.mixer.music.stop()
            pygame.mixer.music.load(settings.BASE_DIR / "assets" / "sounds" / "the_library_2.mp3") 
            pygame.mixer.music.play(-1)


        if getattr(self.player, "has_key", False):
            self.timer_stopped = True  
            self.player.change_state("idle")
            pygame.mixer.music.stop()
            settings.SOUNDS["reveal"].stop()
            self.state_machine.change(
                "victory", 
                player=self.player, 
                level=self.level,
                game_level=self.game_level,
                camera=self.camera
            )
            
            self.player.has_key = False 
            return


        self.player.update(dt)

        if self.player.y >= self.tilemap.pixel_height:
            self.player.change_state("dead")

        self.camera.update(dt)
        self.game_level.update(dt)

        for creature in self.game_level.creatures:
           if isinstance(creature.state_machine.current, SnailDieState):
                continue
           if self.player.collides(creature):
                if self.player.vy > 0 and (self.player.y + self.player.height) <= creature.y + (creature.height * 0.65):
                    self.player.vy = -180  
                    creature.change_state("die")  
                    self.player.score += settings.POINTS_KILL_ENEMY 
                else:
                    if not isinstance(creature.state_machine.current, SnailDieState):
                        self.player.change_state("dead")
            
        for item in self.game_level.items:
            if not item.active or not item.collidable:
                continue

            if self.player.collides(item):
                item.on_collide(self.player)
                item.on_consume(self.player)

    def render(self, surface: pygame.Surface) -> None:
        self.game_level.render(surface, self.camera)
        self.player.render(surface, self.camera)

        render_text(
            surface,
            f"Score: {self.player.score}/{self.current_target}",
            settings.FONTS["small"],
            5,
            5,
            (255, 255, 255),
            shadowed=True,
        )

        render_text(
            surface,
            f"Time: {self.clock.time}",
            settings.FONTS["small"],
            settings.VIRTUAL_WIDTH - 60,
            5,
            (255, 255, 255),
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "pause" and input_data.pressed:
            Timer.pause()
            self.state_machine.change(
                "pause",
                level=self.level,
                camera=self.camera,
                game_level=self.game_level,
                player=self.player,
                clock=self.clock,
                special_event_triggered=self.special_event_triggered,
            )
        else:
            self.player.on_input(input_id, input_data)
