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

def compute_convex_hull(points):
    points = sorted(set(points))
    if len(points) <= 2: return points
    
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
        
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0: lower.pop()
        lower.append(p)
        
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0: upper.pop()
        upper.append(p)
        
    return lower[:-1] + upper[:-1]


def update_quantum_nodes(state, dt):
    if getattr(state, 'quantum_timer', 0) > 0:
        state.quantum_timer -= dt
        
        for node in getattr(state, 'quantum_nodes', []):
            node["x"] += node["vx"] * dt
            node["y"] += node["vy"] * dt
            
            if node["x"] < 0 or node["x"] > settings.VIRTUAL_WIDTH:
                node["vx"] *= -1
                node["x"] = max(0, min(node["x"], settings.VIRTUAL_WIDTH))
                
            floor_y = settings.VIRTUAL_HEIGHT
            ceil_y = settings.VIRTUAL_HEIGHT - 80 #Limite Y for shield
            if node["y"] < ceil_y or node["y"] > floor_y:
                node["vy"] *= -1
                node["y"] = max(ceil_y, min(node["y"], floor_y))

        nodes = getattr(state, 'quantum_nodes', [])
        points = [(n["x"], n["y"]) for n in nodes]
        points.append((state.paddle.x, state.paddle.y + state.paddle.height))
        points.append((state.paddle.x + state.paddle.width, state.paddle.y + state.paddle.height))
        
        state.quantum_hull = compute_convex_hull(points)

def check_quantum_bounce(state, ball):
    if getattr(state, 'quantum_timer', 0) > 0 and hasattr(state, 'quantum_hull'):
        hull = state.quantum_hull
        if len(hull) < 3: return
        
        bx = ball.x + ball.width / 2
        by = ball.y + ball.height
        bounce_y = None
        normal = None
        
    
        for i in range(len(hull)):
            p1, p2 = hull[i], hull[(i + 1) % len(hull)]
            min_x, max_x = min(p1[0], p2[0]), max(p1[0], p2[0])
            
            if min_x <= bx <= max_x and max_x - min_x > 0.1:
                t = (bx - p1[0]) / (p2[0] - p1[0])
                line_y = p1[1] + t * (p2[1] - p1[1])
                
              
                if bounce_y is None or line_y < bounce_y:
                    bounce_y = line_y
                    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
                    nx, ny = -dy, dx 
                    length = math.hypot(nx, ny)
                    if length != 0:
                        nx, ny = nx / length, ny / length
                        if ny > 0: nx, ny = -nx, -ny 
                        normal = (nx, ny)

        if bounce_y is not None and by >= bounce_y and ball.vy > 0:
            ball.y = bounce_y - ball.height - 1
            
            if normal:
                nx, ny = normal
                dot_product = ball.vx * nx + ball.vy * ny
                ball.vx = ball.vx - 2 * dot_product * nx
                ball.vy = ball.vy - 2 * dot_product * ny
                ball.vx *= 1.05 
                ball.vy *= 1.05
            ball.vy = -abs(ball.vy)
            if ball.vy > -120:
                ball.vy = -120

            settings.SOUNDS["hit_shield"].stop()
            settings.SOUNDS["hit_shield"].play()
            state.screen_shake_timer = 0.15
            state.flash_timer = 0.05