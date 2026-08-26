import math
from src.LogPair import LogPair
import settings

class MovingLogPair(LogPair):
    def __init__(self, x: float, y: float, gap: float, speed: float=5.0) -> None:
        super().__init__(x, y, gap)
        self.base_y = y
        self.base_gap = gap
        self.timer = 0.0
        self.speed = speed
        self.is_closed = False #Flag for sound of bite

    def update(self, dt: float) -> None:
        super().update(dt) 
        self.timer += dt
        factor = (math.cos(self.timer * self.speed) + 1) / 2 #Factor cos for logic bite
        self.gap = self.base_gap * factor #If factor is 0 it is close logs
        
        self.y = self.base_y + (self.base_gap - self.gap) / 2 #two logs move
        
        #Sound Bite logic
        if self.gap <= 5.0 and not self.is_closed:
            settings.SOUNDS["ponk_log"].play()
            self.is_closed = True
        
        elif self.gap > 25.0:
            self.is_closed = False