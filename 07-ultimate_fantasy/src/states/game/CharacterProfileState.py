from typing import Any
import pygame
from gale.state import BaseState
import settings
from src.gui.Panel import Panel
from src.definitions.entity import DEFAULT_CHARACTER_FRAME

class CharacterProfileState(BaseState):
    def enter(self, character: Any, play_state: Any) -> None:
        self.character = character
        self.play_state = play_state
        self.actions = character.actions 
        self.selected_action = 0
        
        self.panel = Panel(
            x=settings.VIRTUAL_WIDTH / 2 - 120,
            y=settings.VIRTUAL_HEIGHT / 2 - 95, 
            width=240,
            height=190
        )

    def on_input(self, input_id: str, input_data: Any) -> None:
        if not input_data.pressed: return

        if input_id == "space" or input_id == "escape":
            settings.SOUNDS["blip"].stop()
            settings.SOUNDS["blip"].play()
            self.state_machine.pop()

            from src.states.game.PartySelectState import PartySelectState
            self.state_machine.push(
                PartySelectState(self.state_machine),
                play_state=self.play_state
            )
            
        elif input_id == "move_up":
            self.selected_action = max(0, self.selected_action - 1)
            settings.SOUNDS["blip"].stop(); settings.SOUNDS["blip"].play()
        elif input_id == "move_down":
            self.selected_action = min(len(self.actions) - 1, self.selected_action + 1)
            settings.SOUNDS["blip"].stop(); settings.SOUNDS["blip"].play()
            
        elif input_id == "enter":
            if self.character.dead:
                settings.SOUNDS["error"].play()
                return
            action = self.actions[self.selected_action]
            if "Heal" in action["name"]:
                self._try_heal(action)
            else:
                settings.SOUNDS["error"].play() 

    def _try_heal(self, action: Any) -> None:
       
        if self.character.rest_time >= 15:
            settings.SOUNDS["error"].play()
            return 
            
        if action["require_target"]:
            from src.states.game.PartySelectState import PartySelectState
            self.state_machine.pop()
            self.state_machine.push(
                PartySelectState(self.state_machine),
                play_state=self.play_state,
                on_select=lambda target: self._apply_heal(action, target),
                on_cancel=lambda: self._return_to_profile()
            )

        else:
            targets = list(self.play_state.world.party.characters.values())
            alive_targets = [t for t in targets if not t.dead]
            action["func"](self.character, alive_targets, action.get("strength"))
            settings.SOUNDS["heal"].play()
            cost = action.get("fatigue_cost", 5)
            self.character.rest_time += cost

    def _apply_heal(self, action: Any, target: Any) -> None:
        if target.dead:
            settings.SOUNDS["error"].play()
        else:
            action["func"](self.character, target, action.get("strength"))
            settings.SOUNDS["heal"].play()
            cost = action.get("fatigue_cost", 5)
            self.character.rest_time += cost
            
        self._return_to_profile()

    def _return_to_profile(self) -> None:
        self.state_machine.push(
            CharacterProfileState(self.state_machine),
            character=self.character,
            play_state=self.play_state
        )

    def update(self, dt: float) -> None: pass

    def render(self, surface: pygame.Surface) -> None:
        self.panel.render(surface)

        font_medium = settings.FONTS["medium"]
        font_small = settings.FONTS["small"]
        
        start_x = self.panel.x + 15
        start_y = self.panel.y + 15

        status_text = "Dead" if self.character.dead else "Alive"
        name_surface = font_medium.render(f"{self.character.name} - {status_text}", True, (255, 255, 255))
        surface.blit(name_surface, (start_x, start_y))

        stats = [
            f"Level: {self.character.level}",
            f"EXP: {int(self.character.current_exp)} / {int(self.character.exp_to_level)}",
            f"HP: {self.character.current_hp} / {self.character.hp}",
            f"Rest Time: {self.character.rest_time} / 15", 
            f"Attack: {self.character.attack}",
            f"Speed: {int(self.character.speed)}",
            f"Defense: {self.character.defense}",
            f"Magic: {self.character.magic}",
        ]

        y_offset = start_y + 30
        for stat_line in stats:
            stat_surface = font_small.render(stat_line, True, (255, 255, 255))
            surface.blit(stat_surface, (start_x + 10, y_offset))
            y_offset += 16

        sprite_x = self.panel.x + self.panel.width - 60
        sprite_y = self.panel.y + 35
        
        texture = self.character.texture
        surface.blit(settings.TEXTURES[texture], (sprite_x, sprite_y), settings.frame(texture, DEFAULT_CHARACTER_FRAME))

        action_y = sprite_y + 45
        for i, action in enumerate(self.actions):
            is_heal = "Heal" in action["name"]
            
           
            text_surf = font_small.render(action["name"], True, (255, 255, 255))
            if not is_heal:
                text_surf.set_alpha(90) 
                
            text_x = sprite_x - 10 
            surface.blit(text_surf, (text_x, action_y + (i * 18)))
            
            if i == self.selected_action:
                surface.blit(settings.TEXTURES["cursor-right"], (text_x - 18, action_y + (i * 18)))