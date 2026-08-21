import pygame
import settings

class PowerUp:
    def __init__(self, x: float, y: float) -> None:
        self.image = settings.TEXTURES["powerup"]
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.in_play = True 
        self.x = x
        self.y = y

    def get_rect(self) -> pygame.Rect:
        margen_x = 8  
        margen_y = 10
        return pygame.Rect(round(self.x) + margen_x, round(self.y) + margen_y, self.width - (margen_x*2), self.height  - (margen_y * 2))

    def collides(self, rect: pygame.Rect) -> bool:
        return self.get_rect().colliderect(rect)

    def update(self, dt: float) -> None:
        self.x += -settings.MAIN_SCROLL_SPEED * dt

    def is_out_of_game(self) -> bool:
        return self.x < -self.width

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.image, (round(self.x), round(self.y)))