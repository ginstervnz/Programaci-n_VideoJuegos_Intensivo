"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Room.
"""

import random
from typing import Any, Callable, List, Optional, TypeVar

import pygame

from gale.tilemap import TileMap

import settings
from src.definitions.entity import ENTITY_DEFS
from src.definitions.game_objects import GAME_OBJECT_DEFS
from src.Entity import Entity
from src.GameObject import GameObject
from src.states.entity.EntityIdleState import EntityIdleState
from src.states.entity.EntityWalkState import EntityWalkState
from src.world.Doorway import Doorway
from gale.particle_system import ParticleSystem

_ENEMY_TYPES = ["skeleton", "slime", "bat", "ghost", "spider"]

# Door archway detection zones, in the same room-local coordinates as
# every entity's x/y (not screen space, so this works regardless of
# camera/adjacent-room render offsets). Wider than the doorway's own
# get_collision_rect() on purpose -- these only decide *whether* the
# player is close enough to a doorway to bother clipping at all; the
# actual visible shape while crossing is the doorway's own, narrower,
# rect (see _doorway_opening_for below), applied with gale.stencil in
# Entity.render_sprite so the player is seen passing through the wall
# opening -- clipped by its edges -- instead of popping in and out of
# existence.
_DOORWAY_ZONES = {
    "left": pygame.Rect(
        -settings.TILE_SIZE - 6,
        settings.MAP_RENDER_OFFSET_Y + settings.MAP_HEIGHT // 2 * settings.TILE_SIZE - settings.TILE_SIZE * 2,
        settings.TILE_SIZE * 2 + 6,
        settings.TILE_SIZE * 3,
    ),
    "right": pygame.Rect(
        settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH * settings.TILE_SIZE - 6,
        settings.MAP_RENDER_OFFSET_Y + settings.MAP_HEIGHT // 2 * settings.TILE_SIZE - settings.TILE_SIZE * 2,
        settings.TILE_SIZE * 2 + 6,
        settings.TILE_SIZE * 3,
    ),
    "top": pygame.Rect(
        settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH // 2 * settings.TILE_SIZE - settings.TILE_SIZE,
        -settings.TILE_SIZE - 6,
        settings.TILE_SIZE * 2,
        settings.TILE_SIZE * 2 + 12,
    ),
    "bottom": pygame.Rect(
        settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH // 2 * settings.TILE_SIZE - settings.TILE_SIZE,
        settings.VIRTUAL_HEIGHT - settings.TILE_SIZE - 6,
        settings.TILE_SIZE * 2,
        settings.TILE_SIZE * 2 + 12,
    ),
}


def _doorway_opening_for(
    rect: pygame.Rect, doorways_by_direction: dict
) -> Optional[pygame.Rect]:
    """
    :returns: The precise opening rect of whichever doorway rect is
        close to (i.e. overlapping the wider detection zone of), or
        None if rect isn't near any doorway right now.
    """
    for direction, zone in _DOORWAY_ZONES.items():
        if zone.colliderect(rect):
            if direction in doorways_by_direction:
                return doorways_by_direction[direction].get_collision_rect()

    return None

class ParticleEffect:
    def __init__(self, x: float, y: float, colors: list):
        self.active = True
        self.system = ParticleSystem(int(x), int(y), 15, self.on_finish)
        self.system.set_colors(colors)
        self.system.set_life_time(0.1, 0.25) 
        self.system.set_linear_acceleration(-30, -30, 30, 30)
        self.system.set_area_spread(2, 2)
        
        self.system.generate()

    def on_finish(self) -> None:
        self.active = False

class ExplosionEffect:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.timer = 0.0
        self.frame = 1
        self.active = True

    def update(self, dt: float) -> None:
        self.timer += dt
        if self.timer > 0.05: #Velocity of the explosion animation
            self.timer = 0
            self.frame += 1
            if self.frame > 7:
                self.active = False

    def render(self, surface: pygame.Surface, offset_x: float = 0, offset_y: float = 0) -> None:
        if self.active:
            image = settings.TEXTURES["explosion"]
            frame_rect = settings.frame("explosion", self.frame)
            surface.blit(image, (self.x + offset_x, self.y + offset_y), frame_rect)

class Room:
    def __init__(
        self,
        player: TypeVar("Player"),
        on_game_over: Callable[[], None],
    ) -> None:
        # Reference to player for collisions, etc.
        self.player = player
        self.on_game_over = on_game_over

        self.width = settings.MAP_WIDTH
        self.height = settings.MAP_HEIGHT

        self.tilemap = TileMap(settings.TILE_SIZE, settings.TILE_SIZE, self.width, self.height)
        self.tilemap.add_tileset(settings.TILESET)
        self._generate_walls_and_floors()

        self.entities: List[Entity] = []
        self._generate_entities()

        self.objects: List[GameObject] = []
        self._generate_objects()

        # Doorways that lead to other dungeon rooms.
        self.doorways = [
            Doorway("top", False, self),
            Doorway("bottom", False, self),
            Doorway("left", False, self),
            Doorway("right", False, self),
        ]
        self._doorways_by_direction = {
            doorway.direction: doorway for doorway in self.doorways
        }

        # Used for centering the dungeon rendering.
        self.render_offset_x = settings.MAP_RENDER_OFFSET_X
        self.render_offset_y = settings.MAP_RENDER_OFFSET_Y

        # Used for drawing when this room is the next room, adjacent to the
        # active one, while sliding between rooms.
        self.adjacent_offset_x = 0
        self.adjacent_offset_y = 0

        self.projectiles: List[Any] = []

        self.particle_effects = []
        self.explosions = []

    def update(self, dt: float) -> None:

        # Don't update anything if we are sliding to another room.
        if self.adjacent_offset_x != 0 or self.adjacent_offset_y != 0:
            return

        # Check if the doors should be opened based on the switch state and whether the player has the bow if a chest is present
        self.check_door_conditions()

        for effect in self.particle_effects:
            effect.system.update(dt)
        self.particle_effects = [e for e in self.particle_effects if e.active]

        self.player.update(dt)

        # Grab spawned projectiles from the player 
        if getattr(self.player, 'pending_projectiles', []):
            self.projectiles.extend(self.player.pending_projectiles)
            self.player.pending_projectiles.clear()

        
        if getattr(self.player, 'pending_objects', []):
            self.objects.extend(self.player.pending_objects)
            self.player.pending_objects.clear()
        
        for entity in self.entities:
            if entity.health <= 0 and type(entity).__name__ != "Boss":
                entity.dead = True

                # Chance to drop a heart.
                if not entity.dropped and random.randint(1, 10) == 1:
                    self.objects.append(
                        GameObject(GAME_OBJECT_DEFS["heart"], entity.x, entity.y)
                    )

                # Whether the entity dropped or not, it is assumed that it did.
                entity.dropped = True

            elif not entity.dead:
                entity.process_ai(self, dt)
                entity.update(dt)

            # Collision between the player and entities in the room.
            if (
                not entity.dead
                and self.player.collides(entity)
                and not self.player.invulnerable
            ):
                if type(entity).__name__ == "Boss" and entity.health <= 0:
                    continue
                settings.SOUNDS["hit-player"].play()
                if type(entity).__name__ == "Boss":
                    self.player.damage(2)
                else:
                    self.player.damage(1)
                
                self.player.go_invulnerable(1.5)

                if self.player.health <= 0:
                    self.player.health = 0
                    self.on_game_over()

        self.entities = [entity for entity in self.entities if not entity.dead]

        for obj in list(self.objects):
            obj.update(dt)

            if self.player.collides(obj):
                obj.on_collide()

                if obj.solid and not obj.taken:
                    self._push_player_out_of(obj)

                if obj.consumable:
                    obj.on_consume(self.player, obj)
                    self.objects.remove(obj)

        for projectile in list(self.projectiles):
            was_dead = projectile.dead
            projectile.update(dt)
       
            hit_enemy = False
            
            # Fireballs from the boss are considered "enemy projectiles" and will damage the player if they collide.
            if getattr(projectile, 'is_enemy_projectile', False):
                if not projectile.dead and projectile.collides(self.player):
                    settings.SOUNDS["hit-player"].play()
                    self.player.health = 0
                    projectile.dead = True
                    self.explosions.append(ExplosionEffect(projectile.obj.x - 8, projectile.obj.y - 8))
                    self.on_game_over()
                if projectile.dead and not was_dead:
                    self.explosions.append(ExplosionEffect(projectile.obj.x - 8, projectile.obj.y - 8))      
            
            # Arrow projectiles from the player will damage enemies if they collide.
            else:
                for entity in self.entities:
                    if projectile.dead:
                        break
           
                    if not entity.dead and projectile.collides(entity):
                        projectile.dead = True
                        hit_enemy = True
                        
                        if hasattr(entity, 'is_immune'):
                            if entity.is_immune:
                                entity.is_immune = False
                                entity.immunity_timer = 5.0
                                settings.SOUNDS["hit-enemy"].play()
                        else:
                            entity.damage(1)
                            settings.SOUNDS["hit-enemy"].play()
           
                        # Particle effect for hitting an enemy (red particles)
                        effect = ParticleEffect(
                            entity.x + entity.width / 2, 
                            entity.y + entity.height / 2, 
                            [(255, 0, 0, 255), (255, 100, 100, 255)]
                        )
                        self.particle_effects.append(effect)
                        
                # Particle effect for hitting a wall (gray particles)
                if projectile.dead and not was_dead and not hit_enemy:
                    effect = ParticleEffect(
                        projectile.obj.x + projectile.obj.width / 2, 
                        projectile.obj.y + projectile.obj.height / 2, 
                        [(200, 200, 200, 255), (255, 255, 255, 255)]
                    )
                    self.particle_effects.append(effect)
       
            if projectile.dead:
                self.projectiles.remove(projectile)
        
        for exp in self.explosions:
            exp.update(dt)
        self.explosions = [e for e in self.explosions if e.active]
        
        # Remove any objects that have been picked up (like the bow) from the room's object list
        self.objects = [obj for obj in self.objects if not getattr(obj, 'picked_up', False)]

    def _push_player_out_of(self, obj: GameObject) -> None:
        player = self.player
        player_y = player.y + player.height / 2
        player_height = player.height - player.height / 2
        player_right = player.x + player.width
        player_bottom = player_y + player_height

        if (
            player.direction == "left"
            and not (player_y >= (obj.y + obj.height))
            and not (player_bottom <= obj.y)
        ):
            player.x = obj.x + obj.width
        elif (
            player.direction == "right"
            and not (player_y >= (obj.y + obj.height))
            and not (player_bottom <= obj.y)
        ):
            player.x = obj.x - player.width
        elif (
            player.direction == "down"
            and not (player.x >= (obj.x + obj.width))
            and not (player_right <= obj.x)
        ):
            player.y = obj.y - player.height
        elif (
            player.direction == "up"
            and not (player.x >= (obj.x + obj.width))
            and not (player_right <= obj.x)
        ):
            player.y = obj.y + obj.height - player.height / 2

    def take_adjacent_pot(self, player: TypeVar("Player")) -> None:
        """
        Looks for a takeable object directly in front of the player (one
        tile away, in the direction they're currently facing) and, if
        found, removes it from the room and has the player lift it.
        """
        player_y = player.y + player.height / 2
        player_height = player.height - player.height / 2
        player_col = int((player.x + player.width / 2) // settings.TILE_SIZE)
        player_row = int((player_y + player_height / 2) // settings.TILE_SIZE)

        for obj in self.objects:
            if not obj.takeable:
                continue

            obj_col = int((obj.x + obj.width / 2) // settings.TILE_SIZE)
            obj_row = int((obj.y + obj.height / 2) // settings.TILE_SIZE)

            adjacent = (
                (player.direction == "right" and obj_row == player_row and obj_col == player_col + 1)
                or (player.direction == "left" and obj_row == player_row and obj_col == player_col - 1)
                or (player.direction == "up" and obj_col == player_col and obj_row == player_row - 1)
                or (player.direction == "down" and obj_col == player_col and obj_row == player_row + 1)
            )

            if adjacent:
                self.objects.remove(obj)
                player.change_state("pot-lift", pot=obj)
                return

    def interact_adjacent_object(self, player: TypeVar("Player")) -> None:
        """
        Looks for an interactable object directly in front of the player using 
        a projected hitbox, and triggers it.
        """
        reach = 16 
        interaction_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        
        #Create a projected hitbox in front of the player based on their direction and reach
        if player.direction == "right":
            interaction_rect.x += player.width
            interaction_rect.width = reach
        elif player.direction == "left":
            interaction_rect.x -= reach
            interaction_rect.width = reach
        elif player.direction == "up":
            interaction_rect.y -= reach
            interaction_rect.height = reach
        elif player.direction == "down":
            interaction_rect.y += player.height
            interaction_rect.height = reach

        # Expand the interaction rectangle slightly to make it easier to trigger interactions
        if player.direction in ["left", "right"]:
            interaction_rect.y -= 8
            interaction_rect.height += 16
        else:
            interaction_rect.x -= 8
            interaction_rect.width += 16

        # Check for collisions with interactable objects in the room
        for obj in self.objects:
            interaction_func = GAME_OBJECT_DEFS[obj.type].get("on_interact")
            if not interaction_func:
                continue

            obj_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)

            if interaction_rect.colliderect(obj_rect):
                interaction_func(player, obj)
            
    def check_door_conditions(self) -> None:
        # If doors are already open, we don't need to check again
        if getattr(self, 'doors_opened', False):
            return

        #The switch MUST be pressed
        can_open = self.switch.state == "pressed"

        #If the chest spawned in this room, the player MUST have the bow
        if getattr(self, 'chest_in_room', False):
            if not getattr(self.player, 'has_bow', False):
                can_open = False

        # If all conditions are met, open the doors
        if can_open:
            for doorway in self.doorways:
                doorway.open = True
            
            settings.SOUNDS["door"].play()
            self.doors_opened = True


    def _generate_walls_and_floors(self) -> None:
        """
        Generates the walls and floors of the room, randomizing the various
        varieties of said tiles for visual variety.
        """
        floor = self.tilemap.add_layer("floor")

        for y in range(1, self.height + 1):
            for x in range(1, self.width + 1):
                if x == 1 and y == 1:
                    tile_id = settings.TILE_TOP_LEFT_CORNER
                elif x == 1 and y == self.height:
                    tile_id = settings.TILE_BOTTOM_LEFT_CORNER
                elif x == self.width and y == 1:
                    tile_id = settings.TILE_TOP_RIGHT_CORNER
                elif x == self.width and y == self.height:
                    tile_id = settings.TILE_BOTTOM_RIGHT_CORNER
                elif x == 1:
                    tile_id = random.choice(settings.TILE_LEFT_WALLS)
                elif x == self.width:
                    tile_id = random.choice(settings.TILE_RIGHT_WALLS)
                elif y == 1:
                    tile_id = random.choice(settings.TILE_TOP_WALLS)
                elif y == self.height:
                    tile_id = random.choice(settings.TILE_BOTTOM_WALLS)
                else:
                    tile_id = random.choice(settings.TILE_FLOORS)

                floor[y - 1][x - 1] = tile_id

    def _generate_entities(self) -> None:
        """Randomly creates an assortment of enemies for the player to fight."""
        for _ in range(10):
            enemy_type = random.choice(_ENEMY_TYPES)
            definition = ENTITY_DEFS[enemy_type]

            entity = Entity(
                x=random.randint(
                    settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE,
                    settings.VIRTUAL_WIDTH - settings.TILE_SIZE * 2 - 16,
                ),
                y=random.randint(
                    settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE,
                    settings.MAP_HEIGHT * settings.TILE_SIZE
                    + settings.MAP_RENDER_OFFSET_Y
                    - settings.TILE_SIZE
                    - 16,
                ),
                width=16,
                height=16,
                walk_speed=definition.get("walk_speed", 20),
                health=1,
                animation_defs=definition["animations"],
                states={},
            )

            entity.state_machine.states = {
                "walk": lambda sm, e=entity: EntityWalkState(e, sm),
                "idle": lambda sm, e=entity: EntityIdleState(e, sm),
            }
            entity.change_state("walk")
            self.entities.append(entity)

    def _generate_objects(self) -> None:
        """Randomly creates an assortment of obstacles for the player to navigate around."""
        # Create a switch in the room
        self.switch = GameObject(
            GAME_OBJECT_DEFS["switch"],
            random.randint(
                settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE,
                settings.VIRTUAL_WIDTH - settings.TILE_SIZE * 2 - 16,
            ),
            random.randint(
                settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE,
                settings.MAP_HEIGHT * settings.TILE_SIZE
                + settings.MAP_RENDER_OFFSET_Y
                - settings.TILE_SIZE
                - 16,
            ),
        )
        self.objects.append(self.switch)

        def press_switch() -> None:
            if self.switch.state == "unpressed":
                self.switch.state = "pressed"

        self.switch.on_collide = press_switch
        self.chest_in_room = False

        if not getattr(self.player, 'chest_spawned', False):
            if random.random() < settings.CHEST_SPAWN_CHANCE:
                while True:
                    chest_x = random.randint(2, self.width - 1) * settings.TILE_SIZE
                    chest_y = random.randint(2, self.height - 2) * settings.TILE_SIZE
                    
                    chest_rect = pygame.Rect(chest_x, chest_y, 16, 16)
                    switch_rect = pygame.Rect(self.switch.x, self.switch.y, self.switch.width, self.switch.height)
                    
                    if not chest_rect.colliderect(switch_rect):
                        break

                self.objects.append(
                    GameObject(GAME_OBJECT_DEFS["chest"], chest_x, chest_y)
                )
                self.player.chest_spawned = True
                self.chest_in_room = True

        # POT GENERATION 
        for y in range(2, self.height):
            for x in range(2, self.width):
                pot_x = x * settings.TILE_SIZE
                pot_y = y * settings.TILE_SIZE
                
                # Check if there is already an object (like the chest or switch) in this tile
                overlap = False
                pot_rect = pygame.Rect(pot_x, pot_y, 16, 16)
                for obj in self.objects:
                    obj_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                    if pot_rect.colliderect(obj_rect):
                        overlap = True
                        break
                
                # Only spawn the pot if the tile is empty
                if not overlap and random.randint(1, 20) == 1:
                    self.objects.append(
                        GameObject(GAME_OBJECT_DEFS["pot"], pot_x, pot_y)
                    )

        

    def render(
        self,
        surface: pygame.Surface,
        camera_offset_x: float = 0,
        camera_offset_y: float = 0,
    ) -> None:
        offset_x = self.adjacent_offset_x + camera_offset_x
        offset_y = self.adjacent_offset_y + camera_offset_y

        # Not tilemap.render(surface): offset_x/offset_y can carry the room
        # a full VIRTUAL_WIDTH/HEIGHT off-screen mid room-shift, and
        # Surface.subsurface() (used for 07-ultimate_fantasy's BattleState,
        # whose offset is fixed and always in-bounds) requires the rect to
        # land fully inside surface -- a plain blit per tile, sourcing the
        # gid/rect from the TileMap/Tileset instead of the old self.tiles
        # list and settings.frame("tiles", ...), has no such restriction.
        for y in range(self.height):
            for x in range(self.width):
                gid = self.tilemap.get_gid("floor", y, x)
                tileset = self.tilemap.tileset_for_gid(gid)
                surface.blit(
                    tileset.image,
                    (
                        x * settings.TILE_SIZE + self.render_offset_x + offset_x,
                        y * settings.TILE_SIZE + self.render_offset_y + offset_y,
                    ),
                    tileset.rect_for(gid),
                )

        for doorway in self.doorways:
            doorway.render(surface, offset_x, offset_y)

        for obj in self.objects:
            obj.render(surface, offset_x, offset_y)

        for entity in self.entities:
            if not entity.dead:
                entity.render(surface, offset_x, offset_y)

        # The player and projectiles are drawn using only the camera pan —
        # never this room's own adjacent_offset — matching the original,
        # where Player:render()/Projectile:render() take no room offset at
        # all. Their x/y already track the correct absolute (pre-camera-pan)
        # screen position on their own, including mid-tween during a room
        # shift; adding adjacent_offset on top (as tiles/entities do) would
        # draw them a full room-width off from where they actually are.
        #
        # While the player is near a doorway, clip their sprite to that
        # doorway's own opening rect (via gale.stencil, applied inside
        # Entity.render_sprite) instead of hiding them outright: the part
        # of the sprite still overlapping solid wall disappears, but the
        # part inside the opening keeps showing, so walking (or, mid
        # room-shift, tweening) through the gap reads as passing under/
        # through the archway rather than blinking out of existence.
        if self.player:
            self.player.visibility_clip_rect = _doorway_opening_for(
                self.player.get_collision_rect(), self._doorways_by_direction
            )
            self.player.render(surface, camera_offset_x, camera_offset_y)
            self.player.visibility_clip_rect = None

        for projectile in self.projectiles:
            if not _doorway_opening_for(
                projectile.get_collision_rect(), self._doorways_by_direction
            ):
                projectile.render(surface, camera_offset_x, camera_offset_y)
        
        for exp in self.explosions:
            exp.render(surface, offset_x, offset_y)

        for effect in self.particle_effects:
            effect.system.render(surface)

        
            