"""
ISPPV1 2023
Study Case: Throw a Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState, ported from main.script: the
whole per-frame update/input loop -- aiming, panning, flinging the bird,
camera follow-and-zoom, and idle-detection to reset the bird back to the
slingshot once a shot has settled.

Deviation from the Lua source: main.script disables the parrot's
collisionobject at rest and re-enables it only once flung, so gravity
and everything else leaves it alone until it is thrown.
gale.physics.Body has no enable/disable toggle for an existing fixture,
so instead the bird is held in place by brute force every frame it is
neither being aimed nor already in flight (_hold_bird_at_rest): its
position/velocity are pinned back to the slingshot each update(), which
cancels out whatever one frame of gravity would have done. The bird
remains a normal dynamic body throughout (nothing in the level ever
reaches the slingshot's position anyway), it is just re-pinned faster
than it can visibly fall.
"""

import math

import pygame

from gale.camera import Camera
from gale.input_handler import InputData
from gale.physics.world import World
from gale.state import BaseState
from gale.text import render_text
import random
import settings
from src.entity.Bird import Bird
from src.world.Level import Level

# How close (world pixels) a press has to land to the bird to start
# aiming instead of panning the camera.
AIM_GRAB_RADIUS = 50

# The pull-back vector is clamped to this length (world pixels) both
# while aiming (how far the bird can be dragged back) and when computing
# the launch impulse on release.
MAX_PULL_DISTANCE = 150

# Scales the (clamped) pull-back vector into a launch impulse. Not a
# port of the original's `950` (a force applied for a single Defold
# physics step, at Defold's own physics.scale) -- chosen instead, by
# testing actual throws, so a full pull-back (MAX_PULL_DISTANCE) launches
# the bird fast enough to comfortably clear the gap and reach the tower
# under gale's default gravity, factoring in the energy the bird's own
# high friction/low restitution shed on its first bounce.
#
# This is the only tuning number that matters here, regardless of the
# bird's mass: gale.physics.Body.apply_impulse(ix, iy) divides by
# pixels_per_meter before hand it to Box2D, and Box2D's resulting
# delta-v is impulse / mass -- so passing an impulse of
# `pull * FLING_IMPULSE_SCALE * mass` (mirroring the Lua source's own
# `direction * 950 * parrot_mass`, force proportional to mass) makes
# mass cancel out of the result: launch speed is just
# `pull * FLING_IMPULSE_SCALE`.
#
# 10.5 (barely cleared the gap) was bumped to 16.0 (comfortably punched
# into the tower) per feedback that throws felt too weak -- then walked
# back to the average of the two, 13.25, per feedback that 16.0 then felt
# too strong.
FLING_IMPULSE_SCALE = 13.25

# A shot is considered "settled" once the bird's linear/angular velocity
# has been below these thresholds for IDLE_FRAMES_LIMIT consecutive
# frames (~1.6s at 60fps) -- ported from main.script, retuned for gale's
# pixel/physics scale (angular velocity here is radians/second, not
# Defold's units).
IDLE_LINEAR_SPEED_THRESHOLD = 30
IDLE_ANGULAR_SPEED_THRESHOLD = 0.3
IDLE_FRAMES_LIMIT = 100

CAMERA_FOLLOW_RATE = 6.0
CAMERA_ZOOM_LERP_RATE = 3.0
CAMERA_ZOOM_MIN = 1.0
CAMERA_ZOOM_MAX = 1.5
CAMERA_PAN_MARGIN = 300

HUD_TEXT = "Drag the bird to aim and release to fling. Drag elsewhere to pan."


