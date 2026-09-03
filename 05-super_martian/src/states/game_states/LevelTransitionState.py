import pygame
from gale.state import BaseState
from gale.timer import Timer
from gale.text import render_text
import settings

class LevelTransitionState(BaseState):
    def enter(self, **enter_params) -> None:
        self.level = enter_params.get("level", 1)
        self.saved_score = enter_params.get("saved_score", 0)
        self.saved_coins = enter_params.get("saved_coins", None)
        self.text_alpha = 0
        Timer.tween(1.0, [(self, {"text_alpha": 255})], on_finish=self.hold_screen)
        
    def hold_screen(self) -> None:
        Timer.after(1.0, self.start_level)
        
    def start_level(self) -> None:
        self.state_machine.change(
            "play", 
            level=self.level,
            saved_score=self.saved_score,
            saved_coins=self.saved_coins
        )

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0)) 
        
        temp_surface = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        render_text(
            temp_surface,
            f"World - {self.level}",
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH // 2,
            settings.VIRTUAL_HEIGHT // 2,
            (255, 255, 255),
            center=True,
            shadowed=True
        )
        
        temp_surface.set_alpha(int(self.text_alpha))
        surface.blit(temp_surface, (0, 0))