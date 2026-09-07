import pygame
import random
from src.Entity import Entity
from gale.animation import Animation
from src.states.entity.BaseEntityState import BaseEntityState
from src.Fireball import Fireball
import settings
import math


class BossWalkState(BaseEntityState):
    def enter(self, *args, **kwargs) -> None:
        self.entity.change_animation("walk-down")
        self.entity.texture_id = "boss-walk"
        self.timer = 0.0
        if self.entity.health <= 2:
            self.walk_time = random.uniform(0.5, 1.2)
        else:
            self.walk_time = random.uniform(1.0, 2.5)
        self.entity.direction = random.choice(["left", "right", "up", "down"])
        
    def process_ai(self, room, dt: float) -> None:
        self.timer += dt
        
        if self.entity.direction == "left":
            self.entity.x -= self.entity.walk_speed * dt
        elif self.entity.direction == "right":
            self.entity.x += self.entity.walk_speed * dt
        elif self.entity.direction == "up":
            self.entity.y -= self.entity.walk_speed * dt
        elif self.entity.direction == "down":
            self.entity.y += self.entity.walk_speed * dt
            
        margin_x = settings.TILE_SIZE * 2
        margin_y = settings.TILE_SIZE * 3
        
        left_bound = settings.MAP_RENDER_OFFSET_X + margin_x
        right_bound = settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH * settings.TILE_SIZE - self.entity.width - margin_x
        top_bound = settings.MAP_RENDER_OFFSET_Y + margin_y
        bottom_bound = settings.MAP_RENDER_OFFSET_Y + settings.MAP_HEIGHT * settings.TILE_SIZE - self.entity.height - margin_y

        self.entity.x = max(left_bound, min(self.entity.x, right_bound))
        self.entity.y = max(top_bound, min(self.entity.y, bottom_bound))
        
        if self.timer >= self.walk_time and room.player.health > 0:
            self.entity.change_state("attack")

class BossHitState(BaseEntityState):
    def enter(self, *args, **kwargs) -> None:
        
        hit_def = self.entity.anim_defs["hit-down"]
        self.entity.animations["hit-down"] = Animation(
            hit_def["frames"], hit_def["interval"], loops=hit_def.get("loops")
        )
        self.entity.change_animation("hit-down")
        self.entity.texture_id = "boss-hit"
        self.timer = 0.0

    def process_ai(self, room, dt: float) -> None:
        self.timer += dt
        if self.timer >= 0.3:
            self.entity.change_state("idle")

class BossDeathState(BaseEntityState):
    def enter(self, *args, **kwargs) -> None:
        
        death_def = self.entity.anim_defs["death-down"]
        self.entity.animations["death-down"] = Animation(
            death_def["frames"], death_def["interval"], loops=death_def.get("loops")
        )
        self.entity.change_animation("death-down")
        self.entity.texture_id = "boss-death"
        self.entity.is_immune = True 
        self.timer = 0.0
        
    def process_ai(self, room, dt: float) -> None:
        self.timer += dt
        if self.timer >= 1.2:
            if hasattr(self.entity.current_animation, 'interval'):
                self.entity.current_animation.interval = 9999

class BossIdleState(BaseEntityState):
    def enter(self, *args, **kwargs) -> None:
        self.entity.change_animation("idle-down")
        self.entity.texture_id = "boss-idle"
        self.timer = 0.0
        
    def process_ai(self, room, dt: float) -> None:
        self.timer += dt
        wait_time = 0.5 if self.entity.health <= 2 else 1.5
        if self.timer >= wait_time:
            self.entity.change_state("walk")

