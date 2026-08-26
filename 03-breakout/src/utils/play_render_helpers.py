import random
import pygame
import settings
from gale.text import render_text

def render_lightning_rays(surface, rays):
    if not rays:
        return
    for ray in rays:
        start = ray["start"]
        end = ray["end"]
        steps = 4 
        points = [start]
        dx = (end[0] - start[0]) / steps
        dy = (end[1] - start[1]) / steps
        for j in range(1, steps):
            px = start[0] + dx * j + random.randint(-12, 12)
            py = start[1] + dy * j + random.randint(-12, 12)
            points.append((px, py))
        points.append(end)
        pygame.draw.lines(surface, (0, 255, 255), False, points, 3)
        pygame.draw.lines(surface, (255, 255, 255), False, points, 1)

def render_electro_aura(surface, ball):
    if getattr(ball, 'electro_charges', 0) > 0:
        center_x = ball.x + ball.width / 2
        center_y = ball.y + ball.height / 2
        for _ in range(4):
            end_x = center_x + random.randint(-12, 12)
            end_y = center_y + random.randint(-12, 12)
            pygame.draw.line(surface, (0, 255, 255), (center_x, center_y), (end_x, end_y), 2)
            pygame.draw.line(surface, (255, 255, 255), (center_x, center_y), (end_x, end_y), 1)

def is_paddle_visible(paddle, rocket_timer, sticky_timer):
    time_left = rocket_timer if getattr(paddle, 'has_rockets', False) else (sticky_timer if getattr(paddle, 'is_sticky', False) else 0)
    draw_paddle = True
    if 0 < time_left <= 3:
        if time_left > 1.5:
            draw_paddle = int(time_left * 5) % 2 == 0
        elif time_left > 0.5:
            draw_paddle = int(time_left * 10) % 2 == 0
        else:
            draw_paddle = int(time_left * 20) % 2 == 0
            
    return draw_paddle

def render_stuck_arrow(surface, ball, angle):
    if getattr(ball, 'stuck', False):
        rotated_arrow = pygame.transform.rotate(settings.TEXTURES["arrow_shot"], -angle)
        new_rect = rotated_arrow.get_rect()
        new_rect.centerx = ball.x + ball.width // 2
        new_rect.centery = ball.y + ball.height // 2
        surface.blit(rotated_arrow, new_rect.topleft)

def apply_screen_shake(main_surface, world_surf, timer):
    shake_x = 0
    shake_y = 0
    if timer > 0:
        shake_x = random.randint(-4, 4)
        shake_y = random.randint(-4, 4)
    main_surface.blit(world_surf, (shake_x, shake_y))

def render_flash(surface, timer):
    if timer > 0:
        flash_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        alpha = int((timer / 0.1) * 150)
        flash_surf.fill((200, 255, 255, max(0, alpha))) 
        surface.blit(flash_surf, (0, 0))

def render_hud(surface, lives, score):
    heart_x = settings.VIRTUAL_WIDTH - 120
    i = 0
    while i < lives:
        surface.blit(settings.TEXTURES["hearts"], (heart_x, 5), settings.FRAMES["hearts"][0])
        heart_x += 11
        i += 1
    while i < 3:
        surface.blit(settings.TEXTURES["hearts"], (heart_x, 5), settings.FRAMES["hearts"][1])
        heart_x += 11
        i += 1
    render_text(surface, f"Score: {score}", settings.FONTS["tiny"], settings.VIRTUAL_WIDTH - 80, 5, (255, 255, 255))