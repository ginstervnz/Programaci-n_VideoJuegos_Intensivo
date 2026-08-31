"""
ISPPV1 2023
Study Case: Super Martian (Platformer)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class GameItem.
"""

from typing import Callable, TypeVar, Any, Optional

from src import mixins


class GameItem(mixins.DrawableMixin, mixins.CollidableMixin):
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        texture_id: str,
        frame_index: int = 0,
        collidable: bool = True,
        consumable: bool = False,
        on_collide: Optional[Callable[[TypeVar("GameItem"), Any], Any]] = None,
        on_consume: Optional[Callable[[TypeVar("GameItem"), Any], Any]] = None,
        frames: Optional[list] = None,
        interval: float = 0.1,
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.texture_id = texture_id
        self.frame_index = frame_index
        self.flipped = False
        self.collidable = collidable
        self.consumable = consumable
        self._on_collide = on_collide
        self._on_consume = on_consume
        self.active = True
        self.frames = frames
        self.interval = interval
        self.anim_timer = 0
        self.current_frame = 0
        if self.frames:
            self.frame_index = self.frames[0]

    def respawn(self, x: Optional[float] = None, y: Optional[float] = None) -> None:
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        self.active = True

    def on_collide(self, another: Any) -> Any:
        if not self.collidable or self._on_collide is None:
            return None
        return self._on_collide(self, another)

    def on_consume(self, consumer: Any) -> Any:
        if not self.consumable or self._on_consume is None:
            return None
        self.active = False
        return self._on_consume(self, consumer)

    def update(self, dt: float) -> None:
        if not self.active or not self.frames:
            return
            
        self.anim_timer += dt
        if self.anim_timer >= self.interval:
            self.anim_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.frame_index = self.frames[self.current_frame]