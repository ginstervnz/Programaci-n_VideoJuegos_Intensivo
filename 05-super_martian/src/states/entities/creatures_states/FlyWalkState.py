from src.states.entities.BaseEntityState import BaseEntityState

class FlyWalkState(BaseEntityState):
    def enter(self, flipped: bool) -> None:
        self.entity.change_animation("walk")
        self.entity.flipped = flipped
        # Clean one-liner for velocity assignment
        self.entity.vx = self.entity.walk_speed if flipped else -self.entity.walk_speed
        self.entity.vy = 0

    def update(self, dt: float) -> None:
        self.entity.vy = 0
        if self.check_boundary():
            self.entity.vx *= -1
            self.entity.flipped = not self.entity.flipped

    def check_boundary(self) -> bool:
        world_width = self.entity.tilemap.pixel_width

        if self.entity.x + self.entity.width >= world_width:
            self.entity.x = world_width - self.entity.width
            return True
        elif self.entity.x <= 0:
            self.entity.x = 0
            return True
        
        return self.entity.collided_x