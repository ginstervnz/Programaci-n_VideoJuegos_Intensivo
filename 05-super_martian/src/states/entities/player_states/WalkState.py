"""
ISPPV1 2023
Study Case: Super Martian (Platformer)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class WalkState for player.
"""

from gale.input_handler import InputData

import settings
from src.states.entities.BaseEntityState import BaseEntityState


class WalkState(BaseEntityState):
    def enter(self, direction: str) -> None:
        self.entity.flipped = direction == "left"
        self.entity.vx = settings.PLAYER_SPEED
        if self.entity.flipped:
            self.entity.vx *= -1
        self.entity.change_animation("walk")

    def update(self, dt: float) -> None:
        standing_on_block = False
        
        for item in self.entity.game_level.items:
            if getattr(item, "frame_index", None) == 10 and item.active:
                if self.entity.x + self.entity.width > item.x and self.entity.x < item.x + item.width:
                    if abs((self.entity.y + self.entity.height) - item.y) <= 5:
                        standing_on_block = True
                        break

        if not self.entity.on_ground and not standing_on_block:
            self.entity.change_state("fall")

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "move_left":
            if input_data.pressed:
                self.entity.vx = -settings.PLAYER_SPEED
                self.entity.flipped = True
            elif input_data.released and self.entity.vx <= 0:
                self.entity.change_state("idle")

        elif input_id == "move_right":
            if input_data.pressed:
                self.entity.vx = settings.PLAYER_SPEED
                self.entity.flipped = False
            elif input_data.released and self.entity.vx >= 0:
                self.entity.change_state("idle")
        elif input_id == "jump" and input_data.pressed:
            self.entity.change_state("jump")
