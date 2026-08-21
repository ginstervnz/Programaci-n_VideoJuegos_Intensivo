import math
from src.LogPair import LogPair

class MovingLogPair(LogPair):
    def __init__(self, x: float, y: float, gap: float, speed: float=5.0) -> None:
        super().__init__(x, y, gap)
        self.base_y = y
        self.base_gap = gap
        self.timer = 0.0
        self.speed = speed

    def update(self, dt: float) -> None:
        super().update(dt) 
        self.timer += dt
        movimiento = math.sin(self.timer * self.speed) * 20
        self.y = self.base_y + movimiento
        self.gap = self.base_gap - (2 * movimiento)