"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)
"""
from typing import Any
import pygame
from gale.state import BaseState
import settings
from src.gui.Menu import Menu
from src.states.game.BattleMessageState import BattleMessageState

class GuildState(BaseState):
    def enter(self, party) -> None:
        self.party = party
        self.menu = None
        
        self.enemies = []
        self.particle_effects = []
        
        settings.stop_music("town")
        settings.play_music("gremio")

        self.render_chars = []
        start_x = 30
        y = settings.VIRTUAL_HEIGHT - 90
        for i, char in self.party.characters.items():
            if not char.dead:
                char.x = start_x + (i * 25)
                char.y = y
                char.direction = "right"
                char.change_state("idle")
                self.render_chars.append(char)

        self._show_message("Welcome to the Guild! How can I help you?", self._show_menu)

    def exit(self) -> None:
        settings.stop_music("gremio")
        settings.play_music("town")
        
        leader = self.party.first_alive()
        if leader:
            self.party.set_position(4, 7, "up")

    def _show_message(self, text, callback) -> None:
        self.state_machine.push(
            BattleMessageState(self.state_machine),
            battle_state=self, 
            message=text,
            on_close=callback
        )

    def _show_menu(self) -> None:
        items = [
            (f"Revive Ally ({self.party.revives_left})", self._revive_ally),
            (f"Rest Party ({self.party.rests_left})", self._rest_party),
            ("Leave", self._leave)
        ]
        self.menu = Menu(
            settings.VIRTUAL_WIDTH - 180, settings.VIRTUAL_HEIGHT - 90,
            180, 90, items=items, font=settings.FONTS["small"]
        )

    def _revive_ally(self) -> None:
        self.menu = None
        if self.party.revives_left <= 0:
            settings.SOUNDS["error"].play()
            self._show_message("We can't provide more revives right now.", self._show_menu)
            return

        dead_chars = [c for c in self.party.characters.values() if c.dead]
        if not dead_chars:
            settings.SOUNDS["error"].play()
            self._show_message("Everyone is already alive and well!", self._show_menu)
            return

        char = dead_chars[0]
        char.dead = False
        char.current_hp = 5
        char.turn_timer = 0
        if hasattr(char, "rest_time"): 
            char.rest_time = 0
        
        self.party.revives_left -= 1
        settings.SOUNDS["powerup"].play()
        
        self.render_chars = []
        for i, c in self.party.characters.items():
            if not c.dead:
                c.x = 30 + (i * 25)
                c.y = settings.VIRTUAL_HEIGHT - 90
                c.direction = "right"
                c.change_state("idle")
                self.render_chars.append(c)
        
        self._show_message(f"{char.name} has been revived with 5 HP!", self._show_menu)

    def _rest_party(self) -> None:
        self.menu = None
        if self.party.rests_left <= 0:
            settings.SOUNDS["error"].play()
            self._show_message("The resting rooms are full.", self._show_menu)
            return

        for char in self.party.characters.values():
            if not char.dead:
                char.turn_timer = 0
                if hasattr(char, "rest_time"): 
                    char.rest_time = 0

        self.party.rests_left -= 1
        settings.SOUNDS["powerup"].play()
        self._show_message("The party is fully rested!", self._show_menu)

    def _leave(self) -> None:
        self.menu = None
        self._show_message("Safe travels!", self._do_leave)

    def _do_leave(self) -> None:
        from src.states.game.FadeInState import FadeInState
        from src.states.game.FadeOutState import FadeOutState
        from src.states.game.ShowTextState import ShowTextState
        
        def on_fade_in_complete() -> None:
            self.state_machine.pop()
            self.exit()

            def on_fade_out_complete() -> None:
                self.state_machine.push(
                    ShowTextState(self.state_machine),
                    color=(0, 0, 0),
                    text="center",
                    on_complete=lambda: None
                )

            self.state_machine.push(
                FadeOutState(self.state_machine),
                color=(0, 0, 0),
                time=0.5,
                on_complete=on_fade_out_complete
            )

        self.state_machine.push(
            FadeInState(self.state_machine),
            color=(0, 0, 0),
            time=0.5,
            on_complete=on_fade_in_complete
        )

    def update(self, dt: float) -> None:
        if self.menu:
            self.menu.update(dt)
        for char in self.render_chars:
            char.update(dt)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if self.menu:
            if not input_data.pressed: return
            if input_id == "move_up": self.menu.navigate((0, -1))
            elif input_id == "move_down": self.menu.navigate((0, 1))
            elif input_id == "enter": self.menu.confirm()

    def render(self, surface: pygame.Surface) -> None:
        sheet = settings.TEXTURES["guild-interior"]
        BLOCK_SIZE = 64 
        
        wall_rect  = pygame.Rect(63, 575, BLOCK_SIZE, BLOCK_SIZE) 
        floor_rect = pygame.Rect(384, 704, BLOCK_SIZE, BLOCK_SIZE)
        rug_rect    = pygame.Rect(1042, 722, 85, 85)
        decoration1 = pygame.Rect(1548, 522, 39, 35)
        for py in range(0, settings.VIRTUAL_HEIGHT, BLOCK_SIZE):
            for px in range(0, settings.VIRTUAL_WIDTH, BLOCK_SIZE):
                # If we are in the top half of the screen, draw the wall
                if py < settings.VIRTUAL_HEIGHT // 2:
                    surface.blit(sheet, (px, py), wall_rect)
                # If we are in the bottom half, draw the floor
                else:
                    surface.blit(sheet, (px, py), floor_rect)
        
        # Place the rug in the center of the floor
        surface.blit(sheet, (settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT - 60), rug_rect)
        
        # Place a decoration on the left side
        surface.blit(sheet, (40, 50), decoration1)
        surface.blit(sheet,(settings.VIRTUAL_WIDTH-140,50), decoration1)

        for char in self.render_chars:
            char.render(surface)
            
        npc_x = settings.VIRTUAL_WIDTH - 40
        npc_y = settings.VIRTUAL_HEIGHT - 90
        surface.blit(settings.TEXTURES["npc-female"], (npc_x, npc_y), settings.frame("npc-female", 11))

        if self.menu:
            self.menu.render(surface)