"""
ISPPV1 2023
Study Case: Pong

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class ServeState.
"""

import random

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings
from src.rendering import render_table


class ServeState(BaseState):
    def enter(self, pong) -> None:
        self.pong = pong

    def render(self, surface: pygame.Surface) -> None:
        pong = self.pong
        render_table(surface,pong)

        is_both_ai = pong.player1.is_ai and pong.player2.is_ai #Logic for Color IAs and Human
        is_none_ai = not pong.player1.is_ai and not pong.player2.is_ai
        color_z = pong.player1.ai_color if (pong.player1.is_ai and not pong.player2.is_ai) else settings.COLOR_WHITE
        color_x = pong.player2.ai_color if (pong.player2.is_ai and not pong.player1.is_ai) else settings.COLOR_WHITE
        color_c = settings.COLOR_YELLOW if is_both_ai else settings.COLOR_WHITE
        color_v = settings.COLOR_GRAY if is_none_ai else settings.COLOR_WHITE

        render_text(
            surface,
            "Press enter to serve",
            settings.FONTS["large"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 2 - 40,
            settings.COLOR_WHITE,
            center=True,
        )
        render_text(
            surface,
            "Press Z for Player 1 AI",
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH / 2,
            (settings.VIRTUAL_HEIGHT / 2), 
            color_z,
            center=True,
        )
        render_text(
            surface,
            "Press X for Player 2 AI",
            settings.FONTS["medium"], 
            settings.VIRTUAL_WIDTH / 2,
            (settings.VIRTUAL_HEIGHT / 2) + 20,
            color_x,
            center=True,
        )
        render_text(
            surface,
            "Press C to toggle BOTH AI",
            settings.FONTS["medium"], 
            settings.VIRTUAL_WIDTH / 2,
            (settings.VIRTUAL_HEIGHT / 2) + 40,
            color_c,
            center=True,
        )
        render_text(
            surface,
            "Press V No IA",
            settings.FONTS["medium"], 
            settings.VIRTUAL_WIDTH / 2,
            (settings.VIRTUAL_HEIGHT / 2) + 60, 
            color_v,
            center=True,
        )


    def on_input(self, input_id: str, input_data: InputData) -> None:
        pong = self.pong
        if input_id == "confirm" and input_data.pressed:
        
            pong.ball.vx = random.randint(140, 199)

            if pong.serving_player == 2:
                pong.ball.vx *= -1

            pong.ball.vy = random.randint(-50, 49)
            self.state_machine.change("play", pong=pong)
            return

        if input_data.pressed: # Switching to pressed state to ensure that the AI toggle only happens on key press
            if input_id == "toggle_ai_p1":
                pong.player1.is_ai = True
                pong.player2.is_ai = False
                pong.player1.color = pong.player1.ai_color
                pong.player2.color = settings.COLOR_WHITE
                
            elif input_id == "toggle_ai_p2":
                pong.player2.is_ai = True
                pong.player1.is_ai = False
                pong.player2.color = pong.player2.ai_color
                pong.player1.color = settings.COLOR_WHITE
                
            elif input_id == "toggle_ai_both":
                pong.player1.is_ai = True
                pong.player2.is_ai = True
                pong.player1.color = pong.player1.ai_color
                pong.player2.color = pong.player2.ai_color
            elif input_id == "toggle_no_ai":
                pong.player1.is_ai = False
                pong.player2.is_ai = False
                pong.player1.color = settings.COLOR_WHITE
                pong.player2.color = settings.COLOR_WHITE    