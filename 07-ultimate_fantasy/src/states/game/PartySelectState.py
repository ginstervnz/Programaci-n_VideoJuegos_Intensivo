from typing import Any
import pygame
from gale.state import BaseState
import settings
from src.gui.Menu import Menu
from src.gui.Panel import Panel
from src.definitions.entity import DEFAULT_CHARACTER_FRAME

class PartySelectState(BaseState):
    def enter(self, play_state: Any, on_select=None, on_cancel=None) -> None:
        self.play_state = play_state
        self.party = play_state.world.party
        self.on_select = on_select
        self.on_cancel = on_cancel 

        self.characters_list = list(self.party.characters.values())

        items = []
        for character in self.characters_list:
            status_icon = " (DEAD)" if character.dead else ""
            display_name = f"{character.name}{status_icon}"
            
            if self.on_select:
                callback = lambda c=character: self._trigger_selection(c)
            else:
                callback = lambda c=character: self._show_profile(c)
                
            items.append((display_name, callback))

        menu_width = 130
        menu_height = 32 + (len(items) * 16)
        
        self.menu = Menu(
            x=settings.VIRTUAL_WIDTH / 2 - menu_width - 10,
            y=settings.VIRTUAL_HEIGHT / 2 - menu_height / 2,
            width=menu_width,
            height=menu_height,
            items=items,
            font=settings.FONTS["small"],
        )

        self.preview_panel = Panel(
            x=settings.VIRTUAL_WIDTH / 2 + 10,
            y=settings.VIRTUAL_HEIGHT / 2 - 32,
            width=64,
            height=64,
        )
        
    def _trigger_selection(self, character: Any) -> None:
        self.state_machine.pop() 
        self.on_select(character) 

    def _show_profile(self, character: Any) -> None:
        from src.states.game.CharacterProfileState import CharacterProfileState
        self.state_machine.pop() 
        
        self.state_machine.push(
            CharacterProfileState(self.state_machine),
            character=character,
            play_state=self.play_state
        )

    def update(self, dt: float) -> None:
        self.menu.update(dt)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if not input_data.pressed:
            return

        if input_id == "move_up":
            self.menu.navigate((0, -1))
        elif input_id == "move_down":
            self.menu.navigate((0, 1))
        elif input_id == "enter":
            self.menu.confirm()
        elif input_id == "space" or input_id == "escape":
            self.state_machine.pop()

            if self.on_cancel:
                self.on_cancel()
            elif not self.on_select:
                from src.states.game.PauseMenuState import PauseMenuState
                self.state_machine.push(
                    PauseMenuState(self.state_machine), 
                    play_state=self.play_state
                )

    def render(self, surface: pygame.Surface) -> None:
        self.menu.render(surface)
        self.preview_panel.render(surface)

        selected_index = self.menu.list_view.selected_index
        character = self.characters_list[selected_index]
        texture = character.texture
        frame_rect = settings.frame(texture, DEFAULT_CHARACTER_FRAME)

        sprite_x = self.preview_panel.x + self.preview_panel.width / 2 - frame_rect.width / 2
        sprite_y = self.preview_panel.y + self.preview_panel.height / 2 - frame_rect.height / 2

        if character.dead:
            ghost_image = pygame.Surface((frame_rect.width, frame_rect.height), pygame.SRCALPHA)
            ghost_image.blit(settings.TEXTURES[texture], (0, 0), frame_rect)
            ghost_image.set_alpha(100) 
            surface.blit(ghost_image, (sprite_x, sprite_y))
            
            font = settings.FONTS["small"]
            dead_text = font.render("DEAD", True, (255, 50, 50))
            text_x = self.preview_panel.x + self.preview_panel.width / 2 - dead_text.get_width() / 2
            surface.blit(dead_text, (text_x, self.preview_panel.y + 5))
        else:
            surface.blit(settings.TEXTURES[texture], (sprite_x, sprite_y), frame_rect)