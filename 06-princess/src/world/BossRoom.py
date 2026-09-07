import pygame
import settings
from src.world.Room import Room
from src.Boss import Boss
from src.definitions.entity import ENTITY_DEFS
from src.definitions.game_objects import GAME_OBJECT_DEFS
from src.GameObject import GameObject


class BossRoom(Room):
    def __init__(self, player, on_game_over, entry_door_direction):
        self.entry_door = entry_door_direction
        super().__init__(player, on_game_over)
        pygame.mixer.music.load(settings.MUSIC["boss"])
        pygame.mixer.music.play(-1)
        self.boss_defeated = False
        self.key_spawned = False
        self.doorways = [d for d in self.doorways if d.direction == self.entry_door]

    def _generate_objects(self) -> None:
        pass

    def _generate_entities(self) -> None:
        pass

    def check_door_conditions(self) -> None:
        if getattr(self, 'doors_opened', False):
            return

        if getattr(self.player, 'has_boss_key', False):
            for doorway in self.doorways:
                doorway.open = True
            settings.SOUNDS["door"].play()
            self.doors_opened = True
            self.player.has_boss_key = False
        pass

    def _generate_entities(self) -> None:
        # Center the boss in the room, but adjust its position based on the entry door direction
        boss_x = settings.MAP_RENDER_OFFSET_X + (settings.MAP_WIDTH * settings.TILE_SIZE) // 2 - 25
        boss_y = settings.MAP_RENDER_OFFSET_Y + (settings.MAP_HEIGHT * settings.TILE_SIZE) // 2 - 20

        if self.entry_door == "left":
            boss_x = settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH * settings.TILE_SIZE - 85
        elif self.entry_door == "right":
            boss_x = settings.MAP_RENDER_OFFSET_X + 45
        elif self.entry_door == "top":
            boss_y = settings.MAP_RENDER_OFFSET_Y + settings.MAP_HEIGHT * settings.TILE_SIZE - 80
        elif self.entry_door == "bottom":
            boss_y = settings.MAP_RENDER_OFFSET_Y + 45

        # Create the boss entity and add it to the room's entities
        definition = ENTITY_DEFS["fire_worm"]
        self.boss = Boss(boss_x, boss_y, definition)
        self.boss.change_state("idle")
        self.entities.append(self.boss)

    def update(self, dt: float) -> None:
        super().update(dt)

        if self.boss.health <= 0 and not self.boss_defeated:
            self.boss_defeated = True
            self.death_timer = 0.0 
            pygame.mixer.music.load(settings.MUSIC["victory"])
            pygame.mixer.music.play(-1)

        if self.boss_defeated and not self.key_spawned:
            self.death_timer += dt
            
            if self.death_timer >= 1.2:
                self.key_spawned = True
                
                key_x = self.boss.x + 5
                key_y = self.boss.y + 35 
                
                key = GameObject(GAME_OBJECT_DEFS["boss_key"], key_x, key_y)
                
                def collect_key(player, obj):
                    player.has_boss_key = True
                    
                key.on_consume = collect_key
                self.objects.append(key)