class BossAttackState(BaseEntityState):
    def enter(self, *args, **kwargs) -> None:
        
        atk_def = self.entity.anim_defs["attack-down"]
        self.entity.animations["attack-down"] = Animation(
            atk_def["frames"], atk_def["interval"], loops=atk_def.get("loops")
        )
        self.entity.change_animation("attack-down")
        self.entity.texture_id = "boss-attack"
                
        self.fired = False
        self.attack_timer = 0.0
        self.attack_pattern = random.choice(["single", "spread", "nova"])
        
    def process_ai(self, room, dt: float) -> None:
        self.attack_timer += dt
        
        if self.attack_timer >= 0.64 and not self.fired:
            self.fired = True
            origin_x = self.entity.x + 4
            origin_y = self.entity.y - 24
            target_x = room.player.x + room.player.width / 2
            target_y = room.player.y + room.player.height / 2
            base_angle = math.atan2(target_y - origin_y, target_x - origin_x)
            
            if self.attack_pattern == "single":
                fireball = Fireball(origin_x, origin_y, target_x, target_y)
                fireball.is_enemy_projectile = True 
                room.projectiles.append(fireball)
                
            elif self.attack_pattern == "spread":
                offsets = [-0.4, -0.15, 0.15, 0.4]
                for offset in offsets:
                    new_angle = base_angle + offset
                    new_target_x = origin_x + math.cos(new_angle) * 100
                    new_target_y = origin_y + math.sin(new_angle) * 100
                    
                    fireball = Fireball(origin_x, origin_y, new_target_x, new_target_y)
                    fireball.is_enemy_projectile = True 
                    room.projectiles.append(fireball)
                    
            elif self.attack_pattern == "nova":
                for i in range(8):
                    angle = i * (math.pi / 4)
                    new_target_x = origin_x + math.cos(angle) * 100
                    new_target_y = origin_y + math.sin(angle) * 100
                    
                    fireball = Fireball(origin_x, origin_y, new_target_x, new_target_y)
                    fireball.is_enemy_projectile = True 
                    room.projectiles.append(fireball)
    
        if getattr(self.entity.current_animation, 'times_played', 0) > 0:
            self.entity.fireball_cooldown = settings.FIREBALL_COOLDOWN  # Cooldown before the next attack
            self.entity.change_state("idle")

class Boss(Entity):
    def __init__(self, x: float, y: float, definition: dict):

        if "hit-down" not in definition["animations"]:
            definition["animations"]["hit-down"] = {"texture": "boss-hit", "frames": [1, 2, 3], "interval": 0.1, "loops": 1}
        if "death-down" not in definition["animations"]:
            definition["animations"]["death-down"] = {"texture": "boss-death", "frames": [1, 2, 3, 4, 5, 6, 7, 8], "interval": 0.15, "loops": 1}
        

        self.anim_defs = definition["animations"]

        
        super().__init__(
            x=x, y=y, 
            width=26, height=19,
            walk_speed=definition["walk_speed"], health=5, 
            animation_defs=definition["animations"], states={}
        )
        self.is_immune = True
        self.immunity_timer = 0.0
        self.fireball_cooldown = 2.0
        self.direction = "down"

        self.state_machine.states = {
            "idle": lambda sm: BossIdleState(self, sm),
            "walk": lambda sm: BossWalkState(self, sm),
            "attack": lambda sm: BossAttackState(self, sm),
            "hit": lambda sm: BossHitState(self, sm),
            "death": lambda sm: BossDeathState(self, sm)
        }

    def process_ai(self, room, dt: float) -> None:
        self.state_machine.current.process_ai(room, dt)

    def collides(self, target) -> bool:
        is_player = type(target).__name__ == "Player"
        if not is_player and self.is_immune:
            return False
        if isinstance(target, pygame.Rect):
            target_rect = target
        else:
            target_rect = target.get_collision_rect()
            
        return self.get_collision_rect().colliderect(target_rect)

    def update(self, dt: float) -> None:
        super().update(dt) 
        
        self.invulnerable = self.is_immune
            
        if not self.is_immune:
            self.immunity_timer -= dt
            if self.immunity_timer <= 0:
                self.is_immune = True

    def render(self, surface: pygame.Surface, adjacent_offset_x: float = 0, adjacent_offset_y: float = 0) -> None:
        anim = getattr(self, 'current_animation', None)
        if anim:
            texture_id = getattr(self, 'texture_id', "boss-idle")
            
            if hasattr(anim, 'get_current_frame'):
                frame_idx = anim.get_current_frame()
            elif hasattr(anim, 'current_frame'):
                frame_idx = anim.current_frame
            else:
                frame_idx = 1
                
            max_frames = len(settings.FRAMES.get(texture_id, []))
            if max_frames > 0:
                frame_idx = max(1, min(frame_idx, max_frames)) 
                
                image = settings.TEXTURES[texture_id]
                frame_rect = settings.frame(texture_id, frame_idx)
                
                visual_x = self.x - 35 + adjacent_offset_x
                visual_y = self.y - 40 + adjacent_offset_y
                
                surface.blit(image, (visual_x, visual_y), frame_rect)

        # Draw the collision rectangle for debugging purposes
        #rect = pygame.Rect(self.x + adjacent_offset_x, self.y + adjacent_offset_y, self.width, self.height)
        #pygame.draw.rect(surface, (255, 0, 0), rect, 1)

    def damage(self, amount: int) -> None:
        if not self.is_immune:
            self.health -= amount
            self.is_immune = True
            self.immunity_timer = 0.0 
            settings.SOUNDS["hit_boss"].play()
            if self.health <= 2:
                self.walk_speed = 35 
            
            if self.health <= 0:
                self.change_state("death")
            else:
                if type(self.state_machine.current).__name__ != "BossAttackState":
                    self.change_state("hit")