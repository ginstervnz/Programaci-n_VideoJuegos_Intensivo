from gale.tilemap import CollisionType, collision_type_at

from src.states.entities.BaseEntityState import BaseEntityState


class GoblinWalkState(BaseEntityState):
    def enter(self, flipped: bool) -> None:
        self.entity.change_animation("walk")
        self.entity.flipped = not flipped 
        self.entity.vx = -self.entity.walk_speed if self.entity.flipped else self.entity.walk_speed

    def update(self, dt: float) -> None:
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

        if self.entity.collided_x:
            return True

        tilemap = self.entity.tilemap
        
        row = int((self.entity.y + self.entity.height + 2) // tilemap.tile_height)

        if self.entity.vx > 0:
            col = int((self.entity.x + self.entity.width + 2) // tilemap.tile_width)
        else:
            col = int((self.entity.x - 2) // tilemap.tile_width)

        try:
            cells_to_check = [
                collision_type_at(tilemap, self.entity.COLLISION_LAYER, row, col),
                collision_type_at(tilemap, self.entity.COLLISION_LAYER, row, col - 1),
                collision_type_at(tilemap, self.entity.COLLISION_LAYER, row - 1, col),
                collision_type_at(tilemap, self.entity.COLLISION_LAYER, row - 1, col - 1)
            ]
            
            # Returns True only if ALL cells are NONE
            return all(cell == CollisionType.NONE for cell in cells_to_check)
            
        except IndexError:
            # Safe fallback if looking outside map boundaries
            return True