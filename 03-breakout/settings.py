"""
ISPPV1 2023
Study Case: Breakout

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the game settings that include the association of the
inputs with an their ids, constants of values to set up the game, sounds,
textures, frames, and fonts.
"""

from pathlib import Path

import pygame

from gale import input_handler
from gale.frames import generate_frames

from src.utilities.frames import (
    generate_paddle_frames,
    generate_ball_frames,
    generate_brick_frames,
    generate_powerups_frames,
)

input_handler.InputHandler.set_keyboard_action(input_handler.KEY_ESCAPE, "quit")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_RETURN, "enter")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_UP, "move_up")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_RIGHT, "move_right")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_DOWN, "move_down")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_LEFT, "move_left")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_SPACE, "pause")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_f, "shot")

TITLE = "Breakout"

# Size of our actual window
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Size we are trying to emulate
VIRTUAL_WIDTH = 432
VIRTUAL_HEIGHT = 243

PADDLE_SPEED = 200

NUM_HIGHSCORES = 10

# Num points base to recover a live
LIVE_POINTS_BASE = 2000

PADDLE_GROW_UP_POINTS = 200

#Settings of powerups
POWERUP_SPEED = 50
TIME_POWERUP_STICKY = 5.0
POSSIBILITY_POWERUP_SPAWN = 0.2
RADIACTIVE_DAMAGE = 3
ROCKET_TIME = 10.0
TIME_POWEROP_ELECTRO = 10.0
DURATION_SHIELD = 10.0

BASE_DIR = Path(__file__).parent

SOUNDS = {
    "paddle_hit": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "paddle_hit.wav"),
    "selected": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "selected.wav"),
    "brick_hit_1": pygame.mixer.Sound(
        BASE_DIR / "assets" / "sounds" / "brick_hit_1.wav"
    ),
    "brick_hit_2": pygame.mixer.Sound(
        BASE_DIR / "assets" / "sounds" / "brick_hit_2.wav"
    ),
    "wall_hit": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "wall_hit.wav"),
    "hurt": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "hurt.wav"),
    "level_complete": pygame.mixer.Sound(
        BASE_DIR / "assets" / "sounds" / "level_complete.wav"
    ),
    "high_score": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "high_score.wav"),
    "life": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "life.wav"),
    "grow_up": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "grow_up.wav"),
    "pause": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "pause.wav"),
    "sticky": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "sticky.mp3"),
    "radiactive": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "radiactive_sound.wav"),
    "one_up": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "one_up.mp3"),
    "shot_sound": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "shot_sound.mp3"),
    "rocket": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "take_gun.mp3"),
    "explosion": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "sound_big_explosion.mp3"),
    "take_electro": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "take_electro.mp3"),
    "eletro_efect": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "electro_efect.mp3"),
    "hit_shield": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "hit_shield.mp3"),
    "take_shield": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "take_shield.mp3"),
}

TEXTURES = {
    "background": pygame.image.load(
        BASE_DIR / "assets" / "graphics" / "background.png"
    ),
    "spritesheet": pygame.image.load(BASE_DIR / "assets" / "graphics" / "breakout.png"),
    "hearts": pygame.image.load(BASE_DIR / "assets" / "graphics" / "hearts.png"),
    "arrows": pygame.image.load(BASE_DIR / "assets" / "graphics" / "arrows.png"),
    "sticky_up": pygame.image.load(BASE_DIR / "assets" / "graphics" / "sticky.png"),
    "arrow_shot": pygame.image.load(BASE_DIR / "assets" / "graphics" / "arrows_shot.png"),
    "radiactive_ball": pygame.image.load(BASE_DIR / "assets" / "graphics" / "radiactive_ball.png"),
    "radiactive": pygame.image.load(BASE_DIR / "assets" / "graphics" / "radiactive.png"),
    "paddle_rocket": pygame.image.load(BASE_DIR / "assets" / "graphics" / "breakout_rocket.png"),
    "rocket_projectile": pygame.image.load(BASE_DIR / "assets" / "graphics" / "rocket2.png"),
    "rocket_powerup": pygame.image.load(BASE_DIR / "assets" / "graphics" / "rocket.png"),
    "rocket_left": pygame.image.load(BASE_DIR / "assets" / "graphics" / "rocket_left.png"),
    "rocket_right": pygame.image.load(BASE_DIR / "assets" / "graphics" / "rocket_right.png"),
    "life_powerup": pygame.image.load(BASE_DIR / "assets" / "graphics" / "one_up.png"),
    "paddle_sticky": pygame.image.load(BASE_DIR / "assets" / "graphics" / "breakout_sticky.png"),
    "rocket_special": pygame.image.load(BASE_DIR / "assets" / "graphics" / "rocket3.png"),
    "electro": pygame.image.load(BASE_DIR / "assets" / "graphics" / "electry.png"),
    "shield": pygame.image.load(BASE_DIR / "assets" / "graphics" / "shield.png"),
}

FRAMES = {
    "paddles": generate_paddle_frames(),
    "balls": generate_ball_frames(),
    "bricks": generate_brick_frames(TEXTURES["spritesheet"]),
    "hearts": generate_frames(TEXTURES["hearts"], 10, 9),
    "arrows": generate_frames(TEXTURES["arrows"], 24, 24),
    "powerups": generate_powerups_frames(),
}

FONTS = {
    "tiny": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "font.ttf", 6),
    "small": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "font.ttf", 8),
    "medium": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "font.ttf", 12),
    "large": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "font.ttf", 24),
}

#Colors 
COLOR_WHITE = (255, 255, 255)
BLUE_COLOR = (103, 255, 255)