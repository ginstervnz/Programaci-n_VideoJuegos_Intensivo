"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState for the game.
"""

import pygame

from gale.input_handler import InputData
from gale.state import BaseState, StateMachine

import settings
from src.definitions.entity import ENTITY_DEFS
from src.Player import Player
from src.states.entity import player as player_states
from src.world.Dungeon import Dungeon


class PlayState(BaseState):
    def enter(self) -> None:
        definition = ENTITY_DEFS["player"]

        self.player = Player(
            x=settings.VIRTUAL_WIDTH / 2 - 8,
            y=settings.VIRTUAL_HEIGHT / 2 - 11,
            width=16,
            height=22,
            walk_speed=definition["walk_speed"],
            # One heart == 2 health.
            health=6,
            animation_defs=definition["animations"],
            states={},
        )
        # Rendering/collision offset for the spaced sprite.
        self.player.offset_y = 5

        self.dungeon = Dungeon(self.player, on_game_over=self._on_game_over)

        self.player.state_machine.states = {
            "walk": lambda sm: player_states.PlayerWalkState(self.player, sm, self.dungeon),
            "idle": lambda sm: player_states.PlayerIdleState(self.player, sm, self.dungeon),
            "swing-sword": lambda sm: player_states.PlayerSwingSwordState(
                self.player, sm, self.dungeon
            ),
            "pot-lift": lambda sm: player_states.PlayerPotLiftState(
                self.player, sm, self.dungeon
            ),
            "pot-idle": lambda sm: player_states.PlayerPotIdleState(
                self.player, sm, self.dungeon
            ),
            "pot-walk": lambda sm: player_states.PlayerPotWalkState(
                self.player, sm, self.dungeon
            ),
            "shoot-bow": lambda sm: player_states.PlayerShootBowState(self.player, sm),
        }
        self.player.change_state("idle")

        pygame.mixer.music.load(settings.MUSIC["dungeon"])
        pygame.mixer.music.play(loops=-1)

    def exit(self) -> None:
        pygame.mixer.music.stop()

    def _on_game_over(self) -> None:
        self.state_machine.change("game-over", player=self.player)

    def update(self, dt: float) -> None:
        self.dungeon.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.dungeon.render(surface)

        # Draw player hearts, top of screen.
        health_left = self.player.health
        heart_frame = 1

        for i in range(3):
            if health_left > 1:
                heart_frame = 5
            elif health_left == 1:
                heart_frame = 3
            else:
                heart_frame = 1

            surface.blit(
                settings.TEXTURES["hearts"],
                (i * (settings.TILE_SIZE + 1), 2),
                settings.frame("hearts", heart_frame),
            )

            health_left -= 2

        if hasattr(self.dungeon.current_room, 'boss') and not self.dungeon.current_room.boss.dead:
            boss = self.dungeon.current_room.boss
            
            # Draw the boss health bar at the bottom of the screen
            bar_width = 100
            bar_height = 10
            x_pos = settings.VIRTUAL_WIDTH // 2 - bar_width // 2
            y_pos = settings.VIRTUAL_HEIGHT - 20 
            
            
            pygame.draw.rect(surface, (50, 50, 50), (x_pos, y_pos, bar_width, bar_height))
            health_percentage = boss.health / 5.0 # Max health is 5 hits
            fill_width = int(bar_width * health_percentage)
            
            if fill_width > 0:
                pygame.draw.rect(surface, (200, 0, 0), (x_pos, y_pos, fill_width, bar_height))
                
            pygame.draw.rect(surface, (255, 255, 255), (x_pos, y_pos, bar_width, bar_height), 1)

            cell_width = bar_width // 5
            for i in range(1, 5):
                line_x = x_pos + i * cell_width
                pygame.draw.line(surface, (255, 255, 255), (line_x, y_pos), (line_x, y_pos + bar_height - 1))

            # Draw the shield icon if the boss is immune
            shield_frame = 1 if boss.is_immune else 2
            shield_img = settings.TEXTURES["shield"]
            shield_rect = settings.frame("shield", shield_frame)
            surface.blit(shield_img, (x_pos - 20, y_pos - 2), shield_rect)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "interact" and input_data.pressed:
            # Trigger interaction with adjacent objects
            self.dungeon.current_room.interact_adjacent_object(self.player)
            
        elif input_id == "shoot" and input_data.pressed:
            # Trigger the bow shot if the player has collected it
            if getattr(self.player, 'has_bow', False) and getattr(self.player, 'bow_cooldown', 0) <= 0:
                self.player.change_state("shoot-bow")
                
        else:
            # Pass any other inputs to the player's state machine
            self.player.on_input(input_id, input_data)
