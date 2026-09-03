import pygame
import math
import settings
from src.GameObject import GameObject

class Fireball:
    def __init__(self, x: float, y: float, target_x: float, target_y: float) -> None:
        from src.definitions.game_objects import GAME_OBJECT_DEFS
        
        self.angle = math.atan2(target_y - y, target_x - x)
        self.obj = GameObject(GAME_OBJECT_DEFS["fireball"], x + 16, y + 16)
        self.dead = False
        # Set the speed of the fireball
        speed = 80 
        self.vx = math.cos(self.angle) * speed
        self.vy = math.sin(self.angle) * speed
        self.frame_timer = 0.0
        self.current_frame = 1

    def get_collision_rect(self) -> pygame.Rect:
        rect = self.obj.get_collision_rect()
        rect.inflate_ip(-4, -4) 
        return rect

    def collides(self, target) -> bool:
        return self.get_collision_rect().colliderect(target.get_collision_rect())

    def update(self, dt: float) -> None:
        if self.dead:
            return
            
        self.obj.update(dt)
        self.obj.x += self.vx * dt
        self.obj.y += self.vy * dt

        self.frame_timer += dt
        if self.frame_timer >= 0.1:
            self.frame_timer = 0.0
            self.current_frame += 1
            if self.current_frame > 6:
                self.current_frame = 1


        left_limit = settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE
        right_limit = settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH * settings.TILE_SIZE - self.obj.width
        top_limit = settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE
        bottom_limit = settings.MAP_RENDER_OFFSET_Y + settings.MAP_HEIGHT * settings.TILE_SIZE - self.obj.height

        if (self.obj.x <= left_limit or self.obj.x >= right_limit or 
            self.obj.y <= top_limit or self.obj.y >= bottom_limit):
            self.dead = True

    def render(self, surface: pygame.Surface, offset_x: float = 0, offset_y: float = 0) -> None:

        texture_id = "fireball" 
        image = settings.TEXTURES[texture_id]
        
        frame_rect = settings.frame(texture_id, self.current_frame)
        frame_surf = image.subsurface(frame_rect)

        degrees = math.degrees(self.angle)
        rotated_surf = pygame.transform.rotate(frame_surf, -degrees)

        center_x = self.obj.x + self.obj.width / 2 + offset_x
        center_y = self.obj.y + self.obj.height / 2 + offset_y
        rotated_rect = rotated_surf.get_rect(center=(center_x, center_y))

        surface.blit(rotated_surf, rotated_rect.topleft)