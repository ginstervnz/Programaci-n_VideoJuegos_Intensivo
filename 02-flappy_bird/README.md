# Flappy Bird: Advanced Edition

> *An advanced, object-oriented implementation of the classic Flappy Bird game, built with Python, Pygame, and the event-driven Gale framework. Designed with complex software patterns, dynamic physics, and comprehensive state management for a polished gameplay experience.*

---

## Table of Contents
1. [Architecture & Design Patterns](#-architecture--design-patterns)
2. [Core Gameplay Mechanics](#-core-gameplay-mechanics)
3. [Dynamic Obstacles & Items](#-dynamic-obstacles--items)

---

## Architecture & Design Patterns

The codebase is strictly object-oriented, utilizing standard industry patterns to maintain a scalable, modular, and clean structure:

* **Robust State Machine:** Manages seamless transitions between distinct game phases. The architecture includes new states how a `ServeState` for pre-game preparation, a fully functional `PauseState` for mid-game interruptions, and a comprehensive `GameOverState`. Each state independently manages its own logic, UI rendering, user options, and dedicated background music tracks.
* **Strategy Pattern:** Decouples spawn logic and bird movement from the core entities, allowing the game to dynamically switch between normal and hard difficulties (`HardSpawnStrategy`, `HardMovementStrategy`).
* **Factory & Abstract Factory:** Instantiates game entities efficiently. Simple factories handle the creation of standard and moving logs, while an Abstract Factory dynamically loads and generates collectible items directly from the `src.powerups` module.

## Core Gameplay Mechanics

* **Expanded Input Handling:** Features a comprehensive set of keybindings for seamless menu navigation, state toggling (e.g., pausing the game), and options selection. 
* **Event-Driven Movement:** Implements specific `pressed` and `released` state checks for keyboard events, bypassing OS-level key repeat delays to provide instantaneous, Breakout-style horizontal movement.
* **Predictive Spawning Algorithm:** Uses a predictive pre-calculation system to determine the spawn timer of the *upcoming* obstacle before placing the current one. This prevents "spawn lag" and guarantees fair spatial gaps for the player.
* **Audio Synchronization & UI:** Custom audio cues (such as the biting log impact or UI selections) are tightly controlled via boolean flags within the update loops. Each state integrates contextual background music and tailored UI elements (menus, scoreboards) to provide a complete gameplay loop.

## Dynamic Obstacles & Items

* **Complex Obstacles:** Introduces `ShiftingLogPair` (translates vertically towards a target Y coordinate) and `MovingLogPair` (bites shut completely using a smooth cosine wave calculation).
* **Advanced Power-Up System:** Powered by the Abstract Factory pattern, the game features dynamic items like the **"Ghost Potion"**. When collected, it triggers a temporary invulnerability status, ignoring obstacle hitboxes while maintaining gravity and movement physics, complete with custom audio transitions.
* **Centric Power-Up Spawning:** Power-ups are spawned precisely halfway between logs along the X-axis using a dynamic physics formula (`Distance = Speed * Time / 2`) based on the predictive timer. Meanwhile, their vertical (Y-axis) placement remains randomized within a safe margin, keeping the collection challenging while avoiding structural overlaps.
* **Collision-Free Zones:** Before instantiation, a `16x16` dummy hitbox scans the environment using the `world.collides()` engine. This guarantees items never spawn inside dynamic obstacles or below the ground plane.

---
*Developed for advanced game programming evaluation.*