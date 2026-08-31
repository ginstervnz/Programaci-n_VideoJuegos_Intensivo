from src.states.entities.BaseEntityState import BaseEntityState
import settings
from gale.timer import Timer


class SnailDieState(BaseEntityState):
    def enter(self, *args, **kwargs) -> None:
        self.entity.vx = 0
        self.entity.vy = 0
        settings.SOUNDS["dead_enemy"].stop()
        settings.SOUNDS["dead_enemy"].play()
        self.entity.change_animation("die")

        Timer.after(0.4, lambda: setattr(self.entity, "is_dead", True))
        
        