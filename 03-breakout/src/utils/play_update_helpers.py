import math
import pygame
import settings

def update_visual_timers(state, dt):
    if getattr(state, 'screen_shake_timer', 0) > 0:
        state.screen_shake_timer -= dt
    if getattr(state, 'flash_timer', 0) > 0:
        state.flash_timer -= dt
    if hasattr(state, 'lightning_rays'):
        for ray in state.lightning_rays:
            ray["life"] -= dt
        state.lightning_rays = [r for r in state.lightning_rays if r["life"] > 0]

def release_stuck_balls(state):
    action_performed = False
    for ball in state.balls:
        if getattr(ball, 'stuck', False):
            ball.stuck = False
            speed = 160 
            radian_angle = math.radians(getattr(state, 'arrow_angle', 0))
            ball.vx = speed * math.sin(radian_angle)
            ball.vy = -speed * math.cos(radian_angle)
            action_performed = True
    return action_performed

def process_sticky_and_arrow(state, dt):
    if getattr(state.paddle, 'is_sticky', False):
        state.sticky_timer -= dt
        if state.sticky_timer <= 0:
            state.paddle.is_sticky = False
            release_stuck_balls(state)

    for ball in state.balls:
        if getattr(ball, 'stuck', False):
            ball.x = state.paddle.x + ball.stuck_offset
            ball.y = state.paddle.y - ball.height
            state.arrow_angle += state.ARROW_ROTATE_SPEED * dt * state.arrow_dir
            if abs(state.arrow_angle) >= state.ARROW_MAX_ANGLE:
                state.arrow_angle = state.ARROW_MAX_ANGLE * state.arrow_dir
                state.arrow_dir *= -1

def process_rocket_system(state, dt):
    if getattr(state.paddle, 'has_rockets', False):
        state.rocket_timer -= dt
        if state.rocket_timer <= 0:
            state.paddle.has_rockets = False
    
    for rocket in getattr(state, 'rockets', []):
        rocket.update(dt)
        if not getattr(rocket, 'exploded', False) and rocket.collides(state.brickset):
            brick = state.brickset.get_colliding_brick(rocket.get_collision_rect())
            if brick and not brick.broken:
                brick.hit()
                state.score += brick.score()
                
                if getattr(rocket, 'is_special', False):
                    state.screen_shake_timer = 0.4 
                    settings.SOUNDS["explosion"].play() 
                    blast_rect = pygame.Rect(rocket.x - 32, brick.y - 32, 72, 64)
                    for pos, other_brick in state.brickset.bricks.items():
                        if not other_brick.broken and other_brick.get_collision_rect().colliderect(blast_rect):
                            other_brick.hit()
                            state.score += other_brick.score()

                impact_x = rocket.x + rocket.width / 2
                impact_y = brick.y + brick.height
                rocket.explode(impact_x, impact_y)
        
    state.rockets = [r for r in getattr(state, 'rockets', []) if r.active]

def trigger_electro_storm(state, ball, brick):
    if getattr(ball, 'electro_charges', 0) > 0:
        ball.electro_charges -= 1 
        settings.SOUNDS["eletro_efect"].stop()
        settings.SOUNDS["eletro_efect"].play()
        state.flash_timer = 0.1 
        state.screen_shake_timer = 0.2 
        
        active_bricks = [b for b in state.brickset.bricks.values() if not b.broken and b != brick]
        active_bricks.sort(key=lambda b: math.hypot(b.x - brick.x, b.y - brick.y))
        targets = active_bricks[:3]
        
        for target in targets:
            target.hit()
            state.score += target.score()
            if not hasattr(state, 'lightning_rays'):
                state.lightning_rays = []
            state.lightning_rays.append({
                "start": (brick.x + 16, brick.y + 8),
                "end": (target.x + 16, target.y + 8),
                "life": 0.2 
            })