class PlayState(BaseState):
    def enter(self) -> None:
        self.world = World(gravity=settings.GRAVITY)

        self.level = Level(self.world)
        color = random.choice(["red", "blue", "black", "yellow"])
        self.birds = [Bird(self.world, self.level.bird_start.x, self.level.bird_start.y, color=color)]

        self.camera = Camera(settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
        self.camera.x, self.camera.y = self.birds[0].position
        self.camera_target = pygame.Vector2(self.camera.x, self.camera.y)
        self.camera.follow(self.camera_target, rate=CAMERA_FOLLOW_RATE)
        # Mirrors main.script's self.camera_zoom (ranges 1..1.5, bigger
        # means "farther away"); gale's own Camera.zoom is the inverse
        # (bigger means "closer"), so it is always set to 1/this ratio.
        self.camera_zoom_ratio = 1.0
        self.camera.zoom = 1.0

        self.aiming = False
        self.panning = False
        self.flinging = False
        self.manual_cam = False
        self.manual_cam_index = 0
        self.idle_frames = 0

        self.bomb_primed = False
        self.bomb_timer = 0.0
        self.particles = []
        self.screen_shake = 0.0

        self.pressed_position = pygame.Vector2()
        self.pressed_camera_target = pygame.Vector2()
        self.aim_offset = pygame.Vector2()


        self.is_dashing = False
        self.is_yellow_charging = False
        self.yellow_charge_timer = 0.0
        self.yellow_target_pos = None
        self.yellow_charge_pos = None

        self.victory_timer = 3.0

        if "music" in settings.SOUNDS:
            settings.SOUNDS["music"].stop()
            settings.SOUNDS["music"].play(loops=-1)

    def fixed_update(self) -> None:
        # Driven by gale.game.Game's own accumulator (added in gale
        # 1.10.0) instead of calling self.world.update(dt) here, which
        # would otherwise run a second, redundant accumulator on top of
        # World's own.
        self.world.fixed_update()
        self.level.fixed_update()

    def update(self, dt: float) -> None:
        for block in self.level.blocks:
            if block.destroyed and not getattr(block, "fx_played", False):
                block.fx_played = True 
                
                is_alien = block.archetype.startswith("alien")
                
                if is_alien and "alien_death" in settings.SOUNDS:
                    settings.SOUNDS["alien_death"].play()
                elif not is_alien and "block_break" in settings.SOUNDS:
                    settings.SOUNDS["block_break"].play()
                    
                num_particles = random.randint(5, 8)
                for _ in range(num_particles):
                    p_angle = random.uniform(0, math.pi * 2)
                    speed = random.uniform(30, 80)
                    
                    if is_alien:
                        color = random.choice([(100, 255, 100), (50, 200, 50), (200, 50, 50)])
                    else:
                        color = random.choice([(139, 69, 19), (160, 82, 45), (105, 105, 105)])
                        
                    self.particles.append({
                        'pos': pygame.Vector2(block.body.position.x, block.body.position.y),
                        'vel': pygame.Vector2(math.cos(p_angle)*speed, math.sin(p_angle)*speed),
                        'timer': random.uniform(0.2, 0.4),
                        'color': color
                    })

        self.level.update(dt)

        if self.level.all_enemies_defeated:
            self.victory_timer -= dt
            if self.victory_timer <= 0:
                self.state_machine.change("victory")
            

        if self.bomb_primed:
            self.bomb_timer -= dt
            if self.birds:
                b = self.birds[0]
                angle = b.body.angle
                offset_x = b.radius * math.sin(angle)
                offset_y = -b.radius * math.cos(angle)
                
                self.particles.append({
                    'pos': pygame.Vector2(b.position.x + offset_x, b.position.y + offset_y),
                    'vel': pygame.Vector2(random.uniform(-20, 20), random.uniform(-40, -10)),
                    'timer': random.uniform(0.1, 0.3),
                    'color': random.choice([(255, 150, 0), (255, 50, 0), (100, 100, 100)])
                })
            if self.bomb_timer <= 0:
                self._explode_bomb()

        if getattr(self, "is_yellow_charging", False) and self.birds:
            b = self.birds[0]
            if b.has_collided:
                self.is_yellow_charging = False
            else:
                self.yellow_charge_timer -= dt
                
                b.body.position = self.yellow_charge_pos
                b.body.velocity = (0, 0)
                b.body.angular_velocity = 0.0
                self.idle_frames = 0 
                diff = self.yellow_target_pos - b.position
                b.body.angle = math.atan2(diff.y, diff.x)
                
                self.particles.append({
                    'pos': pygame.Vector2(b.position.x + random.uniform(-20, 20), b.position.y + random.uniform(-20, 20)),
                    'vel': pygame.Vector2(0, 0),
                    'timer': 0.1,
                    'color': random.choice([(255, 255, 255), (255, 255, 0)])
                })
                
                if self.yellow_charge_timer <= 0:
                    self.is_yellow_charging = False
                    self.is_dashing = True
                    if "dash" in settings.SOUNDS:
                        settings.SOUNDS["dash"].play()
                    
                    direction = diff.normalize() if diff.length() > 0 else pygame.Vector2(1, 0)
                    
                    dash_power = 3500 * b.mass
                    b.body.apply_impulse(direction.x * dash_power, direction.y * dash_power)

        for p in reversed(self.particles):
            p['pos'] += p['vel'] * dt
            p['timer'] -= dt
            if p['timer'] <= 0:
                self.particles.remove(p)
        self.screen_shake = max(0, self.screen_shake - dt * 2)
            
        for b in self.birds:
            b.check_collision()

            if b.is_split and not b.has_collided:
                self.particles.append({
                    'pos': pygame.Vector2(b.position.x, b.position.y),
                    'vel': pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10)),
                    'timer': random.uniform(0.2, 0.4),
                    'color': (150, 220, 255) 
                })
                
            if getattr(self, "is_dashing", False) and b.color == "yellow":
                if not b.has_collided:
                    self.particles.append({
                        'pos': pygame.Vector2(b.position.x, b.position.y),
                        'vel': pygame.Vector2(random.uniform(-15, 15), random.uniform(-15, 15)),
                        'timer': random.uniform(0.1, 0.3),
                        'color': random.choice([(255, 255, 0), (255, 200, 0)]) # Amarillo y Naranja
                    })
                else:
                    self.is_dashing = False

        if self.flinging:
            if self.birds:
                if not self.manual_cam:
                    fastest = max(self.birds, key=lambda b: b.body.velocity.length_squared())
                    self.camera_target.update(fastest.position)
                else:
                    sorted_birds = sorted(self.birds, key=lambda b: b.body.velocity.length_squared())
                    if len(sorted_birds) > 0: 
                        target = sorted_birds[self.manual_cam_index % len(sorted_birds)]
                        self.camera_target.update(target.position)
                
            self._update_idle()
        elif self.aiming:
            self._hold_bird_while_aiming()
        else:
            self._hold_bird_at_rest()

        self._update_zoom(dt)
        self.camera.update(dt)

    def _hold_bird_at_rest(self) -> None:
        self.birds[0].reset()

    def _hold_bird_while_aiming(self) -> None:
        # world.update(dt) above still steps gravity on the bird every
        # frame regardless of aiming state (gale.physics.Body has no
        # enable/disable toggle -- see the module docstring), and
        # _on_touch_motion only fires on mouse-motion *events*, not every
        # frame. Without re-pinning here too, any frame with no fresh
        # motion event lets gravity accumulate velocity that then snaps
        # the bird around erratically the moment position gets set again.
        # Re-applying the held offset and zeroing velocity every frame
        # keeps the bird glued to the mouse the whole time it is aiming.
        self.birds[0].body.position = self.birds[0].initial_position - self.aim_offset
        self.birds[0].body.velocity = (0, 0)
        self.birds[0].body.angular_velocity = 0.0

    def _update_idle(self) -> None:
        all_idle = True
        for b in self.birds:
            if b.body.velocity.length() >= IDLE_LINEAR_SPEED_THRESHOLD or abs(b.body.angular_velocity) >= IDLE_ANGULAR_SPEED_THRESHOLD:
                all_idle = False
                break

        if all_idle:
            self.idle_frames += 1
            if self.idle_frames > IDLE_FRAMES_LIMIT:
                self.flinging = False
                self.idle_frames = 0
                
                for b in self.birds:
                    self.world.destroy_body(b.body)
                
                color = random.choice(["red", "blue", "black", "yellow"])
                self.birds = [Bird(self.world, self.level.bird_start.x, self.level.bird_start.y, color=color)]
                self.manual_cam = False
                self.is_dashing = False
                self.is_yellow_charging = False
                self.camera_target.update(self.birds[0].position)
        else:
            self.idle_frames = 0

    def _update_zoom(self, dt: float) -> None:
        if not self.birds:
            return
            
        distance = abs(self.birds[0].position.x - self.birds[0].initial_position.x)
        reach = max(1.0, self.birds[0].initial_position.x)
        
        target_ratio = max(
            CAMERA_ZOOM_MIN, min(CAMERA_ZOOM_MAX, math.sqrt(distance / reach))
        )
        factor = 1.0 - math.exp(-CAMERA_ZOOM_LERP_RATE * dt)
        self.camera_zoom_ratio += (target_ratio - self.camera_zoom_ratio) * factor
        self.camera.zoom = 1.0 / self.camera_zoom_ratio

    def render(self, surface: pygame.Surface) -> None:
        surface.fill(settings.BG_COLOR)
        shake_x = random.uniform(-1, 1) * self.screen_shake * 50 if self.screen_shake > 0 else 0
        shake_y = random.uniform(-1, 1) * self.screen_shake * 50 if self.screen_shake > 0 else 0
        self.camera.x += shake_x
        self.camera.y += shake_y
        
        self.level.render(surface, self.camera)
        
        for b in self.birds:
            b.render(surface, self.camera)
            
        for p in self.particles:
            screen_pos = self.camera.world_to_screen(p['pos'])
            pygame.draw.circle(surface, p['color'], screen_pos, 4)

        if self.aiming:
            self._render_pull_line(surface)
        render_text(surface, HUD_TEXT, settings.FONTS["small"], 10, 10, (70, 55, 40))
        
        self.camera.x -= shake_x
        self.camera.y -= shake_y

        enemies_text = f"Left enemies: {self.level.enemies_alive}"
        render_text(surface, enemies_text, settings.FONTS["medium"], settings.VIRTUAL_WIDTH - 190, 10, (200, 50, 50))

    def _render_pull_line(self, surface: pygame.Surface) -> None:
        start = self.camera.world_to_screen(self.birds[0].initial_position)
        end = self.camera.world_to_screen(self.birds[0].position)
        pygame.draw.line(surface, (110, 75, 40), start, end, 3)

    def _split_bird(self) -> None:
        original = self.birds[0]
        v = original.body.velocity
        pos = original.position
        color = original.color
        self.world.destroy_body(original.body)
        self.birds.clear()
        
        angle = math.pi / 6
        b_center = Bird(self.world, pos.x, pos.y, is_split=True, color=color)
        b_center.body.velocity = (v.x, v.y)
        
        
        v1_x = v.x * math.cos(angle) - v.y * math.sin(angle)
        v1_y = v.x * math.sin(angle) + v.y * math.cos(angle)
        b1 = Bird(self.world, pos.x, pos.y, is_split=True, color=color)
        b1.body.velocity = (v1_x, v1_y)
        
        
        v2_x = v.x * math.cos(-angle) - v.y * math.sin(-angle)
        v2_y = v.x * math.sin(-angle) + v.y * math.cos(-angle)
        b2 = Bird(self.world, pos.x, pos.y, is_split=True, color=color)
        b2.body.velocity = (v2_x, v2_y)
        
        self.birds.extend([b_center, b1, b2])
        
        for _ in range(20):
            p_angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 150)
            self.particles.append({
                'pos': pygame.Vector2(pos.x, pos.y),
                'vel': pygame.Vector2(math.cos(p_angle)*speed, math.sin(p_angle)*speed),
                'timer': random.uniform(0.3, 0.6),
                'color': (100, 200, 255) 
            })

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if getattr(input_data, "pressed", False):
            if input_id == "split" and self.flinging and len(self.birds) == 1 and not self.birds[0].has_collided:
                if self.birds[0].color == "blue":
                    settings.SOUNDS["split"].play()
                    self._split_bird()
                elif self.birds[0].color == "black" and not self.bomb_primed:
                    self.bomb_primed = True
                    self.bomb_timer = 3.0
                elif self.birds[0].color == "yellow" and not getattr(self, "is_dashing", False) and not getattr(self, "is_yellow_charging", False):
                    b_pos = self.birds[0].position
                    nearest_enemy = None
                    min_dist = float('inf')
                    
                    for block in self.level.blocks:
                        if block.archetype.startswith("alien") and not block.destroyed:
                            dist = (block.body.position - b_pos).length_squared()
                            if dist < min_dist:
                                min_dist = dist
                                nearest_enemy = block
                                
                    if nearest_enemy:
                        self.yellow_target_pos = pygame.Vector2(nearest_enemy.body.position.x, nearest_enemy.body.position.y)
                    else:
                        self.yellow_target_pos = pygame.Vector2(b_pos.x + 1000, b_pos.y)

                    self.is_yellow_charging = True
                    self.yellow_charge_timer = 1.0
                    self.yellow_charge_pos = pygame.Vector2(b_pos.x, b_pos.y)
                    
                    if "stretch" in settings.SOUNDS:
                        settings.SOUNDS["stretch"].play()
                    
            elif input_id == "cam_slower" and self.flinging:
                self.manual_cam = True
                self.manual_cam_index -= 1
            elif input_id == "cam_faster" and self.flinging:
                self.manual_cam = True
                self.manual_cam_index += 1

        if input_id == "touch":
            self._on_touch(input_data)
        elif input_id == "touch_motion":
            self._on_touch_motion(input_data)

    def _mouse_to_virtual(self, position) -> pygame.Vector2:
        scale_x = settings.VIRTUAL_WIDTH / settings.WINDOW_WIDTH
        scale_y = settings.VIRTUAL_HEIGHT / settings.WINDOW_HEIGHT
        return pygame.Vector2(position[0] * scale_x, position[1] * scale_y)

    def _on_touch(self, input_data: InputData) -> None:
        position = self._mouse_to_virtual(input_data.position)
        if input_data.pressed:
            self.pressed_position = position
            world_position = pygame.Vector2(self.camera.screen_to_world(position))

            if not self.flinging and (world_position - self.birds[0].position).length() < AIM_GRAB_RADIUS:
                self.aiming = True
                self.aim_offset = pygame.Vector2()
                if "stretch" in settings.SOUNDS:
                    settings.SOUNDS["stretch"].play()
            else:
                self.panning = True
                self.pressed_camera_target = pygame.Vector2(self.camera_target)
        elif input_data.released:
            if self.aiming:
                self._fling()
            self.aiming = False
            self.panning = False

    def _fling(self) -> None:
        pull = self.birds[0].initial_position - self.birds[0].position
        if pull.length() < 5:
            self.birds[0].reset()
            return
        # Scaled by the bird's own mass so it cancels out of the
        # resulting delta-v -- see the FLING_IMPULSE_SCALE docstring.
        scale = FLING_IMPULSE_SCALE * self.birds[0].mass
        self.birds[0].body.apply_impulse(pull.x * scale, pull.y * scale)
        self.flinging = True
        self.idle_frames = 0

    def _explode_bomb(self) -> None:
        self.bomb_primed = False
        settings.SOUNDS["bom"].play()
        bomb_pos = self.birds[0].position
        
        for block in self.level.blocks:
            if block.destroyed: continue
            diff = block.body.position - bomb_pos
            dist = diff.length()
            if 0 < dist < 400:
                strength = (1 - (dist / 400)) * block.mass * 2000 
                force_dir = diff.normalize()
                block.body.apply_impulse(force_dir.x * strength, force_dir.y * strength)
                
        for _ in range(60):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(100, 500)
            self.particles.append({
                'pos': pygame.Vector2(bomb_pos.x, bomb_pos.y),
                'vel': pygame.Vector2(math.cos(angle)*speed, math.sin(angle)*speed),
                'timer': random.uniform(0.5, 1.5),
                'color': random.choice([(255,100,0), (200,50,0), (50,50,50)])
            })
            
        self.world.destroy_body(self.birds[0].body)
        self.birds = []
        self.screen_shake = 0.8
        self.idle_frames = -120


    def _on_touch_motion(self, input_data: InputData) -> None:
        if not (self.aiming or self.panning):
            return

        position = self._mouse_to_virtual(input_data.position)
        # Screen-space delta since the press, converted to world units by
        # dividing out the camera's current zoom.
        screen_delta = self.pressed_position - position
        world_delta = screen_delta / self.camera.zoom

        if self.aiming:
            if world_delta.length() > MAX_PULL_DISTANCE:
                world_delta.scale_to_length(MAX_PULL_DISTANCE)

            # Just remember the offset; update()'s _hold_bird_while_aiming
            # re-applies it (and zeroes velocity) every frame, not only on
            # the frames a motion event happens to arrive.
            self.aim_offset = world_delta
        elif self.panning:
            target = self.pressed_camera_target + world_delta
            left, right = self.level.ground_x_range
            target.x = max(
                left - CAMERA_PAN_MARGIN, min(right + CAMERA_PAN_MARGIN, target.x)
            )
            self.camera_target.update(target)
