"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition for game objects.
"""

from typing import Any, Dict
import settings


def _pickup_heart(player, obj) -> None:
    player.heal(2)
    settings.SOUNDS["heart-taken"].play()

def _pickup_bow(player, obj):
    # Give the bow to the player
    player.has_bow = True
    from src.Bow import Bow
    player.bow = Bow()
    settings.SOUNDS["heart-taken"].play()
    
    # Mark the physical bow item to be removed from the room
    obj.picked_up = True

def _open_chest(player, obj):
    if obj.state == "closed" and player.direction == "up":
        obj.state = "open"
        settings.SOUNDS["open_chest"].play()
        # Spawn the bow below the chest so it drops to the floor
        from src.GameObject import GameObject
        bow_obj = GameObject(GAME_OBJECT_DEFS["bow_item"], obj.x, obj.y + 16)
        
        if not hasattr(player, 'pending_objects'):
            player.pending_objects = []
        player.pending_objects.append(bow_obj)

GAME_OBJECT_DEFS: Dict[str, Dict[str, Any]] = {
    "switch": {
        "type": "switch",
        "texture": "switches",
        "frame": 2,
        "width": 16,
        "height": 16,
        "solid": False,
        "default_state": "unpressed",
        "states": {
            "unpressed": {"frame": 2},
            "pressed": {"frame": 1},
        },
    },
    "pot": {
        "type": "pot",
        "texture": "tiles",
        "frame": 16,
        "width": 16,
        "height": 16,
        "solid": True,
        "consumable": False,
        "default_state": "default",
        "takeable": True,
        "states": {
            "default": {"frame": 16},
        },
    },
    # Definition of heart as a consumable object type.
    "heart": {
        "type": "heart",
        "texture": "hearts",
        "frame": 5,
        "width": 16,
        "height": 16,
        "solid": False,
        "consumable": True,
        "default_state": "default",
        "states": {
            "default": {"frame": 5},
        },
        "on_consume": _pickup_heart,
    },

    "chest": {
        "type": "chest",
        "texture": "chests",
        "width": 16,      
        "height": 16,
        "solid": True,
        "default_state": "closed",
        "states": {
            "closed": {"frame": 1},
            "open": {"frame": 2}
        },
        "on_interact": _open_chest
    },

    "bow_item": {
        "type": "bow_item",
        "texture": "bow",
        "width": 16,
        "height": 16,
        "solid": False,
        "default_state": "default",
        "states": {
            "default": {"frame": 1},
        },
        "on_interact": _pickup_bow,
    },

    "arrow": {
        "type": "arrow",
        "texture": "arrows",
        "width": 16,
        "height": 16,
        "solid": False,
        "default_state": "up",
        "states": {
            "right": {"frame": 1},
            "up": {"frame": 2},
            "left": {"frame": 3},
            "down": {"frame": 4},
        }
    },

    "fireball": {
        "type": "fireball",
        "texture": "fireball",
        "width": 19,
        "height": 11,
        "solid": False,
        "default_state": "active",
        "states": {
            "active": {"frames": [1, 2, 3, 4, 5, 6], "interval": 0.1}
        }
    },

    "boss_key": {
        "type": "boss_key",
        "texture": "boss_key",
        "width": 16,
        "height": 16,     
        "solid": False,
        "consumable": True,
        "default_state": "idle", 
        "states": {
            "idle": { "frame": 1 }
        }
    },

}


