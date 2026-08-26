import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings

class ServeState(BaseState):

    def __init__(self, state_machine) -> None:
        super().__init__(state_machine)
        self.options = ["Normal", "Hard"] #Two opcions
        self.selected_option = 0

    def enter(self, **enter_params: dict) -> None:
        self.world = enter_params.get("world")
        self.selected_option = 0

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_data.pressed:
            if input_id == "down":
                settings.SOUNDS["change_select"].play()
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif input_id == "up":
                settings.SOUNDS["change_select"].play()
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif input_id == "confirm":
                mode = self.options[self.selected_option].lower()
                settings.SOUNDS["select"].play()
                self.state_machine.change("count_down", mode=mode, world=self.world)

    def update(self, dt: float) -> None:
        if self.world:
            self.world.update(dt)
        pass

    def render(self, surface: pygame.Surface) -> None:
        if self.world:
            self.world.render(surface)
        else:
            surface.blit(settings.TEXTURES["background"], (0, 0))
            surface.blit(settings.TEXTURES["ground"], (0, settings.VIRTUAL_HEIGHT - settings.GROUND_HEIGHT))
        #Render mini menu
        render_text(surface, "Select Difficulty", settings.FONTS["title"], settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 3, settings.COLOR_WHITE, center=True, shadowed=True)
        #Opciones
        start_y = (settings.VIRTUAL_HEIGHT // 2) + 20
        for i, option in enumerate(self.options):
            color = settings.COLOR_YELLOW if i == self.selected_option else settings.COLOR_WHITE
            render_text(surface, option, settings.FONTS["sub_title"], settings.VIRTUAL_WIDTH // 2, start_y + (i * 30), color, center=True, shadowed=True)