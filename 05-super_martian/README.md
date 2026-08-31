# Super Martian - Extended Edition 

A 2D platformer game built in Python using **Pygame** and the **Gale Engine**. This project originated as a study case for ISPPV1 (Game Programming) and has been heavily expanded with new game mechanics, advanced entity states, dynamic UI elements, and a robust level progression system.

**Original Author:** Alejandro Mujica  
**Extended & Modified by:** Ricardo Felzani Olmedillo  

---

## Key Features & Implementations

### 1.  State Persistence
*   **Persistent Inventory & Scoring:** Overhauled the state machine flow to allow the player's score and collected coins to persist seamlessly across multiple levels (`PlayState` -> `VictoryState` -> `PlayState`).

### 2. Custom Entities & Smart AI
*   **Smart Edge-Detection (Cliff AI):** Developed a multi-cell "radar" system for enemy AI (`GoblinWalkState`, `FlyWalkState`) that accurately reads Tiled map layers, allowing enemies to autonomously patrol platforms and turn around before falling off edges.
*   **New Enemy Varieties:** Integrated multiple new custom sprite sheets (Goblins, Skeletons, Slimes) with distinct animation intervals and tailored state machines.
*   **Custom Collectibles:** Added animated custom coins (ID: 36) with unique point values and pickup logic, fully integrated into the game's internal item dictionary.

### 3. Dynamic Events & Level Interactions
*   **Triggered Special Blocks:** Implemented interactive blocks that, when hit from below under specific score conditions, trigger a tweened animation to spawn a Level Key. 
*   **Dynamic Audio Engine:** Programmed the `PlayState` to seamlessly switch background music based on the active level (e.g., custom Level 3 music) and trigger specific intense tracks when special in-game events are unlocked.

### 4. Cinematic UI & Polish
*   **Cinematic "Curtain" Transitions:** Replaced basic screen cuts with a professional top-and-bottom cinematic black bar transition in the `VictoryState`, powered by `gale.timer.Timer` tweens.
*   **Interactive Final Menu:** Created a custom end-game menu for Level 3, allowing players to either restart the entire campaign or safely quit the application.
*   **Dynamic Game Over Screen:** Upgraded the `GameOverState` to dynamically loop through the player's inventory, rendering only the specific coin types collected (including custom assets) alongside the total accumulated score.

---
##  Built With
*   **Python 3**
*   **Pygame** (Rendering and Audio)
*   **Gale Engine** (Game Architecture, State Machines, Timers, and Input Handling)
*   **Tiled** (Level Map Design & JSON Layering)

##  How to Play
1. Ensure you have Python installed along with the required dependencies.
2. Install the Gale Engine via pip.
3. Run `python main.py` to start the game.
4. Collect coins, reach the target score to spawn the key, avoid enemies, and beat all 3 levels.