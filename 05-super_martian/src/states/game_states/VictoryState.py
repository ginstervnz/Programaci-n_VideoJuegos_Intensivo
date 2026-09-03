from typing import Dict, Any
import pygame
import sys

from gale.state import BaseState
from gale.timer import Timer
from gale.text import render_text
from gale.input_handler import InputData
import settings

class VictoryState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.level = enter_params.get("level", 1)
        self.game_level = enter_params.get("game_level")
        self.player = enter_params.get("player")
        self.camera = enter_params.get("camera")
        self.bar_height = 0
        settings.SOUNDS["victory"].play()
        Timer.tween(1.5, [(self, {"bar_height": settings.VIRTUAL_HEIGHT // 2})])

        if self.level == 3:
            self.current_option = 1
            self.show_menu = False
            Timer.after(1.5, self.enable_menu)
        else:
           
            Timer.after(2.0, lambda: self.state_machine.change(
                "level_transition", 
                level=self.level + 1,
                saved_score=self.player.score,
                saved_coins=self.player.coins_counter
            ))
      
    def enable_menu(self):
        self.show_menu = True

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        self.game_level.render(surface, self.camera)
        self.player.render(surface, self.camera)
        
        # Draw the TOP cinematic bar
        pygame.draw.rect(
            surface, 
            (0, 0, 0), 
            (0, 0, settings.VIRTUAL_WIDTH, int(self.bar_height))
        )
        
        # Draw the BOTTOM cinematic bar
        pygame.draw.rect(
            surface, 
            (0, 0, 0), 
            (0, settings.VIRTUAL_HEIGHT - int(self.bar_height), settings.VIRTUAL_WIDTH, int(self.bar_height))
        )

        # Render the final Victory Menu ONLY on level 3 and after the curtains close
        if self.level == 3 and getattr(self, "show_menu", False):
            
            render_text(
                surface, "VICTORY!", settings.FONTS["medium"], 
                settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 3, 
                (255, 215, 0), center=True, shadowed=True
            )
            
            color_retry = (255, 255, 255) if self.current_option == 1 else (100, 100, 100)
            render_text(
                surface, "Retry", settings.FONTS["small"], 
                settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2, 
                color_retry, center=True, shadowed=True
            )
            
            color_quit = (255, 255, 255) if self.current_option == 2 else (100, 100, 100)
            render_text(
                surface, "Quit", settings.FONTS["small"], 
                settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2 + 20, 
                color_quit, center=True, shadowed=True
            )

    
    def on_input(self, input_id: str, input_data: InputData) -> None:
        if self.level == 3 and input_data.pressed:
            if input_id == "up" or input_id == "down":
                self.current_option = 2 if self.current_option == 1 else 1
                settings.SOUNDS["select"].play()
            elif input_id == "enter":
                if self.current_option == 1:
                    # Restart the game from level 1 or the start screen
                    self.state_machine.change("start") 
                else:
                    # Quit the application
                    pygame.quit()
                    sys.exit()