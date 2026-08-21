import random
import settings
from src.LogPair import LogPair
from src.MovingLogPair import MovingLogPair
from src.ShiftingLogPair import ShiftingLogPair

class NormalSpawnStrategy:
    def update(self, world, dt: float) -> None:
        
        world.logs_spawn_timer += dt
        if world.logs_spawn_timer >= settings.TIME_TO_SPAWN_LOGS:
            world.logs_spawn_timer = 0.0
            y = max(
                -settings.LOG_HEIGHT + 10,
                min(
                    world.last_log_y + random.randint(-20, 20),
                    settings.VIRTUAL_HEIGHT + 90 - settings.LOG_HEIGHT,
                ),
            )
            world.last_log_y = y
            world.logs.append(world.log_pair_factory.create(settings.VIRTUAL_WIDTH, y))


class HardSpawnStrategy:
    def __init__(self):
        self.next_spawn_time = random.uniform(1.2, 2.5)
        self.speed_multiplier = 1.0
        
    def update(self, world, dt: float) -> None:
        if self.speed_multiplier < 2.0:
            self.speed_multiplier += 0.03 * dt
            
        world.logs_spawn_timer += (dt * self.speed_multiplier)
        
        if world.logs_spawn_timer >= self.next_spawn_time:
            world.logs_spawn_timer = 0.0
            chance = random.random()
    
            if chance < settings.LOGS_BIT_POSIBILITY:
                base_gap = random.randint(settings.LOGS_GAP, settings.LOGS_GAP + 25)
            elif chance < settings.LOGS_MOVING_POSIBILITY:
                base_gap = random.randint(settings.LOGS_GAP - 10, settings.LOGS_GAP + 15)
            else:
                base_gap = random.randint(60, settings.LOGS_GAP)
            
            safe_bottom_y = settings.VIRTUAL_HEIGHT - settings.GROUND_HEIGHT - settings.LOG_HEIGHT - base_gap - 100
            max_y_diff = int(60 * (self.next_spawn_time / 1.5))
            
            y = max(
                -settings.LOG_HEIGHT + 30,
                min(
                    world.last_log_y + random.randint(-max_y_diff, max_y_diff),
                    safe_bottom_y
                ),
            )
            world.last_log_y = y

            if chance < settings.LOGS_BIT_POSIBILITY:
                speed = random.uniform(1.2, 3.5) 
                new_log = MovingLogPair(settings.VIRTUAL_WIDTH, y, base_gap, speed)
                
            elif chance < settings.LOGS_MOVING_POSIBILITY:
                target_y = random.randint(-settings.LOG_HEIGHT + 30, int(safe_bottom_y))
                new_log = ShiftingLogPair(settings.VIRTUAL_WIDTH, y, base_gap, target_y)
                
            else:
                new_log = LogPair(settings.VIRTUAL_WIDTH, y, base_gap)
                if random.random() < settings.PROBABILITY_POWERUP:
                    pu_x = settings.VIRTUAL_WIDTH + 15
                    pu_y = y + settings.LOG_HEIGHT + (base_gap / 2) - 32 
                    nuevo_powerup = world.powerup_factory.create(pu_x, pu_y)
                    world.powerups.append(nuevo_powerup)

            world.logs.append(new_log)

            self.next_spawn_time = random.uniform(1.2, 2.5)