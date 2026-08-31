"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Board.
"""

from typing import List, Optional, Tuple, Any, Dict, Set

import pygame

import random

import settings
from src.Tile import Tile


class Board:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.matches: List[List[Tile]] = []
        self.tiles: List[List[Tile]] = []

        # Ensure the board starts with valid moves
        while True:
            self._initialize_tiles()
            if self.has_possible_moves():
                break

        
    def render(self, surface: pygame.Surface) -> None:
        for row in self.tiles:
            for tile in row:
                if tile is not None:
                    tile.render(surface, self.x, self.y)

    def _is_match_generated(self, i: int, j: int, color: int) -> bool:
        if (
            i >= 2
            and self.tiles[i - 1][j].color == color
            and self.tiles[i - 2][j].color == color
        ):
            return True

        return (
            j >= 2
            and self.tiles[i][j - 1].color == color
            and self.tiles[i][j - 2].color == color
        )

    def _initialize_tiles(self) -> None:
        self.tiles = [
            [None for _ in range(settings.BOARD_WIDTH)]
            for _ in range(settings.BOARD_HEIGHT)
        ]
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                color = random.randint(0, settings.NUM_COLORS - 1)
                while self._is_match_generated(i, j, color):
                    color = random.randint(0, settings.NUM_COLORS - 1)

                self.tiles[i][j] = Tile(
                    i, j, color, random.randint(0, settings.NUM_VARIETIES - 1)
                )

    def _calculate_match_rec(self, tile: Tile) -> Set[Tile]:
        if tile in self.in_stack:
            return []

        self.in_stack.add(tile)

        color_to_match = tile.color

        # Check horizontal match
        h_match: List[Tile] = []

        # Check left
        if tile.j > 0:
            left = max(0, tile.j - 2)
            for j in range(tile.j - 1, left - 1, -1):
                if self.tiles[tile.i][j].color != color_to_match:
                    break
                h_match.append(self.tiles[tile.i][j])

        # Check right
        if tile.j < settings.BOARD_WIDTH - 1:
            right = min(settings.BOARD_WIDTH - 1, tile.j + 2)
            for j in range(tile.j + 1, right + 1):
                if self.tiles[tile.i][j].color != color_to_match:
                    break
                h_match.append(self.tiles[tile.i][j])

        # Check vertical match
        v_match: List[Tile] = []

        # Check top
        if tile.i > 0:
            top = max(0, tile.i - 2)
            for i in range(tile.i - 1, top - 1, -1):
                if self.tiles[i][tile.j].color != color_to_match:
                    break
                v_match.append(self.tiles[i][tile.j])

        # Check bottom
        if tile.i < settings.BOARD_HEIGHT - 1:
            bottom = min(settings.BOARD_HEIGHT - 1, tile.i + 2)
            for i in range(tile.i + 1, bottom + 1):
                if self.tiles[i][tile.j].color != color_to_match:
                    break
                v_match.append(self.tiles[i][tile.j])

        match: List[Tile] = []

        if len(h_match) >= 2:
            for t in h_match:
                if t not in self.in_match:
                    self.in_match.add(t)
                    match.append(t)

        if len(v_match) >= 2:
            for t in v_match:
                if t not in self.in_match:
                    self.in_match.add(t)
                    match.append(t)

        if len(match) > 0:
            if tile not in self.in_match:
                self.in_match.add(tile)
                match.append(tile)

        for t in match:
            match += self._calculate_match_rec(t)

        self.in_stack.remove(tile)
        return match

    def calculate_matches_for(
        self, new_tiles: List[Tile]
    ) -> Optional[List[List[Tile]]]:
        self.in_match: Set[Tile] = set()
        self.in_stack: Set[Tile] = set()

        for tile in new_tiles:
            if tile in self.in_match:
                continue
            match = self._calculate_match_rec(tile)
            if len(match) > 0:
                self.matches.append(match)

        delattr(self, "in_match")
        delattr(self, "in_stack")

        return self.matches if len(self.matches) > 0 else None

    def remove_matches(self) -> None:
        for match in self.matches:
            for tile in match:
                if self.tiles[tile.i][tile.j] is not None:
                    self.tiles[tile.i][tile.j] = None

        self.matches = []

    def get_falling_tiles(self, columns: List[int] = None) -> Tuple[Any, Dict[str, Any]]:
        tweens = []
        cols_to_process = columns if columns is not None else range(settings.BOARD_WIDTH)

        for j in cols_to_process:
            space = False
            space_i = -1
            i = settings.BOARD_HEIGHT - 1

            while i >= 0:
                tile = self.tiles[i][j]
                if space:
                    if tile is not None:
                        self.tiles[space_i][j] = tile
                        tile.i = space_i
                        self.tiles[i][j] = None
                        tweens.append((tile, {"y": tile.i * settings.TILE_SIZE}))
                        space = False
                        i = space_i
                        space_i = -1
                elif tile is None:
                    space = True
                    if space_i == -1:
                        space_i = i
                i -= 1

        for j in cols_to_process:
            missing_count = 0
            for i in range(settings.BOARD_HEIGHT - 1, -1, -1):
                tile = self.tiles[i][j]
                if tile is None:
                    missing_count += 1
                    tile = Tile(
                        i, j,
                        random.randint(0, settings.NUM_COLORS - 1),
                        random.randint(0, settings.NUM_VARIETIES - 1),
                    )
                    tile.y = -missing_count * settings.TILE_SIZE
                    self.tiles[i][j] = tile
                    tweens.append((tile, {"y": tile.i * settings.TILE_SIZE}))

        return tweens


    def reshuffle(self) -> list:

        #Keep the powers
        powerup_locations = []
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                tile = self.tiles[i][j]
                if tile is not None:
                    if getattr(tile, 'is_powerup', False):
                        powerup_locations.append((i, j, 'powerup'))
                    elif getattr(tile, 'is_color_bomb', False):
                        powerup_locations.append((i, j, 'color_bomb'))

        # Re-initialize board until possible moves exist
        while True:
            self._initialize_tiles()

            for loc in powerup_locations:
                i, j, p_type = loc
                if p_type == 'powerup':
                    self.tiles[i][j].is_powerup = True
                elif p_type == 'color_bomb':
                    self.tiles[i][j].is_color_bomb = True

            if self.has_possible_moves():
                break

        tweens = []
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                tile = self.tiles[i][j]
                target_y = tile.y
                tile.y -= settings.VIRTUAL_HEIGHT
                tweens.append((tile, {"y": target_y}))
                
        return tweens

    def has_possible_moves(self) -> bool:
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                # Simulate right swap
                if j < settings.BOARD_WIDTH - 1:
                    if self._check_simulated_match(i, j, i, j + 1):
                        return True
                # Simulate left swap
                if i < settings.BOARD_HEIGHT - 1:
                    if self._check_simulated_match(i, j, i + 1, j):
                        return True
        return False

    def get_hint_move(self) -> Optional[Tuple[Tile, Tile]]:
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                if j < settings.BOARD_WIDTH - 1:
                    if self._check_simulated_match(i, j, i, j + 1):
                        return (self.tiles[i][j], self.tiles[i][j + 1])
                if i < settings.BOARD_HEIGHT - 1:
                    if self._check_simulated_match(i, j, i + 1, j):
                        return (self.tiles[i][j], self.tiles[i + 1][j])
        return None


    def _check_simulated_match(self, i1: int, j1: int, i2: int, j2: int) -> bool:
        # Swap virtually for simulation
        self.tiles[i1][j1], self.tiles[i2][j2] = self.tiles[i2][j2], self.tiles[i1][j1]
        
        # Check for matches
        has_match = self._has_match_at(i1, j1) or self._has_match_at(i2, j2)
        
        # Revert the board state
        self.tiles[i1][j1], self.tiles[i2][j2] = self.tiles[i2][j2], self.tiles[i1][j1]
        
        return has_match

    def _has_match_at(self, i: int, j: int) -> bool:
        
        if self.tiles[i][j] is None:
            return False
            
        color = self.tiles[i][j].color

        # Horizontal check
        count = 1
        for c in range(j - 1, -1, -1):
            if self.tiles[i][c] is not None and self.tiles[i][c].color == color: count += 1
            else: break
        for c in range(j + 1, settings.BOARD_WIDTH):
            if self.tiles[i][c] is not None and self.tiles[i][c].color == color: count += 1
            else: break
        if count >= 3: return True

        # Vertical check
        count = 1
        for r in range(i - 1, -1, -1):
            if self.tiles[r][j] is not None and self.tiles[r][j].color == color: count += 1
            else: break
        for r in range(i + 1, settings.BOARD_HEIGHT):
            if self.tiles[r][j] is not None and self.tiles[r][j].color == color: count += 1
            else: break
            
        return count >= 3
