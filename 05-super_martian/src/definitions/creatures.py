"""
ISPPV1 2023
Study Case: Super Martian (Platformer)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition for creatures.
"""

from typing import Dict, Any

from src.states.entities import creatures_states


CREATURES: Dict[int, Dict[str, Any]] = {
    48: {
        "texture_id": "creatures",
        "walk_speed": 10,
        "animation_defs": {"walk": {"frames": [48, 49], "interval": 0.25}, "die": {"frames": [50,51], "interval": 1.0}},
        "states": {"walk": creatures_states.SnailWalkState, "die": creatures_states.SnailDieState},
        "first_state": "walk",
    },
    52: {
        "texture_id": "creatures",
        "walk_speed": 15,
        "animation_defs": {"walk": {"frames": [52, 53], "interval": 0.18}, "die": {"frames": [54,55], "interval": 1.0}},
        "states": {"walk": creatures_states.SnailWalkState, "die": creatures_states.SnailDieState},
        "first_state": "walk",
    },
    0: {
        "texture_id": "creatures",
        "walk_speed": 12,  
        "animation_defs": {"walk": {"frames": [0, 1], "interval": 0.2}, "die": {"frames": [2], "interval": 1.0}},  
        "states": {"walk": creatures_states.SnailWalkState, "die": creatures_states.SnailDieState},
        "first_state": "walk",
    },
    19: {
        "texture_id": "creatures",
        "walk_speed": 12,  
        "animation_defs": {"walk": {"frames": [19, 20], "interval": 0.2}, "die": {"frames": [21], "interval": 1.0}},  
        "states": {"walk": creatures_states.SnailWalkState, "die": creatures_states.SnailDieState},
        "first_state": "walk",
    },
    32: {
        "texture_id": "creatures",
        "walk_speed": 20, 
        "animation_defs": {"walk": {"frames": [32, 33], "interval": 0.15}, "die": {"frames": [34], "interval": 1.0}},
        "states": {"walk": creatures_states.FlyWalkState, "die": creatures_states.SnailDieState},
        "first_state": "walk",
    },
    10:{
        "texture_id": "slime_sheet_v2",
        "walk_speed": 12,  
        "animation_defs": {"walk": {"frames": [9, 13], "interval": 0.2}, "die": {"frames": [28,36,37,38,39,40], "interval": 0.1}},  
        "states": {"walk": creatures_states.GoblinWalkState, "die": creatures_states.SnailDieState},
        "first_state": "walk",
    },
    9:{
        "texture_id": "slime_sheet_v4",
        "walk_speed": 12,  
        "animation_defs": {"walk": {"frames": [9, 13], "interval": 0.2}, "die": {"frames": [28,36,37,38,39,40], "interval": 0.1}},  
        "states": {"walk": creatures_states.GoblinWalkState, "die": creatures_states.SnailDieState},
        "first_state": "walk",
    },
    7:{
        "texture_id": "skeleton_sheet",
        "walk_speed": 12,  
        "animation_defs": {"walk": {"frames": [6, 9], "interval": 0.2}, "die": {"frames": [24,25,26,27,28,29], "interval": 0.07}},  
        "states": {"walk": creatures_states.GoblinWalkState, "die": creatures_states.SnailDieState},
        "first_state": "walk",
    },
    6:{
        "texture_id": "goblin_sheet_1",
        "walk_speed": 12,  
        "animation_defs": {"walk": {"frames": [6, 9], "interval": 0.2}, "die": {"frames": [24,25,26,27,28], "interval": 0.1}},  
        "states": {"walk": creatures_states.GoblinWalkState, "die": creatures_states.SnailDieState},
        "first_state": "walk",
    },
    
}
