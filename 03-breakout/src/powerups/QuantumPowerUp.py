from typing import TypeVar
import pygame
import random
import settings
from src.powerups.PowerUp import PowerUp

class QuantumPowerUp(PowerUp):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 0)

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(settings.TEXTURES["shield"], (self.x, self.y))

    def take(self, play_state: TypeVar("PlayState")) -> None:
        play_state.quantum_timer = settings.DURATION_SHIELD 
        play_state.quantum_nodes = []
        
        # Generate 4 Nodes of center paddle
        for _ in range(4):
            play_state.quantum_nodes.append({
                "x": play_state.paddle.x + play_state.paddle.width / 2,
                "y": play_state.paddle.y,
                "vx": random.uniform(-200, 200),
                "vy": random.uniform(-150, 150) 
            })
        
        settings.SOUNDS["take_shield"].stop()
        settings.SOUNDS["take_shield"].play()
        
        self.active = False