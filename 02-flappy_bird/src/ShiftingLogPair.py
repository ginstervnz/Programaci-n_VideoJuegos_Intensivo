
from src.LogPair import LogPair
import settings

class ShiftingLogPair(LogPair):
    def __init__(self, x: float, y: float, gap: float, target_y: float) -> None:
        super().__init__(x, y, gap)
        self.target_y = target_y
        self.triggered = False
        self.smoothness = settings.LOGS_SMOOTHNESS  

    def update(self, dt: float) -> None:
        super().update(dt) 
        if self.x < settings.VIRTUAL_WIDTH * 0.75:
            self.triggered = True

        if self.triggered:
            distance_left = self.target_y - self.y
            self.y += distance_left * self.smoothness * dt