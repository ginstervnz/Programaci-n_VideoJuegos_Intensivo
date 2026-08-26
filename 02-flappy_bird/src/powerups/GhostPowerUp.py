import pygame
import settings
from .PowerUp import PowerUp

class GhostPowerUp(PowerUp):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y)
        self.image = settings.TEXTURES["powerup"]
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def get_rect(self) -> pygame.Rect:
        margen_x = 14 
        margen_y = 16 
        return pygame.Rect(
            round(self.x) + margen_x, 
            round(self.y) + margen_y, 
            self.width - (margen_x * 2), 
            self.height - (margen_y * 2)
        )

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.image, (round(self.x), round(self.y)))

    def take(self, play_state) -> None:
        settings.SOUNDS["powerup"].play() 
        if not play_state.bird.is_ghost:
            pygame.mixer.music.pause()
            settings.SOUNDS["ghost_form"].play(loops=-1)
        play_state.bird.is_ghost = True
        play_state.ghost_timer = settings.TIME_BIRD_FORM
        play_state.grace_timer = settings.TIME_INVULNERABLE
        self.active = False