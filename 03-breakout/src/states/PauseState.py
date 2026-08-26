import pygame

from gale.state import BaseState
from gale.input_handler import InputData
from gale.text import render_text

import settings


class PauseState(BaseState):
    def enter(self, **params: dict) -> None:
        self.level = params["level"]
        self.paddle = params["paddle"]
        self.balls = params["balls"]
        self.brickset = params["brickset"]
        self.score = params["score"]
        self.lives = params["lives"]
        self.live_factor = params["live_factor"]
        self.points_to_next_live = params["points_to_next_live"]
        self.powerups = params["powerups"]
        settings.SOUNDS["pause"].play()
        self.sticky_timer = params.get("sticky_timer", 0)
        self.radiactive_timer = params.get("radiactive_timer", 0)
        self.rocket_timer = params.get("rocket_timer", 0)
        self.rockets = params.get("rockets", [])
        self.arrow_angle = params.get("arrow_angle", 0)
        self.arrow_dir = params.get("arrow_dir", 1)
        self.rocket_shots_left = params.get("rocket_shots_left", 0)
        self.screen_shake_timer = params.get("screen_shake_timer", 0)
        self.selected_option = 0
        self.lightning_rays = params.get("lightning_rays", [])
        self.flash_timer = params.get("flash_timer", 0)

    def render(self, surface: pygame.Surface) -> None:
        heart_x = settings.VIRTUAL_WIDTH - 120

        i = 0
        # Draw filled hearts
        while i < self.lives:
            surface.blit(
                settings.TEXTURES["hearts"], (heart_x, 5), settings.FRAMES["hearts"][0]
            )
            heart_x += 11
            i += 1

        # Draw empty hearts
        while i < 3:
            surface.blit(
                settings.TEXTURES["hearts"], (heart_x, 5), settings.FRAMES["hearts"][1]
            )
            heart_x += 11
            i += 1

        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["tiny"],
            settings.VIRTUAL_WIDTH - 80,
            5,
            (255, 255, 255),
        )

        self.brickset.render(surface)
        self.paddle.render(surface)

        render_text(
            surface,
            "Pause",
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH // 2,
            settings.VIRTUAL_HEIGHT // 3,
            settings.COLOR_WHITE,
            center=True,
        )
        color_resume = settings.BLUE_COLOR if getattr(self, 'selected_option', 0) == 0 else settings.COLOR_WHITE
        render_text(
            surface,
            "Resume",
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH // 2,
            settings.VIRTUAL_HEIGHT // 2,
            color_resume,
            center=True,
        )
        color_retry = settings.BLUE_COLOR if getattr(self, 'selected_option', 0) == 1 else settings.COLOR_WHITE
        render_text(
            surface,
            "Restart Run",
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH // 2,
            settings.VIRTUAL_HEIGHT // 2 + 20,
            color_retry,
            center=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "move_up" and input_data.pressed:
            self.selected_option = 0 if self.selected_option == 1 else 1
            settings.SOUNDS["paddle_hit"].play()
        elif input_id == "move_down" and input_data.pressed:
            self.selected_option = 1 if self.selected_option == 0 else 0
            settings.SOUNDS["paddle_hit"].play()
        elif input_id == "enter" and input_data.pressed:
            if self.selected_option == 0:
                self.resume_game()
            elif self.selected_option == 1:
                self.state_machine.change("start")
        elif input_id == "pause" and input_data.pressed:
            self.resume_game()
           
           
    def resume_game(self) -> None:
        self.state_machine.change(
            "play",
            resume=True,
            level=self.level,
            score=self.score,
            lives=self.lives,
            paddle=self.paddle,
            balls=self.balls,
            brickset=self.brickset,
            points_to_next_live=self.points_to_next_live,
            live_factor=self.live_factor,
            powerups=self.powerups,
            sticky_timer=self.sticky_timer,
            radiactive_timer=self.radiactive_timer,
            rocket_timer=self.rocket_timer,
            rockets=self.rockets,
            arrow_angle=self.arrow_angle,
            arrow_dir=self.arrow_dir,
            rocket_shots_left=self.rocket_shots_left,
            screen_shake_timer=self.screen_shake_timer,
            lightning_rays=getattr(self, "lightning_rays", []),
            flash_timer=getattr(self, "flash_timer", 0),
        )