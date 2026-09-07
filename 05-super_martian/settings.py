"""
ISPPV1 2023
Study Case: Super Martian (Platformer)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the game settings that include the association of the
inputs with an their ids, constants of values to set up the game, sounds,
textures, frames, and fonts.
"""

import pathlib

import pygame

from gale import frames
from gale import input_handler

input_handler.InputHandler.set_keyboard_action(input_handler.KEY_ESCAPE, "quit")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_p, "pause")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_RETURN, "enter")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_KP_ENTER, "enter")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_RIGHT, "move_right")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_d, "move_right")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_LEFT, "move_left")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_a, "move_left")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_SPACE, "jump")
input_handler.InputHandler.set_mouse_click_action(input_handler.MOUSE_BUTTON_1, "jump")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_UP, "up")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_DOWN, "down")

TITLE = "Super Martian"

# Size we want to emulate
VIRTUAL_WIDTH = 400
VIRTUAL_HEIGHT = 192

# Size of our actual window
WINDOW_WIDTH = VIRTUAL_WIDTH * 4
WINDOW_HEIGHT = VIRTUAL_HEIGHT * 4

PLAYER_SPEED = 80

GRAVITY = 980

CAMERA_FOLLOW_RATE = 8.0

NUM_LEVELS = 3
TIME_LEVELS = 80
POINTS_KILL_ENEMY = 40
TARGET_SCORE = 250
TARGET_SCORE2 = 500
TARGET_SCORE3 = 1000

BASE_DIR = pathlib.Path(__file__).parent

TILEMAPS = {
    i: str(BASE_DIR / "assets" / "tilemaps" / f"level{i}.json")
    for i in range(1, NUM_LEVELS + 1)
}

TEXTURES = {
    "tiles": pygame.image.load(BASE_DIR / "assets" / "graphics" / "tileset.png"),
    "martian": pygame.image.load(BASE_DIR / "assets" / "graphics" / "martian.png"),
    "creatures": pygame.image.load(BASE_DIR / "assets" / "graphics" / "creatures.png"),
    "new_coins": pygame.image.load(BASE_DIR / "assets" / "graphics" / "MorningSheet.png"),
    "slime_sheet_v2": pygame.image.load(BASE_DIR / "assets" / "graphics" / "slime_sheet_v2.png"),
    "slime_sheet_v4": pygame.image.load(BASE_DIR / "assets" / "graphics" / "slime_sheet_v4.png"),
    "skeleton_sheet": pygame.image.load(BASE_DIR / "assets" / "graphics" / "skeleton_sheet.png"),
    "goblin_sheet_1": pygame.image.load(BASE_DIR / "assets" / "graphics" / "goblin_sheet_1.png"),
}

#Auxiliar funtion for sprites with margin
def get_spaced_frames(surface, width, height, spacing):
    frames_list = []   
    for y in range(0, surface.get_height(), height + spacing):
        for x in range(0, surface.get_width(), width + spacing):
            if x + width <= surface.get_width() and y + height <= surface.get_height():
                frames_list.append(pygame.Rect(x, y, width, height))
    return frames_list


FRAMES = {
    "tiles": frames.generate_frames(TEXTURES["tiles"], 16, 16),
    "martian": frames.generate_frames(TEXTURES["martian"], 16, 20),
    "creatures": frames.generate_frames(TEXTURES["creatures"], 16, 16),
    "new_coins": frames.generate_frames(TEXTURES["new_coins"], 16, 16),
    "slime_sheet_v2": get_spaced_frames(TEXTURES["slime_sheet_v2"], 16, 16, 2),
    "slime_sheet_v4": get_spaced_frames(TEXTURES["slime_sheet_v4"], 16, 16, 2),
    "skeleton_sheet": get_spaced_frames(TEXTURES["skeleton_sheet"], 16, 16, 2),
    "goblin_sheet_1": get_spaced_frames(TEXTURES["goblin_sheet_1"], 16, 16, 2),
}

SOUNDS = {
    "pickup_coin": pygame.mixer.Sound(
        BASE_DIR / "assets" / "sounds" / "pickup_coin.wav"
    ),
    "jump": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "jump.wav"),
    "timer": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "timer.wav"),
    "count": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "count.wav"),
    "punch": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "punch_block.mp3"),
    "pick_key": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "pick_key.mp3"),
    "dead_enemy": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "dead_enemy.mp3"),
    "reveal": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "reveal.mp3"),
    "select": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "pickup_coin.wav"),
    "victory": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "victory.mp3"),
    "game_over": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "game-over.wav"),
}

SOUNDS["pickup_coin"].set_volume(0.5)

FONTS = {
    "small": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "font.ttf", 8),
    "medium": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "font.ttf", 16),
}
