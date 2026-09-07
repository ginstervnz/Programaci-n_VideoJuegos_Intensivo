from gale.factory import Factory
from src.Projectile import Projectile
from src.GameObject import GameObject

#Create a new class for the arrow projectile
class Arrow(Projectile):
    def __init__(self, x: float, y: float, direction: str, **kwargs):
        from src.definitions.game_objects import GAME_OBJECT_DEFS
        arrow_obj = GameObject(GAME_OBJECT_DEFS["arrow"], x, y)
        arrow_obj.state = direction
        super().__init__(arrow_obj, direction, max_tiles=10)


class Bow:
    def __init__(self):
        #Gale's Factory will handle the creation of Arrow instances
        self.arrow_factory = Factory(Arrow)

    def fire(self, x: float, y: float, direction: str):
        properties = {
            'direction': direction
        }
        return self.arrow_factory.create(x, y, properties)