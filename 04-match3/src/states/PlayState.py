"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState.
"""

from typing import Dict, Any, List

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text
from gale.timer import Timer
import random
import math

import settings


class PlayState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.level = enter_params["level"]
        self.board = enter_params["board"]
        self.score = enter_params["score"]
        self.show_no_moves = False
        self.board_base_x = self.board.x
        self.board_base_y = self.board.y
        self.idle_timer = 0.0
        self.hinted_tiles = None

        # Position in the grid which we are highlighting
        self.is_dragging = False
        self.dragged_tile = None
        self.start_i = -1
        self.start_j = -1

        self.active = True
        self.timer = settings.LEVEL_TIME
        self.goal_score = self.level * 1.25 * 1000

        # A surface that supports alpha to highlight a selected tile
        self.tile_alpha_surface = pygame.Surface(
            (settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA
        )
        pygame.draw.rect(
            self.tile_alpha_surface,
            (255, 255, 255, 96),
            pygame.Rect(0, 0, settings.TILE_SIZE, settings.TILE_SIZE),
            border_radius=7,
        )

        # A surface that supports alpha to draw behind the text.
        self.text_alpha_surface = pygame.Surface((212, 136), pygame.SRCALPHA)
        pygame.draw.rect(
            self.text_alpha_surface, (56, 56, 56, 234), pygame.Rect(0, 0, 212, 136)
        )

        def decrement_timer():
            self.timer -= 1
            # Play warning sound on timer if we get low
            if self.timer <= 5:
                settings.SOUNDS["clock"].play()

        Timer.every(1, decrement_timer)


    def update(self, dt: float) -> None:
        if self.timer <= 0:
            Timer.clear()
            settings.SOUNDS["game-over"].play()
            self.state_machine.change("game-over", score=self.score)

        if self.score >= self.goal_score:
            Timer.clear()
            settings.SOUNDS["next-level"].play()
            self.state_machine.change("begin", level=self.level + 1, score=self.score)

        # Inactivity hint logic
        if self.active and not getattr(self, 'is_dragging', False):
            self.idle_timer += dt
            if self.idle_timer >= settings.TIMER_IDLE and self.hinted_tiles is None:
                self.hinted_tiles = self.board.get_hint_move()
        else:
            self.idle_timer = 0.0
            self.hinted_tiles = None

        # Drag and drop visual update
        if getattr(self, 'is_dragging', False) and self.dragged_tile and self.active:
            mx, my = pygame.mouse.get_pos()
            pos_x = mx * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
            pos_y = my * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
            self.dragged_tile.x = (pos_x - self.board.x) - settings.TILE_SIZE // 2
            self.dragged_tile.y = (pos_y - self.board.y) - settings.TILE_SIZE // 2

    def render(self, surface: pygame.Surface) -> None:
        self.board.render(surface)

        # Render visual hint for inactive players
        if getattr(self, 'hinted_tiles', None) and self.active:
            alpha = int(177 + math.sin(pygame.time.get_ticks() / 150.0) * 77)
            hint_surf = pygame.Surface((settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(
                hint_surf, 
                (255, 215, 0, alpha), 
                pygame.Rect(0, 0, settings.TILE_SIZE, settings.TILE_SIZE), 
                border_radius=7,
                width=4
            )
            
            for tile in self.hinted_tiles:
                surface.blit(hint_surf, (tile.x + self.board.x, tile.y + self.board.y))


        if getattr(self, 'show_no_moves', False):
            render_text(
                surface,
                "Sin Movimientos",
                settings.FONTS["medium"],
                self.board_base_x + 128,
                self.board_base_y + 128,
                (255, 100, 100),
                center=True,
                shadowed=True
            )

        if getattr(self, 'is_dragging', False) and self.dragged_tile:
            self.dragged_tile.render(surface, self.board.x, self.board.y)

        surface.blit(self.text_alpha_surface, (16, 16))
        render_text(
            surface,
            f"Level: {self.level}",
            settings.FONTS["medium"],
            30,
            24,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["medium"],
            30,
            52,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Goal: {self.goal_score}",
            settings.FONTS["medium"],
            30,
            80,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Timer: {self.timer}",
            settings.FONTS["medium"],
            30,
            108,
            (99, 155, 255),
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not self.active:
            return
        
        # Developer cheats for power-ups
        if getattr(settings, 'ENABLE_CHEATS', False):
            if input_id == "p" and input_data.pressed:
                mx, my = pygame.mouse.get_pos()
                pos_x = mx * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
                pos_y = my * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
                i = (pos_y - self.board.y) // settings.TILE_SIZE
                j = (pos_x - self.board.x) // settings.TILE_SIZE
                if 0 <= i < settings.BOARD_HEIGHT and 0 <= j < settings.BOARD_WIDTH:
                    self.board.tiles[i][j].is_powerup = True
                    
            if input_id == "c" and input_data.pressed:
                mx, my = pygame.mouse.get_pos()
                pos_x = mx * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
                pos_y = my * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
                i = int(pos_y - self.board.y) // settings.TILE_SIZE
                j = int(pos_x - self.board.x) // settings.TILE_SIZE
                if 0 <= i < settings.BOARD_HEIGHT and 0 <= j < settings.BOARD_WIDTH:
                    tile = self.board.tiles[i][j]
                    if tile is not None:
                        tile.color = (tile.color + 1) % settings.NUM_COLORS
                        tile.is_powerup = False 
                        tile.alpha_surface.fill((0, 0, 0, 0))
                        
            if input_id == "b" and input_data.pressed:
                mx, my = pygame.mouse.get_pos()
                i = int(my * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT - self.board.y) // settings.TILE_SIZE
                j = int(mx * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH - self.board.x) // settings.TILE_SIZE
                if 0 <= i < settings.BOARD_HEIGHT and 0 <= j < settings.BOARD_WIDTH:
                    if self.board.tiles[i][j] is not None:
                        self.board.tiles[i][j].is_color_bomb = True

        if input_id == "click":
            self.idle_timer = 0.0
            self.hinted_tiles = None
            pos_x, pos_y = input_data.position
            pos_x = pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
            pos_y = pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
            i = (pos_y - self.board.y) // settings.TILE_SIZE
            j = (pos_x - self.board.x) // settings.TILE_SIZE

            if input_data.pressed:
                if 0 <= i < settings.BOARD_HEIGHT and 0 <= j < settings.BOARD_WIDTH:
                    self.is_dragging = True
                    self.start_i = i
                    self.start_j = j
                    self.dragged_tile = self.board.tiles[i][j]

            elif input_data.released and self.is_dragging:
                self.is_dragging = False
                if 0 <= i < settings.BOARD_HEIGHT and 0 <= j < settings.BOARD_WIDTH:

                    # Release on the same tile 
                    if i == self.start_i and j == self.start_j:
                        tile = self.board.tiles[i][j]
                        if getattr(tile, 'is_powerup', False) or getattr(tile, 'is_color_bomb', False):
                            self.active = False
                            self.board.matches.append([tile])
                            self._calculate_matches([tile], is_player_move=True)
                            self.dragged_tile = None
                            return
                        else:
                        
                            self.active = False
                            Timer.tween(
                                0.15,
                                [
                                    (self.dragged_tile, {
                                        "x": self.start_j * settings.TILE_SIZE,
                                        "y": self.start_i * settings.TILE_SIZE
                                    })
                                ],
                                on_finish=lambda: setattr(self, 'active', True)
                            )
                            self.dragged_tile = None
                            return
                        
                    di = abs(i - self.start_i)
                    dj = abs(j - self.start_j)

                    # Valid adjacent swap
                    if di <= 1 and dj <= 1 and di != dj:
                        self.active = False
                        tile1 = self.dragged_tile
                        tile2 = self.board.tiles[i][j]
                        
                        logical_x1 = self.start_j * settings.TILE_SIZE
                        logical_y1 = self.start_i * settings.TILE_SIZE
                        logical_x2 = j * settings.TILE_SIZE
                        logical_y2 = i * settings.TILE_SIZE

                        def arrive():
                            tile1 = self.board.tiles[self.start_i][self.start_j]
                            tile2 = self.board.tiles[i][j]
                            (
                                self.board.tiles[tile1.i][tile1.j],
                                self.board.tiles[tile2.i][tile2.j],
                            ) = (
                                self.board.tiles[tile2.i][tile2.j],
                                self.board.tiles[tile1.i][tile1.j],
                            )
                            tile1.i, tile1.j, tile2.i, tile2.j = (
                                tile2.i, tile2.j, tile1.i, tile1.j
                            )
                            self._calculate_matches([tile1, tile2], is_player_move=True)

                        Timer.tween(
                            0.25,
                            [
                                (tile1, {"x": logical_x2, "y": logical_y2}),
                                (tile2, {"x": logical_x1, "y": logical_y1}),
                            ],
                            on_finish=arrive,
                        )
                        self.dragged_tile = None
                        return

                # Invalid move 
                if self.dragged_tile:
                    self.active = False
                    settings.SOUNDS["error_move"].stop()
                    settings.SOUNDS["error_move"].play()
                    Timer.tween(
                        0.15,
                        [
                            (self.dragged_tile, {
                                "x": self.start_j * settings.TILE_SIZE,
                                "y": self.start_i * settings.TILE_SIZE
                            })
                        ],
                        on_finish=lambda: setattr(self, 'active', True)
                    )
                self.dragged_tile = None

    def _calculate_matches(self, tiles: List, is_player_move: bool = False) -> None:
        matches = self.board.calculate_matches_for(tiles)

        if matches is None:
            if is_player_move:
                settings.SOUNDS["error_move"].stop()
                settings.SOUNDS["error_move"].play()
                
                tile1, tile2 = tiles[0], tiles[1]
                (
                    self.board.tiles[tile1.i][tile1.j],
                    self.board.tiles[tile2.i][tile2.j],
                ) = (
                    self.board.tiles[tile2.i][tile2.j],
                    self.board.tiles[tile1.i][tile1.j],
                )
                tile1.i, tile1.j, tile2.i, tile2.j = (
                    tile2.i, tile2.j, tile1.i, tile1.j
                )

                Timer.tween(
                    0.25,
                    [
                        (tile1, {"x": tile1.j * settings.TILE_SIZE, "y": tile1.i * settings.TILE_SIZE}),
                        (tile2, {"x": tile2.j * settings.TILE_SIZE, "y": tile2.i * settings.TILE_SIZE}),
                    ],
                    on_finish=lambda: setattr(self, 'active', True)
                )
            else:
                if not self.board.has_possible_moves():
                    self.show_no_moves = True
                    settings.SOUNDS["error_move"].stop()
                    settings.SOUNDS["error_move"].play()
                    
                    def shake(): #auxiliar funtion one
                        self.board.x = self.board_base_x + random.randint(-4, 4)
                        self.board.y = self.board_base_y + random.randint(-4, 4)
                    
                    shaker = Timer.every(0.05, shake)
                    
                    def start_falling(): 
                        shaker.remove() 
                        self.board.x = self.board_base_x 
                        self.board.y = self.board_base_y
                        self.show_no_moves = False
                        
                        # Fall animation for re-shuffled blocks
                        tweens = self.board.reshuffle()
                        Timer.tween(
                            0.5,
                            tweens,
                            ease_function_name="out_bounce",
                            on_finish=lambda: setattr(self, 'active', True)
                        )
                        
                    Timer.after(1.5, start_falling)
                else:
                    self.active = True

            return

        settings.SOUNDS["match"].stop()
        settings.SOUNDS["match"].play()

        cross_powerups = []
        color_bombs = []

        for match in matches:
            self.score += len(match) * 50
            
            for tile in match:
                if getattr(tile, 'is_powerup', False) and tile not in cross_powerups:
                    cross_powerups.append(tile)
                if getattr(tile, 'is_color_bomb', False) and tile not in color_bombs:
                    color_bombs.append(tile)

            if len(match) >= 4:
                spawn_tile = match[0]
                for t in tiles:
                    if t in match:
                        spawn_tile = t
                        break
                
                if len(match) == 4:
                    spawn_tile.is_powerup = True
                else: 
                    spawn_tile.is_color_bomb = True
                    
                match.remove(spawn_tile) 
                
                settings.SOUNDS["power_spawn"].stop()
                settings.SOUNDS["power_spawn"].play()

        self.board.remove_matches()
        # Determine the destruction flow
        if color_bombs:
            p_tile = color_bombs[0]
            self._fire_color_bomb(p_tile)
        elif cross_powerups:
            p_tile = cross_powerups[0]
            self._fire_wave(p_tile.i, p_tile.j, 0)
        else:
            falling_tiles = self.board.get_falling_tiles()
            Timer.tween(
                0.25,
                falling_tiles,
                on_finish=lambda: self._calculate_matches(
                    [item[0] for item in falling_tiles]
                ),
            )


    #Wave animation
    def _fire_wave(self, center_i: int, center_j: int, radius: int) -> None:
    
        if radius > max(settings.BOARD_WIDTH, settings.BOARD_HEIGHT):
            falling_tiles = self.board.get_falling_tiles()
            if falling_tiles:
                Timer.tween(
                    0.25, 
                    falling_tiles, 
                    on_finish=lambda: self._calculate_matches([item[0] for item in falling_tiles])
                )
            else:
                self._calculate_matches([])
            return

        destroyed_cols = []

        def detonate_tile(r: int, c: int, is_center: bool = False) -> bool:
            tile = self.board.tiles[r][c]
            if tile is not None:
                is_power = getattr(tile, 'is_powerup', False)
                is_bomb = getattr(tile, 'is_color_bomb', False)

                saved_tile = tile
                self.board.tiles[r][c] = None
                self.score += 50
                
                if is_power and not is_center:
                    settings.SOUNDS["explosion"].stop()
                    settings.SOUNDS["explosion"].play()
                    self._fire_wave(r, c, 1) 
                elif is_bomb:
                        self._fire_color_bomb(saved_tile)

                
                return True
            return False

        # Initial detonation
        if radius == 0:
            settings.SOUNDS["explosion"].stop()
            settings.SOUNDS["explosion"].play()
            detonate_tile(center_i, center_j, is_center=True)
        else:
            # Horizontal expansion
            if center_j - radius >= 0:
                if detonate_tile(center_i, center_j - radius): 
                    destroyed_cols.append(center_j - radius)
            if center_j + radius < settings.BOARD_WIDTH:
                if detonate_tile(center_i, center_j + radius): 
                    destroyed_cols.append(center_j + radius)
            # Vertical expansion
            if center_i - radius >= 0:
                detonate_tile(center_i - radius, center_j)
            if center_i + radius < settings.BOARD_HEIGHT:
                detonate_tile(center_i + radius, center_j)

        if destroyed_cols:
            falling_tiles = self.board.get_falling_tiles(columns=destroyed_cols)
            if falling_tiles:
                Timer.tween(0.25, falling_tiles)

        Timer.after(0.08, lambda: self._fire_wave(center_i, center_j, radius + 1))


    # Color Bomb 
    def _fire_color_bomb(self, p_tile) -> None:
        settings.SOUNDS["explosion2"].stop()
        settings.SOUNDS["explosion2"].play()
        
        destroyed_cols = [p_tile.j]
        target_color = p_tile.color
        
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                tile = self.board.tiles[i][j]
                if tile is not None and tile.color == target_color:
                    if getattr(tile, 'is_powerup', False):
                        self._fire_wave(i, j, 1)
                        
                    self.board.tiles[i][j] = None
                    self.score += 50
                    if j not in destroyed_cols:
                        destroyed_cols.append(j)

        if destroyed_cols:
            falling_tiles = self.board.get_falling_tiles(columns=destroyed_cols)
            if falling_tiles:
                Timer.tween(
                    0.25, 
                    falling_tiles, 
                    on_finish=lambda: self._calculate_matches([item[0] for item in falling_tiles])
                )
            else:
                self._calculate_matches([])
        else:
            self._calculate_matches([])