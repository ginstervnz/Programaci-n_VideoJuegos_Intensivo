import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings

class GameOverState(BaseState):
    def __init__(self, state_machine) -> None:
        super().__init__(state_machine)
        self.options = ["Retry", "Quit"]
        self.selected_option = 0
        self.score = 0
        self.death_sound = "explosion"
        self.phase = "hit_sound"
        self.timer = 0.0

    def enter(self, **enter_params: dict) -> None:
        self.score = enter_params.get("score", 0)
        self.death_sound = enter_params.get("death_sound", "explosion")
        self.selected_option = 0
        pygame.mixer.music.pause()
        self.phase = "hit_sound"
        self.timer = settings.SOUNDS[self.death_sound].get_length() + 0.2

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_data.pressed:
            if input_id == "down":
                settings.SOUNDS["change_select"].play()
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif input_id == "up":
                settings.SOUNDS["change_select"].play()
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif input_id == "confirm":
                settings.SOUNDS["select"].play()
                settings.SOUNDS["game_over"].stop()
                settings.SOUNDS["hurt"].stop()
                settings.SOUNDS[self.death_sound].stop()
                
                if self.selected_option == 0:  # Retry
                    pygame.mixer.music.load(settings.MUSIC["normal_theme"])
                    pygame.mixer.music.play(loops=-1)
                    self.state_machine.change("serve")
                elif self.selected_option == 1:  # Quit
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                    
    def update(self, dt: float) -> None:
        if self.phase == "hit_sound":
            self.timer -= dt
            if self.timer <= 0:
                settings.SOUNDS["game_over"].play()
                self.timer = settings.SOUNDS["game_over"].get_length()
                self.phase = "game_over_sound"
                
        elif self.phase == "game_over_sound":
            self.timer -= dt
            if self.timer <= 0:
                pygame.mixer.music.unpause()
                self.phase = "music_resumed"

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(settings.TEXTURES["background"], (0, 0))
        surface.blit(settings.TEXTURES["ground"], (0, settings.VIRTUAL_HEIGHT - settings.GROUND_HEIGHT))

        render_text(surface, "GAME OVER", settings.FONTS["title"], settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 3 - 20, settings.COLOR_WHITE, center=True, shadowed=True)
        render_text(surface, f"Final Score: {self.score}", settings.FONTS["flappy"], settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 3 + 40, settings.COLOR_WHITE, center=True, shadowed=True)

        start_y = (settings.VIRTUAL_HEIGHT // 2) + 50
        for i, option in enumerate(self.options):
            color = settings.COLOR_YELLOW if i == self.selected_option else settings.COLOR_WHITE
            render_text(surface, option, settings.FONTS["sub_title"], settings.VIRTUAL_WIDTH // 2, start_y + (i * 30), color, center=True, shadowed=True)