import pygame
import settings
from gale.particle_system import ParticleSystem

class Rocket:
    def __init__(self, x: int, y: int, is_special: bool = False) -> None:
        self.x = float(x)
        self.y = float(y)
        self.width = 8
        self.height = 16
        self.vy = -15 
        self.acceleration = -350 
        self.is_special = is_special # Flag for special shot
        self.active = True
        self.exploded = False
        self.trail_systems = []
        self.trail_timer = 0.1
        self.explosion_system = None

    def explode(self, impact_x: float, impact_y: float):
        self.exploded = True

        def update_active():
            self.active = False
        
        num_particles = 120 if self.is_special else 40
        self.explosion_system = ParticleSystem(impact_x, impact_y, num_particles, update_active)
        
        if self.is_special:
            self.explosion_system.set_life_time(0.3, 0.6)
            # Big explosion
            self.explosion_system.set_linear_acceleration(-2.0, 2.0, -2.0, 2.0)
            self.explosion_system.set_colors([(255, 100, 0, 255), (255, 20, 0, 0)]) # Orange and red 
            self.explosion_system.set_area_spread(20, 20)
        else:
            self.explosion_system.set_life_time(0.15, 0.3)
            self.explosion_system.set_linear_acceleration(-0.8, 0.8, -0.8, 0.8)
            self.explosion_system.set_colors([(255, 255, 0, 200), (255, 50, 0, 0)]) 
            self.explosion_system.set_area_spread(4, 4)
            
        self.explosion_system.generate()
    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def collides(self, another) -> bool:
        return self.get_collision_rect().colliderect(another.get_collision_rect())

    def update(self, dt: float) -> None:
        if not self.exploded:
          
            self.vy += self.acceleration * dt
            self.y += self.vy * dt
            self.trail_timer -= dt

            if self.trail_timer <= 0:
                smoke = ParticleSystem(self.x + 4, self.y + 16, 2)
                smoke.set_life_time(0.1, 0.25)
                smoke.set_linear_acceleration(-0.1, 0.2, 0.5, 1.2)
                smoke.set_colors([(150, 150, 150, 120), (100, 100, 100, 0)]) 
                smoke.set_area_spread(1, 1)
                smoke.generate()
                
                self.trail_systems.append(smoke)
                self.trail_timer = 0.05
                
            if self.y < 0:
                self.active = False

        for ts in self.trail_systems:
            ts.update(dt)
        if self.explosion_system:
            self.explosion_system.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        if not self.exploded:
            
            tex = settings.TEXTURES["rocket_special"] if self.is_special else settings.TEXTURES["rocket_projectile"]
            surface.blit(tex, (self.x, self.y))
        
        for ts in self.trail_systems:
            ts.render(surface)
            
        if self.explosion_system:
            self.explosion_system.render(surface)