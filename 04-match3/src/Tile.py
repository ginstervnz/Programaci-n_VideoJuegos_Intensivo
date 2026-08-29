"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Tile.
"""

import pygame

import settings


class Tile:
    def __init__(self, i: int, j: int, color: int, variety: int) -> None:
        self.i = i
        self.j = j
        self.x = self.j * settings.TILE_SIZE
        self.y = self.i * settings.TILE_SIZE
        self.color = color
        self.variety = variety
        self.alpha_surface = pygame.Surface(
            (settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA
        )
        # Power-up flags
        self.is_powerup = False
        self.is_color_bomb = False

    def render(self, surface: pygame.Surface, offset_x: int, offset_y: int) -> None:
        texture = settings.TEXTURES["tiles"]
        variety = self.variety

        # Determine texture and variety based on power-up status
        if getattr(self, 'is_powerup', False):
            texture = settings.TEXTURES["power_tiles"]
            variety = 5 if self.color % 2 == 0 else 0
        elif getattr(self, 'is_color_bomb', False):
            texture = settings.TEXTURES["bomb_tiles"]
            variety = 5 if self.color % 2 == 0 else 0

        self.alpha_surface.fill((0, 0, 0, 0))
        self.alpha_surface.blit(
            texture,
            (0, 0),
            settings.FRAMES["tiles"][self.color][variety],
        )
        pygame.draw.rect(
            self.alpha_surface,
            (34, 32, 52, 200),
            pygame.Rect(0, 0, settings.TILE_SIZE, settings.TILE_SIZE),
            border_radius=7,
        )
        surface.blit(self.alpha_surface, (self.x + 2 + offset_x, self.y + 2 + offset_y))

        # Draw the actual tile
        surface.blit(
            texture,
            (self.x + offset_x, self.y + offset_y),
            settings.FRAMES["tiles"][self.color][variety],
        )
