"""
ISPPV1 2023
Study Case: Super Martian (Platformer)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition for items.
"""

from typing import Dict, Any

import random

from gale.timer import Timer

import settings
from src.GameItem import GameItem
from src.Player import Player


def pickup_coin(
    coin: GameItem, player: Player, points: int, color: int, time: float
) -> None:
    settings.SOUNDS["pickup_coin"].stop()
    settings.SOUNDS["pickup_coin"].play()
    player.score += points
    player.coins_counter[color] += 1
    def safe_respawn():
        if not getattr(player, "game_frozen", False):
            coin.respawn()
    Timer.after(time, safe_respawn)


def pickup_green_coin(coin: GameItem, player: Player):
    pickup_coin(coin, player, 1, 62, random.uniform(2, 4))


def pickup_blue_coin(coin: GameItem, player: Player):
    pickup_coin(coin, player, 5, 61, random.uniform(5, 8))


def pickup_red_coin(coin: GameItem, player: Player):
    pickup_coin(coin, player, 20, 55, random.uniform(10, 18))


def pickup_yellow_coin(coin: GameItem, player: Player):
    pickup_coin(coin, player, 50, 54, random.uniform(20, 25))

def pickup_new_coin(coin: GameItem, player: Player):
    pickup_coin(coin, player, 10, 36, random.uniform(3, 6))

def pickup_key(key: GameItem, player: Player):
    settings.SOUNDS["pick_key"].stop()
    settings.SOUNDS["pick_key"].play()
    player.has_key = True  
    key.active = False
    

# Handles collision logic for the special block, including spawning a key
def hit_special_block(block: GameItem, player: Player, another=None):
    
    if player.vy >= 0 and (player.y + player.height) <= block.y + 12:
        player.y = block.y - player.height
        player.vy = 0  
        player.on_ground = True
                
    elif player.vy < 0 and player.y >= block.y + block.height - 12:
        player.y = block.y + block.height
        player.vy = 0  
        settings.SOUNDS["punch"].stop()
        settings.SOUNDS["punch"].play()
        if not getattr(block, "is_empty", False):
            block.is_empty = True  
            
            key_def = ITEMS["coins"][11].copy()
            key_def["frame_index"] = 11
            key_def["x"] = block.x
            key_def["y"] = block.y  
            key_def["width"] = block.width
            key_def["height"] = block.height
            
            new_key = GameItem(**key_def)
            new_key.level = block.level 
            new_key.collidable = False
            
            block.level.items.insert(0, new_key)
            settings.SOUNDS["reveal"].play()

            Timer.tween(0.5, [(new_key, {"y": block.y - block.height})])
            Timer.after(0.5, lambda: setattr(new_key, "collidable", True))
            
    elif (player.y + player.height) > block.y + 12 and player.y < block.y + block.height - 12:
        if player.vx > 0 and player.x < block.x:
            player.x = block.x - player.width
        elif player.vx < 0 and player.x > block.x:
            player.x = block.x + block.width

ITEMS: Dict[str, Dict[int, Dict[str, Any]]] = {
    "coins": {
        62: {
            "texture_id": "tiles",
            "consumable": True,
            "collidable": True,
            "on_consume": pickup_green_coin,
        },
        61: {
            "texture_id": "tiles",
            "consumable": True,
            "collidable": True,
            "on_consume": pickup_blue_coin,
        },
        55: {
            "texture_id": "tiles",
            "consumable": True,
            "collidable": True,
            "on_consume": pickup_red_coin,
        },
        54: {
            "texture_id": "tiles",
            "consumable": True,
            "collidable": True,
            "on_consume": pickup_yellow_coin,
        },
        36: {
           "texture_id": "new_coins",  
            "consumable": True,
            "collidable": True,
            "on_consume": pickup_new_coin,
            "frames": [36, 37, 38, 46, 47, 48], 
            "interval": 0.15,
        },
        10: {
            "texture_id": "new_coins", 
            "consumable": False, 
            "collidable": True,
            "on_collide": hit_special_block, 
        },
        11: {
            "texture_id": "new_coins", 
            "consumable": True,
            "collidable": True,
            "on_consume": pickup_key,
        },

    }
}
