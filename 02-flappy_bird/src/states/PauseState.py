"""
Actividad 2 Ricardo Felzani Olmedillo

Curso: ISPPV1 I2026

"""

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings


class PauseState(BaseState):
    options = ["Resume", "Restart", "Quit"]

    def enter(self, **enter_params: dict) -> None:
        self.bird = enter_params["bird"]
        self.world = enter_params["world"]
        self.score = enter_params["score"]
        self.mode = enter_params.get("mode", "hard")
        self.ghost_timer = enter_params.get("ghost_timer", 0.0)
        self.grace_timer = enter_params.get("grace_timer", 0.0)
        self.selected_option = 0

    def on_input(self, input_id: str, input_data: InputData) -> None:
       
            if input_id == "down" and input_data.pressed:
                settings.SOUNDS["score"].play()
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif input_id == "up" and input_data.pressed:
                settings.SOUNDS["score"].play()
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif input_id == "confirm" and input_data.pressed:
                if self.selected_option == 0:  # Resume
                    self.state_machine.change(
                        "count_down",
                        bird=self.bird,
                        world=self.world,
                        score=self.score,
                        mode=self.mode,
                        ghost_timer=self.ghost_timer,
                        grace_timer=self.grace_timer
                    )
                elif self.selected_option == 1:  # Restart
                    settings.SOUNDS["ghost_form"].stop()
                    pygame.mixer.music.load(settings.MUSIC["normal_theme"])
                    pygame.mixer.music.play(loops=-1)
                    self.state_machine.change("count_down", mode=self.mode)
                elif self.selected_option == 2:  # Quit
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
        self.bird.render(surface)
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["flappy"], 
            20, 10, 
            settings.COLOR_WHITE, 
            shadowed=True
            )
        render_text(
            surface, 
            f"{self.mode.capitalize()}", 
            settings.FONTS["flappy"], settings.VIRTUAL_WIDTH - 100,
            10, 
            settings.COLOR_WHITE, 
            shadowed=True
            )
        render_text(
            surface, 
            "PAUSE", 
            settings.FONTS["flappy"], 
            settings.VIRTUAL_WIDTH // 2, 
            settings.VIRTUAL_HEIGHT // 3, 
            settings.COLOR_WHITE, 
            center=True
            )
        start_y = (settings.VIRTUAL_HEIGHT // 2) + 20
        for i, option in enumerate(self.options):
            color = settings.COLOR_YELLOW if i == self.selected_option else settings.COLOR_WHITE
            render_text(
                surface, 
                option, 
                settings.FONTS["medium"], 
                settings.VIRTUAL_WIDTH // 2, 
                start_y + (i * 30), 
                color, 
                center=True
                )