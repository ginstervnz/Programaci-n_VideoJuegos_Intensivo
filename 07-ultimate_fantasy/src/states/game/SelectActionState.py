"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class SelectActionState: menu of the acting
entity's own actions.actions (whatever list its ENTITY_DEFS entry
defines) plus a trailing "Nothing" (skip turn) entry.
"""

from typing import Any, Callable, Dict, List

import pygame

from gale.state import BaseState
from gale.timer import Timer

import settings
from src.gui.Menu import Menu


class SelectActionState(BaseState):
    def enter(
        self, battle_state: Any, entity: Any, on_action_selected: Callable[[], None]
    ) -> None:
        self.battle_state = battle_state
        self.entity = entity
        self.on_action_selected = on_action_selected

        items = [
            (action["name"], self._make_selector(action)) for action in entity.actions
        ]
        items.append(("Nothing", self._nothing))

        self.menu = Menu(
            0, settings.VIRTUAL_HEIGHT - 64, settings.VIRTUAL_WIDTH, 64, items=items
        )

    def _make_selector(self, action: Dict[str, Any]) -> Callable[[], None]:
        return lambda: self._select_action(action)

    def _select_action(self, action: Dict[str, Any]) -> None:
        # Check stamina requirement
        cost = action.get("fatigue_cost", 5)
        if hasattr(self.entity, "turn_timer") and (self.entity.turn_timer + cost) > self.entity.max_fatigue:
            settings.SOUNDS["error"].play()
            return

        from src.states.game.SelectTargetState import SelectTargetState

        targets: List[Any] = self.battle_state.enemies if action["target_type"] == "enemy" else list(self.battle_state.party.characters.values())
        self.state_machine.pop()

        if action["require_target"]:
            self.state_machine.push(
                SelectTargetState(self.state_machine),
                battle_state=self.battle_state,
                targets=targets,
                on_target_selected=lambda target: self._resolve(action, target),
            )
        else:
            alive_targets = [target for target in targets if not target.dead]
            original_x = self.entity.x
            bump_x = original_x + (15 if hasattr(self.entity, "hpiv") else -15)

            def hit_all_targets():
                amount = action["func"](self.entity, alive_targets, action.get("strength"))
                settings.SOUNDS[action["sound_effect"]].play()
                
                # Apply fatigue cost
                if hasattr(self.entity, "turn_timer"):
                    self.entity.turn_timer = min(self.entity.turn_timer + cost, self.entity.max_fatigue)
                    if hasattr(self.entity, "rest_time"):
                        self.entity.rest_time = self.entity.turn_timer
                    if hasattr(self.entity, "fatigue_bar"):
                        self.entity.fatigue_bar.value = self.entity.turn_timer

                for target in alive_targets:
                    Timer.tween(0.5, [(target.energy_bar, {"value": target.current_hp})])
                
                self._apply_hit_effects(alive_targets, action)
                Timer.tween(0.1, [(self.entity, {"x": original_x})], on_finish=lambda e=self.entity, ox=original_x: [setattr(e, "x", ox), self._show_result(f"{action['name']} for {amount} HP to each target.")])
            
            Timer.tween(0.1, [(self.entity, {"x": bump_x})], on_finish=hit_all_targets)

    def _resolve(self, action: Dict[str, Any], target: Any) -> None:
        original_x = self.entity.x
        bump_x = original_x + (15 if hasattr(self.entity, "hpiv") else -15)
        cost = action.get("fatigue_cost", 5)

        def hit_target():
            amount = action["func"](self.entity, target, action.get("strength"))
            settings.SOUNDS[action["sound_effect"]].play()
            
            # Apply fatigue cost 
            if hasattr(self.entity, "turn_timer"):
                self.entity.turn_timer = min(self.entity.turn_timer + cost, self.entity.max_fatigue)
                if hasattr(self.entity, "rest_time"):
                    self.entity.rest_time = self.entity.turn_timer
                if hasattr(self.entity, "fatigue_bar"):
                    self.entity.fatigue_bar.value = self.entity.turn_timer

            Timer.tween(0.5, [(target.energy_bar, {"value": target.current_hp})])
            self._apply_hit_effects([target], action)
            Timer.tween(0.1, [(self.entity, {"x": original_x})], on_finish=lambda e=self.entity, ox=original_x: [setattr(e, "x", ox), self._show_result(f"{action['name']} for {amount} HP to {target.name}.")])

        Timer.tween(0.1, [(self.entity, {"x": bump_x})], on_finish=hit_target)

    def _show_result(self, message: str) -> None:
        from src.states.game.BattleMessageState import BattleMessageState

        self.state_machine.push(
            BattleMessageState(self.state_machine),
            battle_state=self.battle_state,
            message=message,
            on_close=self.on_action_selected,
        )


    # --- Shake and Particles ---
    def _apply_hit_effects(self, targets: list, action: dict) -> None:
        name = action["name"]
        if "Heal" in name:
            colors = [(0, 255, 0, 255), (100, 255, 100, 255)]
        elif "Flame" in name:
            colors = [(255, 100, 0, 255), (255, 165, 0, 255)]
        elif "Arrows" in name:
            colors = [(200, 200, 200, 255), (255, 255, 255, 255)]
        else:
            colors = [(255, 0, 0, 255), (255, 100, 100, 255)]

        def shake_target(t: Any, ox: float):
            Timer.tween(0.05, [(t, {"x": ox + 4})], on_finish=lambda:
                Timer.tween(0.05, [(t, {"x": ox - 4})], on_finish=lambda:
                    Timer.tween(0.05, [(t, {"x": ox})], on_finish=lambda: setattr(t, "x", ox))
                )
            )

        for target in targets:
            self.battle_state.spawn_particles(target.x + target.width / 2, target.y + target.height / 2, colors)
            
            if hasattr(self, "entity") and target == self.entity:
                continue
    
            shake_target(target, target.x)


    def _nothing(self) -> None:
        self.state_machine.pop()
        self.on_action_selected()

    def update(self, dt: float) -> None:
        for enemy in self.battle_state.enemies:
            if not enemy.dead:
                enemy.update(dt)

        self.menu.update(dt)
        for effect in self.battle_state.particle_effects:
            effect.system.update(dt)
        self.battle_state.particle_effects = [e for e in self.battle_state.particle_effects if e.active]

    def on_input(self, input_id: str, input_data: Any) -> None:
        if not input_data.pressed:
            return

        if input_id == "move_up":
            self.menu.navigate((0, -1))
        elif input_id == "move_down":
            self.menu.navigate((0, 1))
        elif input_id == "enter":
            self.menu.confirm()

    def render(self, surface: pygame.Surface) -> None:
        self.menu.render(surface)
