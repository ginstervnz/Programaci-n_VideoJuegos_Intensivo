import pygame
import settings

class NormalMovementStrategy:
    def update(self, bird, dt: float) -> None:
        bird.vy += settings.GRAVITY * dt
        if bird.jumping:
            settings.SOUNDS["jump"].play()
            bird.vy = -settings.JUMP_TAKEOFF_SPEED
            bird.jumping = False

        bird.y += bird.vy * dt

class HardMovementStrategy:
    def __init__(self):
        self.current_speed = settings.BIRD_SPEED

    def update(self, bird, dt: float) -> None:

        max_speed = settings.BIRD_SPEED * 2.2
        if self.current_speed < max_speed:
            self.current_speed += 10.0 * dt

        bird.vy += settings.GRAVITY * dt

        if bird.jumping:
            settings.SOUNDS["jump"].play()
            bird.vy = -settings.JUMP_TAKEOFF_SPEED
            bird.jumping = False
        bird.y += bird.vy * dt

        keys = pygame.key.get_pressed()
        if keys[settings.KEY_LEFT]:
            bird.x -= self.current_speed * dt   
        if keys[settings.KEY_RIGHT]:
            bird.x += self.current_speed * dt
            
        bird.x = max(0, min(bird.x, settings.VIRTUAL_WIDTH - bird.width))