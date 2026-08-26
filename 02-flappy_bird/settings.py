"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the game settings that include the association of the
inputs with an their ids, constants of values to set up the game, sounds,
textures, and fonts.
"""

from pathlib import Path

import pygame

from gale import input_handler

input_handler.InputHandler.set_keyboard_action(input_handler.KEY_ESCAPE, "quit")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_RETURN, "confirm")
input_handler.InputHandler.set_mouse_click_action(input_handler.MOUSE_BUTTON_1, "jump")

#New input actions for the game
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_UP, "up")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_DOWN, "down")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_a, "left")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_d, "right")

TITLE = "Flappy Bird"

# Size of our actual window
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Size we are trying to emulate
VIRTUAL_WIDTH = 512
VIRTUAL_HEIGHT = 288

BIRD_WIDTH = 39
BIRD_HEIGHT = 28

LOG_WIDTH = 70
LOG_HEIGHT = 288
LOGS_GAP = 90
LOGS_SMOOTHNESS = 6.0
LOGS_BIT_POSIBILITY = 0.3
LOGS_MOVING_POSIBILITY = 0.5

#Probability and logic for powerup
PROBABILITY_POWERUP = 0.08
TIME_INVULNERABLE = 1.0
TIME_BIRD_FORM = 7.0

GROUND_HEIGHT = 16

BACKGROUND_LOOPING_POINT = 1157

MAIN_SCROLL_SPEED = 100
BACK_SCROLL_SPEED = 50  # MAIN_SCROLL_SPEED / 2

GRAVITY = 980
JUMP_TAKEOFF_SPEED = GRAVITY / 6
BIRD_SPEED = 150


TIME_TO_SPAWN_LOGS = 1.5

MEDIUM_TEXT_SIZE = 18
HUGE_TEXT_SIZE = 56
FLAPPY_TEXT_SIZE = 28
SUB_TITLE_TEXT = 22
TITLE_TEXT = 28

BASE_DIR = Path(__file__).parent

TEXTURES = {
    "bird": pygame.image.load(BASE_DIR / "assets" / "graphics" / "bird.png"),
    "bird_fantasma": pygame.image.load(BASE_DIR / "assets" / "graphics" / "bird_fantasma.png"),
    "background": pygame.image.load(BASE_DIR / "assets" / "graphics" / "background.png"),
    "ground": pygame.image.load(BASE_DIR / "assets" / "graphics" / "ground.png"),
    "log": pygame.image.load(BASE_DIR / "assets" / "graphics" / "log.png"),
    "powerup": pygame.image.load(BASE_DIR / "assets" / "graphics" / "power_up.png"),
}
# The top log of every pair is the same image, flipped upside down.
TEXTURES["log_inverted"] = pygame.transform.flip(TEXTURES["log"], False, True)

SOUNDS = {
    "jump": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "jump.wav"),
    "explosion": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "explosion.wav"),
    "hurt": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "hurt.wav"),
    "score": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "score.wav"),
    "powerup": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "power_up.mp3"),
    "ghost_form": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "Gost_Bird.mp3"),
    "dead_log_bit": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "dead_2.wav"),
    "change_select": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "change_select.mp3"),
    "select": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "blipSelect.wav"),
    "pause_theme": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "pause_menu.mp3"),
    "game_over": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "game_over.mp3"),
    "ponk_log": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "pum_log.mp3"),
}

MUSIC = {
        "ghost_theme": BASE_DIR / "assets" / "sounds" / "Gost_Bird.mp3",
        "normal_theme": BASE_DIR / "assets" / "sounds" / "BackGround.mp3",
}

pygame.mixer.music.load(BASE_DIR / "assets" / "sounds" / "BackGround.mp3")

FONTS = {
    "medium": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "font.ttf", MEDIUM_TEXT_SIZE),
    "huge": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "font.ttf", HUGE_TEXT_SIZE),
    "flappy": pygame.font.Font(
        BASE_DIR / "assets" / "fonts" / "flappy.ttf", FLAPPY_TEXT_SIZE
    ),
    "sub_title": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "sud_title.ttf", SUB_TITLE_TEXT),
    "title": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "Title.otf", TITLE_TEXT)
}

#Color Global
COLOR_BACKGROUND = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_YELLOW = (255, 255, 0)
