import pygame
from src.states.entity.BaseEntityState import BaseEntityState
import settings

class PlayerShootBowState(BaseEntityState):
    def enter(self, *args, **kwargs) -> None:
        self.entity.change_animation(f"idle-{self.entity.direction}")
        self.timer = 0.0
        self.shoot_delay = 0.1 
        self.entity.bow_cooldown = 0.8

        if getattr(self.entity, 'has_bow', False) and hasattr(self.entity, 'bow'):
            arrow_x = self.entity.x
            arrow_y = self.entity.y
            
            if self.entity.direction == "left":
                arrow_x -= settings.TILE_SIZE
            elif self.entity.direction == "right":
                arrow_x += settings.TILE_SIZE
            elif self.entity.direction == "up":
                arrow_y -= settings.TILE_SIZE
            elif self.entity.direction == "down":
                arrow_y += settings.TILE_SIZE
                
            new_arrow = self.entity.bow.fire(arrow_x, arrow_y, self.entity.direction)
            
            if not hasattr(self.entity, 'pending_projectiles'):
                self.entity.pending_projectiles = []
            self.entity.pending_projectiles.append(new_arrow)

    def update(self, dt: float) -> None:
        self.timer += dt
        if self.timer >= self.shoot_delay:
            self.entity.change_state("idle")

    def render(self, surface: pygame.Surface) -> None:
        #  Draw the player
        anim = self.entity.current_animation
        self.entity.render_sprite(surface, anim.texture_id, anim.get_current_frame())

        # Draw the bow on top of the player
        bow_texture = settings.TEXTURES["bow"]
        bow_x = self.entity.x
        bow_y = self.entity.y + 4 # Slight offset to match the player's hands
        
        # Rotate or flip the bow based on the direction
        if self.entity.direction == "right":
            bow_image = bow_texture
            bow_x += 8
        elif self.entity.direction == "left":
            bow_image = pygame.transform.flip(bow_texture, True, False)
            bow_x -= 8
        elif self.entity.direction == "up":
            bow_image = pygame.transform.rotate(bow_texture, 90)
            bow_y -= 10
        elif self.entity.direction == "down":
            bow_image = pygame.transform.rotate(bow_texture, -90)
            bow_y += 10

        surface.blit(bow_image, (bow_x, bow_y))