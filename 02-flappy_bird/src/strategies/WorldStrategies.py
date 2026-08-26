import random
import settings
import pygame



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
        self.speed_multiplier = 1.0
        # Roll the dice for the first log 
        self.next_chance = random.random()
        self._set_timer_for_next_log()

    def _set_timer_for_next_log(self) -> None: #Helper funcion for spanw logs
        if self.next_chance < settings.LOGS_BIT_POSIBILITY:
            self.next_spawn_time = random.uniform(2.5, 3.5)
        else:
            self.next_spawn_time = random.uniform(1.2, 2.5)
        
    def update(self, world, dt: float) -> None:
        if self.speed_multiplier < 2.0:
            self.speed_multiplier += 0.03 * dt
            
        world.logs_spawn_timer += (dt * self.speed_multiplier)
        
        if world.logs_spawn_timer >= self.next_spawn_time:
            world.logs_spawn_timer = 0.0
            chance = self.next_chance

            #Log chance spawn
            if chance < settings.LOGS_BIT_POSIBILITY:
                log_type = "biting"
                base_gap = random.randint(settings.LOGS_GAP + 60, settings.LOGS_GAP + 110)
            elif chance < settings.LOGS_MOVING_POSIBILITY:
                log_type = "shifting"
                base_gap = random.randint(settings.LOGS_GAP - 10, settings.LOGS_GAP + 15)
            else:
                log_type = "normal"
                base_gap = random.randint(60, settings.LOGS_GAP)

            #Safe bottom and Height
            safe_bottom_y = settings.VIRTUAL_HEIGHT - settings.GROUND_HEIGHT - settings.LOG_HEIGHT - base_gap - 100 
            max_y_diff = int(60 * (self.next_spawn_time / 1.5))
            
            y = max(
                -settings.LOG_HEIGHT + 20,
                min(
                    world.last_log_y + random.randint(-max_y_diff, max_y_diff),
                    safe_bottom_y
                ),
            )
            world.last_log_y = y

            #Create logs with save range
            if log_type == "biting":
                speed = random.uniform(1.0, 2.2) 
                new_log = world.moving_log_factory.create(settings.VIRTUAL_WIDTH, y, properties={"gap": base_gap, "speed": speed})
                
            elif log_type == "shifting":
                target_y = random.randint(-settings.LOG_HEIGHT + 30, int(safe_bottom_y))
                new_log = world.shifting_log_factory.create(settings.VIRTUAL_WIDTH, y, properties={"gap": base_gap, "target_y": target_y})
            else:
                new_log = world.log_pair_factory.create(settings.VIRTUAL_WIDTH, y, properties={"gap": base_gap})


            world.logs.append(new_log)

            #Roll a dice for next spanw
            self.next_chance = random.random()
            self._set_timer_for_next_log()

            # Safe area of powerup spawn
            if random.random() < settings.PROBABILITY_POWERUP:
    
                medium_area = (settings.MAIN_SCROLL_SPEED * self.next_spawn_time) / 2
                pu_x = settings.VIRTUAL_WIDTH + medium_area
                pu_y = random.randint(20, settings.VIRTUAL_HEIGHT - settings.GROUND_HEIGHT - 40)
                check_area = pygame.Rect(pu_x, pu_y, 16, 16)
                
                if not world.collides(check_area):
                    nuevo_powerup = world.powerups_abstract_factory.get_factory("GhostPowerUp").create(pu_x, pu_y)
                    world.powerups.append(nuevo_powerup)
            
         

            
