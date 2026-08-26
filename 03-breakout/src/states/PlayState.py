"""
ISPPV1 2023
Study Case: Breakout

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class to define the Play state.
"""

import random
import pygame
import math
from gale.factory import AbstractFactory
from gale.state import BaseState
from gale.input_handler import InputData
from gale.text import render_text

from src.powerups.Rocket import Rocket

import settings
import src.powerups

#Helpers
from src.utils.play_update_helpers import (
    update_visual_timers, process_sticky_and_arrow, 
    process_rocket_system, trigger_electro_storm, release_stuck_balls
)
from src.utils.play_render_helpers import (
    render_lightning_rays, render_electro_aura, is_paddle_visible, 
    render_stuck_arrow, apply_screen_shake, render_flash, render_hud
)


class PlayState(BaseState):
    def enter(self, **params: dict):
        self.level = params["level"]
        self.score = params["score"]
        self.lives = params["lives"]
        self.paddle = params["paddle"]
        self.paddle.vx = 0
        self.balls = params["balls"]
        self.brickset = params["brickset"]
        self.live_factor = params["live_factor"]
        self.points_to_next_live = params["points_to_next_live"]
        self.points_to_next_grow_up = (
            self.score
            + settings.PADDLE_GROW_UP_POINTS * (self.paddle.size + 1) * self.level
        )
        self.powerups = params.get("powerups", [])
        self.sticky_timer = params.get("sticky_timer", 0)
        self.radiactive_timer = params.get("radiactive_timer", 0)
        self.rocket_timer = params.get("rocket_timer", 0)
        self.rockets = params.get("rockets", [])
        self.arrow_angle = params.get("arrow_angle", 0)
        self.arrow_dir = params.get("arrow_dir", 1)  
        self.ARROW_ROTATE_SPEED = 120 
        self.ARROW_MAX_ANGLE = 60
     
        if not params.get("resume", False):
            self.balls[0].vx = random.randint(-80, 80)
            self.balls[0].vy = random.randint(-170, -100)
            settings.SOUNDS["paddle_hit"].play()
    
        self.powerups_abstract_factory = AbstractFactory("src.powerups")
        self.rocket_shots_left = params.get("rocket_shots_left", 0)
        self.screen_shake_timer = params.get("screen_shake_timer", 0)
        self.lightning_rays = params.get("lightning_rays", [])
        self.flash_timer = params.get("flash_timer", 0)



    def update(self, dt: float) -> None:
        self.paddle.update(dt)

        update_visual_timers(self, dt)
        process_sticky_and_arrow(self, dt)
        process_rocket_system(self, dt)

        # Simple Radiactive logic
        if self.radiactive_timer > 0:
            self.radiactive_timer -= dt
            if self.radiactive_timer <= 0:
                for ball in self.balls:
                    ball.is_radiactive = False

        for ball in self.balls:
            ball.update(dt)
            ball.solve_world_boundaries()

            if ball.collides(self.paddle):
                settings.SOUNDS["paddle_hit"].stop()
                settings.SOUNDS["paddle_hit"].play()
                ball_already_stuck = any(getattr(b, 'stuck', False) for b in self.balls)
                
                if getattr(self.paddle, 'is_sticky', False) and not ball_already_stuck:
                    ball.stuck = True
                    ball.stuck_offset = ball.x - self.paddle.x
                    ball.vx = 0
                    ball.vy = 0
                else:
                    ball.rebound(self.paddle) 
                    ball.push(self.paddle)

            if not ball.collides(self.brickset):
                continue

            brick = self.brickset.get_colliding_brick(ball.get_collision_rect())
            if brick is None:
                continue

            # thunderstorm!
            trigger_electro_storm(self, ball, brick)

            damage = settings.RADIACTIVE_DAMAGE if getattr(ball, 'is_radiactive', False) else 1
            for _ in range(damage):
                if not brick.broken:
                    brick.hit()
                    self.score += brick.score()
           
            ball.rebound(brick)

            # Lives and drops
            if self.score >= self.points_to_next_live:
                settings.SOUNDS["life"].play()
                self.lives = min(3, self.lives + 1)
                self.live_factor += 0.5
                self.points_to_next_live += settings.LIVE_POINTS_BASE * self.live_factor

            if self.score >= self.points_to_next_grow_up:
                settings.SOUNDS["grow_up"].play()
                self.points_to_next_grow_up += (
                    settings.PADDLE_GROW_UP_POINTS * (self.paddle.size + 1) * self.level
                )
                self.paddle.inc_size()

            if random.random() < settings.POSSIBILITY_POWERUP_SPAWN:
                r = brick.get_collision_rect() 
                available_powerups = [
                    "TwoMoreBall", 
                    "StickPowerUp", 
                    "RadiactivePowerUp", 
                    "RocketPowerUp", 
                    "LifePowerUp", 
                    "ElectroPowerUp"
                    ]
                powerup_type = random.choice(available_powerups)
                self.powerups.append( 
                    self.powerups_abstract_factory.get_factory(powerup_type).create(r.centerx - 8, r.centery - 8) 
                )


        self.balls = [ball for ball in self.balls if ball.active]
        self.brickset.update(dt)

        if not self.balls:
            self.lives -= 1
            if self.lives == 0:
                self.state_machine.change("game_over", score=self.score)
            else:
                self.paddle.dec_size()
                self.state_machine.change(
                    "serve", level=self.level, score=self.score, lives=self.lives,
                    paddle=self.paddle, brickset=self.brickset,
                    points_to_next_live=self.points_to_next_live, live_factor=self.live_factor,
                )

        for powerup in self.powerups:
            powerup.update(dt)
            if powerup.collides(self.paddle):
                powerup.take(self)
                
        self.powerups = [p for p in self.powerups if p.active]

        #Victory
        if all(b.broken for b in self.brickset.bricks.values()):
            self.state_machine.change(
                "victory", lives=self.lives, level=self.level, score=self.score,
                paddle=self.paddle, balls=self.balls, points_to_next_live=self.points_to_next_live,
                live_factor=self.live_factor,
            )

    def render(self, surface: pygame.Surface) -> None:
        world_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
        world_surf.blit(settings.TEXTURES["background"], (0, 0))

        self.brickset.render(world_surf)

        for rocket in getattr(self, 'rockets', []):
            rocket.render(world_surf)

        render_lightning_rays(world_surf, getattr(self, 'lightning_rays', []))

        if is_paddle_visible(self.paddle, getattr(self, 'rocket_timer', 0), getattr(self, 'sticky_timer', 0)):
            self.paddle.render(world_surf)
        
        for ball in self.balls:
            render_stuck_arrow(world_surf, ball, getattr(self, 'arrow_angle', 0))
            ball.render(world_surf)
            render_electro_aura(world_surf, ball)

        for powerup in getattr(self, 'powerups', []):
            powerup.render(world_surf)

        apply_screen_shake(surface, world_surf, getattr(self, 'screen_shake_timer', 0))
        render_flash(surface, getattr(self, 'flash_timer', 0))
        render_hud(surface, self.lives, self.score)
      

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "move_left":
            if input_data.pressed:
                self.paddle.vx = -settings.PADDLE_SPEED
            elif input_data.released and self.paddle.vx < 0:
                self.paddle.vx = 0
        elif input_id == "move_right":
            if input_data.pressed:
                self.paddle.vx = settings.PADDLE_SPEED
            elif input_data.released and self.paddle.vx > 0:
                self.paddle.vx = 0
                
        elif input_id == "pause" and input_data.pressed:
            if not release_stuck_balls(self):        
                self.state_machine.change(
                    "pause", 
                    level=self.level, 
                    score=self.score, 
                    lives=self.lives,
                    paddle=self.paddle, 
                    balls=self.balls, 
                    brickset=self.brickset,
                    points_to_next_live=self.points_to_next_live, 
                    live_factor=self.live_factor,
                    powerups=self.powerups, 
                    sticky_timer=self.sticky_timer,
                    radiactive_timer=self.radiactive_timer, 
                    rocket_timer=self.rocket_timer,
                    rockets=self.rockets, 
                    arrow_angle=self.arrow_angle, 
                    arrow_dir=self.arrow_dir,
                    rocket_shots_left=getattr(self, 'rocket_shots_left', 0),
                    screen_shake_timer=getattr(self, 'screen_shake_timer', 0),
                    lightning_rays=getattr(self, 'lightning_rays', []),
                    flash_timer=getattr(self, 'flash_timer', 0),
                )
                
        elif input_id == "shot" and input_data.pressed:
            if getattr(self.paddle, 'has_rockets', False) and len(self.rockets) == 0:
                settings.SOUNDS["shot_sound"].play()
                is_special = (self.rocket_shots_left == 1)
                
                left_x = self.paddle.x + 2
                right_x = self.paddle.x + self.paddle.width - 18 
                spawn_y = self.paddle.y - 8 
                
                self.rockets.append(Rocket(left_x, spawn_y, is_special))
                self.rockets.append(Rocket(right_x, spawn_y, is_special))
                
                self.rocket_shots_left -= 1
                if self.rocket_shots_left <= 0:
                    self.paddle.has_rockets = False