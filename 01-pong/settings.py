"""
ISPPV1 2023
Study Case: Pong

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the game settings that include the association of the
inputs with an their ids, constants of values to set up the game, sounds,
and fonts.
"""

from pathlib import Path

import pygame

from gale import input_handler

input_handler.InputHandler.set_keyboard_action(input_handler.KEY_ESCAPE, "quit")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_RETURN, "confirm")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_w, "p1_up")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_s, "p1_down")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_UP, "p2_up")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_DOWN, "p2_down")

# Additional keyboard actions to toggle AI control for players
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_z, "toggle_ai_p1")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_x, "toggle_ai_p2")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_c, "toggle_ai_both")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_v, "toggle_no_ai") 
TITLE = "Pong"

# Size of our actual window
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Size we are trying to emulate (the original's "table")
VIRTUAL_WIDTH = 432
VIRTUAL_HEIGHT = 243

PADDLE_WIDTH = 5
PADDLE_HEIGHT = 20
PADDLE_X_OFFSET = 10
PADDLE_Y_OFFSET = 30
PADDLE_SPEED = 200

BALL_SIZE = 4

MID_LINE_WIDTH = 2

MAX_POINTS = 5

BASE_DIR = Path(__file__).parent

SOUNDS = {
    "paddle_hit": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "paddle_hit.wav"),
    "wall_hit": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "wall_hit.wav"),
    "score": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "score.wav"),
    "music": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "Final_Match_Point.mp3"),
}

FONTS = {
    "score": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "font.ttf", 32),
    "large": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "font.ttf", 16),
    "medium": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "font.ttf", 14),
}

COLOR_BACKGROUND = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)

#New constants for AI-controlled paddles and color red for IA controlled paddles
PLAYER1_AI_DEFAULT = False
PLAYER2_AI_DEFAULT = True
AI_VISION_P1 = 0.75  
AI_VISION_P2 = 0.25
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
