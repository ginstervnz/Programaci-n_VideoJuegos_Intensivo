# Match-3 Game Engine 

**Author:** Ricardo Felzani  
**Institution:** Universidad de Los Andes  
**Course:** Video Game Programming I (ISPPV1)  

A fully functional, grid-based Match-3 puzzle game built with Python and Pygame. This project focuses on advanced game logic, fluid animations, matrix manipulation, and recursive match detection.

## Features & Logic Implemented

### Drag & Drop Interaction
Replaced the traditional keyboard cursor with a modern Drag & Drop mouse interface. 
* **Logic:** The engine calculates virtual mouse coordinates and maps them to the board's 2D array. It strictly validates moves, snapping tiles back to their original grid position with a smooth tweening animation if an invalid (diagonal or out-of-bounds) move is attempted.

### Inactivity Hint System
A quality-of-life feature to assist players when they are stuck.
* **Logic:** Tracks a delta-time (`dt`) variable while the game state is active and no tiles are being dragged. If 5 seconds pass without player input, it scans the board for valid simulated moves and highlights a possible match using a dynamic, pulsing neon border (driven by a sine wave mathematical function for smooth alpha oscillation).

### Predictive Board Reshuffling
Prevents the game from entering a "dead state" where no matches can be made.
* **Logic:** On every turn, the engine simulates every possible horizontal and vertical swap across the entire matrix. If the `has_possible_moves` flag returns false, it triggers a visual screen shake and smoothly reshuffles all tiles off-screen before dropping a completely new, mathematically validated board.

---

## Power-Up System
The game features an advanced chain-reaction power-up system built through property mutation rather than object instantiation, ensuring smooth grid physics.

### Cross Bomb (Match-4)
* **Trigger:** Formed by matching exactly 4 tiles. It inherits the color of the matched set.
* **Effect:** Destroys all tiles in its row and column.
* **Logic (Wave Animation):** Uses a recursive coroutine timer to create an expanding wave. Instead of destroying the entire cross instantly, it increments a `radius` variable every 0.08 seconds, destroying tiles progressively from the center outward. The gravity system dynamically pushes falling tiles to chase the explosion wave, rather than waiting for the entire animation to finish.

### Color Bomb (Match-5+)
* **Trigger:** Formed by matching 5 or more tiles.
* **Effect:** Clears all tiles of a specific color from the board instantly.
* **Logic:** Scans the entire 2D matrix for tiles matching the bomb's underlying color. It features chain-reaction compatibility: if a Color Bomb destroys a Cross Bomb, it automatically triggers the Cross Bomb's wave destruction in its respective coordinate.

---

## Developer Cheats & Debugging
To facilitate rapid testing of edge cases and power-ups, a developer cheat system was implemented. This can be toggled via the `ENABLE_CHEATS` boolean flag in `settings.py`.

When enabled, hover the mouse over any tile and press:
* `P` **(Power-up):** Instantly mutates the hovered tile into a Cross Bomb.
* `C` **(Color Cycle):** Cycles the tile's color through the available palette to manually set up specific matches.
* `B` **(Bomb):** Instantly mutates the hovered tile into a Color Bomb.

---

## Technologies Used
* **Language:** Python 3
* **Graphics & Audio:** Pygame
* **Framework:** Gale (Custom State Machine and Tweening Engine)