"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class TakeTurnState: drives one full round of
battle -- every living party member acts (in slot order), then every
living enemy acts (in list order, AI picking a uniformly random action
among its own, guaranteed to hit a living target), repeating round after
round until one side is wiped. Also handles the victory (EXP/level-up)
and defeat (game over) end-of-battle flows.
"""

import math
import random
from typing import Any

import pygame

from gale.state import BaseState
from gale.timer import Timer

import settings


class TakeTurnState(BaseState):
    def enter(self, battle_state: Any, entity: Any) -> None: # <--- RECIBE LA ENTITY
        self.battle_state = battle_state
        self.entity = entity
        self.enemy_attacks_in_a_row = 0
        
        if self.entity.dead:
            self.state_machine.pop()
            return

        if hasattr(self.entity, "hpiv"):
            self._take_party_turn()
        else:
            self._take_enemy_turn()
    
    def _party_keys(self):
        return sorted(self.battle_state.party.characters.keys())

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

    # -- party turns ---------------------------------------------------

    def _take_party_turn(self) -> None:
        from src.states.game.BattleMessageState import BattleMessageState

        self.state_machine.push(
            BattleMessageState(self.state_machine),
            battle_state=self.battle_state,
            message=f"Turn for {self.entity.name}! Select an action.",
            on_close=self._prompt_action,
        )
    
    def _prompt_action(self) -> None:
        from src.states.game.SelectActionState import SelectActionState

        self.state_machine.push(
            SelectActionState(self.state_machine),
            battle_state=self.battle_state,
            entity=self.entity,
            on_action_selected=self._check_battle_end,
        )

    # -- enemy turns ----------------------------------------------------

    def _take_enemy_turn(self) -> None:
        enemy = self.entity

        self.enemy_attacks_in_a_row += 1
        action = random.choice(enemy.actions)
        cost = action.get("fatigue_cost", 5)

        # If the enemy is too fatigued to perform the action, it skips the turn to rest
        if hasattr(enemy, "turn_timer") and (enemy.turn_timer + cost) > enemy.max_fatigue:
            def show_rest_message():
                from src.states.game.BattleMessageState import BattleMessageState
                def on_message_close() -> None:
                    self.enemy_attacks_in_a_row = 0
                    self._check_battle_end()
                
                self.state_machine.push(
                    BattleMessageState(self.state_machine),
                    battle_state=self.battle_state,
                    message=f"{enemy.name} is resting to recover stamina.",
                    on_close=on_message_close,
                )
            
            # Pause briefly so the player sees the turn change, then show the message
            Timer.after(0.3, show_rest_message)
            return

        targets = list(self.battle_state.party.characters.values()) if action["target_type"] == "enemy" else self.battle_state.enemies
        target_label = "you" if action["target_type"] == "enemy" else "them"
        alive_targets = [target for target in targets if not target.dead]
        
        if not alive_targets:
            self._check_battle_end()
            return

        original_x = enemy.x
        bump_x = original_x - 15 

        def hit_targets():
            # Update Enemy UI 
            if hasattr(enemy, "turn_timer"):
                enemy.turn_timer = min(enemy.turn_timer + cost, enemy.max_fatigue)
                if hasattr(enemy, "fatigue_bar"):
                    enemy.fatigue_bar.value = enemy.turn_timer

            if action["require_target"]:
                target = random.choice(alive_targets)
                amount = action["func"](enemy, target, action.get("strength"))
                settings.SOUNDS[action["sound_effect"]].play()
                Timer.tween(0.5, [(target.energy_bar, {"value": target.current_hp})])
                self._apply_hit_effects([target], action)
                message = f"{enemy.name} used {action['name']} for {amount} HP on {target.name}."
            else:
                amount = action["func"](enemy, alive_targets, action.get("strength"))
                settings.SOUNDS[action["sound_effect"]].play()
                for target in alive_targets:
                    Timer.tween(0.5, [(target.energy_bar, {"value": target.current_hp})])
                self._apply_hit_effects(alive_targets, action)
                message = f"{enemy.name} used {action['name']} for {amount} HP on all of {target_label}."
            
            Timer.tween(0.1, [(enemy, {"x": original_x})], on_finish=lambda e=enemy, ox=original_x: [setattr(e, "x", ox), show_message(message)])

        def show_message(message: str):
            from src.states.game.BattleMessageState import BattleMessageState
            def on_message_close() -> None:
                if self.enemy_attacks_in_a_row < 3 and enemy.klass == "boss" and random.randint(1, 3) == 1:
                    self._take_enemy_turn()
                else:
                    self.enemy_attacks_in_a_row = 0
                    self._check_battle_end()
            self.state_machine.push(
                BattleMessageState(self.state_machine),
                battle_state=self.battle_state,
                message=message,
                on_close=on_message_close,
            )

        Timer.tween(0.1, [(enemy, {"x": bump_x})], on_finish=hit_targets)


    # -- victory / experience --------------------------------------------

    def _check_battle_end(self) -> None:
        all_enemies_dead = all(e.dead for e in self.battle_state.enemies)
        all_party_dead = all(c.dead for c in self.battle_state.party.characters.values())

        if all_enemies_dead:
            self._victory()
        elif all_party_dead:
            self._faint()
        else:
            self.state_machine.pop()


    def _victory(self) -> None:
        settings.stop_music("battle")
        self._victory_channel = settings.SOUNDS["victory"].play(loops=-1)

        from src.states.game.BattleMessageState import BattleMessageState

        self.state_machine.push(
            BattleMessageState(self.state_machine),
            battle_state=self.battle_state,
            message="Victory!",
            on_close=self._start_exp,
        )

    def _start_exp(self) -> None:
        total_level = sum(enemy.level for enemy in self.battle_state.enemies)
        num_characters = len(self.battle_state.party.characters)
        opponent_level = total_level / num_characters
        self._inc_exp(0, opponent_level)

    def _inc_exp(self, index: int, opponent_level: float) -> None:
        keys = self._party_keys()

        if index >= len(keys):
            self._fade_out()
            return

        character = self.battle_state.party.characters[keys[index]]

        if character.dead:
            self._inc_exp(index + 1, opponent_level)
            return

        exp = math.ceil(
            (character.hpiv + character.attackiv + character.defenseiv + character.magiciv)
            * opponent_level
        )

        from src.states.game.BattleMessageState import BattleMessageState

        self.state_machine.push(
            BattleMessageState(self.state_machine),
            battle_state=self.battle_state,
            message=f"{character.name} earned {exp} experience points!",
            on_close=None,
            can_input=False,
        )
        Timer.after(1.5, lambda: self._apply_exp(character, exp, index, opponent_level))

    def _apply_exp(
        self, character: Any, exp: int, index: int, opponent_level: float
    ) -> None:
        settings.SOUNDS["exp"].play()
        new_value = min(character.current_exp + exp, character.exp_to_level)
        Timer.tween(
            0.5,
            [(character.exp_bar, {"value": new_value})],
            on_finish=lambda: self._exp_applied(character, exp, index, opponent_level),
        )

    def _exp_applied(
        self, character: Any, exp: int, index: int, opponent_level: float
    ) -> None:
        # Pops the can_input=False experience-gain message, which never
        # auto-closes on its own.
        self.state_machine.pop()
        character.current_exp += exp

        if character.current_exp >= character.exp_to_level:
            settings.SOUNDS["levelup"].play()
            character.current_exp -= character.exp_to_level
            last_level = character.level
            increases = character.level_up()
            hp_increase = increases[0]
            Timer.tween(
                0.5, [(character.energy_bar, {"value": character.current_hp - hp_increase})]
            )

            from src.states.game.BattleMessageState import BattleMessageState

            message = (
                f"Congratulations! {character.name} advanced from level "
                f"{last_level} level {character.level}!"
            )
            self.state_machine.push(
                BattleMessageState(self.state_machine),
                battle_state=self.battle_state,
                message=message,
                on_close=lambda: self._show_stats(character, increases, index, opponent_level),
            )
        else:
            self._inc_exp(index + 1, opponent_level)

    def _show_stats(self, character: Any, increases: Any, index: int, opponent_level: float) -> None:
        from src.states.game.StatsMenuState import StatsMenuState

        self.state_machine.push(
            StatsMenuState(self.state_machine),
            character=character,
            stats=increases,
            on_close=lambda: self._inc_exp(index + 1, opponent_level),
        )

    def update(self, dt: float) -> None:
        for effect in self.battle_state.particle_effects:
            effect.system.update(dt)
        self.battle_state.particle_effects = [e for e in self.battle_state.particle_effects if e.active]

    def _fade_out(self) -> None:
        if self._victory_channel is not None:
            self._victory_channel.stop()

        from src.states.game.FadeInState import FadeInState
        from src.states.game.FadeOutState import FadeOutState

        if self.battle_state.final_boss:

            def on_complete() -> None:
                # Pops this lingering TakeTurnState, then the BattleState
                # underneath it (matches the original's "pop twice"). The
                # second pop runs BattleState.exit(), which always calls
                # the on_exit it was pushed with (see
                # PartyWalkState._trigger_encounter) -- for a NORMAL battle
                # that's the whole point (it un-pauses the overworld's
                # "world"/"town" music the encounter had merely paused,
                # not stopped, so walking around resumes right where the
                # music left off), but here there's no overworld to return
                # to: the very next thing on screen is TheEndState. Without
                # silencing what that on_exit just resumed, it played
                # underneath "the-end" for the rest of the game -- the two
                # overlapping tracks this whole fix is about. _victory
                # already stopped "battle" and _fade_out already stopped
                # the "victory" jingle, so this only has the resumed
                # overworld music left to clean up, but stopping "battle"
                # again too is harmless and keeps this correct even if
                # that ordering ever changes.
                self.state_machine.pop()
                self.state_machine.pop()
                settings.stop_music("battle")
                settings.stop_music("world")
                settings.stop_music("town")
                # A bare SOUNDS["the-end"].play() (the original code here)
                # starts a plain, untracked Sound channel -- unlike every
                # other music cue in this game, it was never routed
                # through play_music, so nothing could stop it the same
                # way the stops above stop everything else (see
                # TheEndState's restart handler).
                settings.play_music("the-end")

                from src.states.game.TheEndState import TheEndState

                self.state_machine.push(TheEndState(self.state_machine))
                self.state_machine.push(
                    FadeOutState(self.state_machine),
                    color=(0, 0, 0),
                    time=1,
                    on_complete=lambda: None,
                )

            self.state_machine.push(
                FadeInState(self.state_machine),
                color=(0, 0, 0),
                time=3,
                on_complete=on_complete,
            )
        else:

            def on_complete() -> None:
                # Pops this lingering TakeTurnState, then the BattleState
                # underneath it (BattleState.exit() stops battle music and
                # restores the party's overworld position/music).
                self.state_machine.pop()
                self.state_machine.pop()
                self.state_machine.push(
                    FadeOutState(self.state_machine),
                    color=(255, 255, 255),
                    time=1,
                    on_complete=lambda: None,
                )

            self.state_machine.push(
                FadeInState(self.state_machine),
                color=(255, 255, 255),
                time=1,
                on_complete=on_complete,
            )

    def _faint(self) -> None:
        settings.stop_music("battle")
        settings.SOUNDS["game-over"].play()

        from src.states.game.FadeInState import FadeInState

        def on_complete() -> None:
            from src.states.game.GameOverState import GameOverState

            self.state_machine.push(GameOverState(self.state_machine))

        self.state_machine.push(
            FadeInState(self.state_machine),
            color=(0, 0, 0),
            time=1,
            on_complete=on_complete,
        )

    _victory_channel = None
