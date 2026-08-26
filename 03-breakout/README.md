# Breakout: Advanced Mechanics & Quantum Physics Edition

An enhanced, high-performance clone of the classic arcade game Breakout, built with Python and Pygame using the Gale framework. This project takes the traditional block-breaking formula and elevates it through advanced computational geometry, decoupled software architecture, and highly dynamic, procedurally rendered power-ups.

## Technical Highlights
* **Abstract Factory Pattern:** Seamless and scalable instantiation of diverse power-ups.
* **Decoupled Architecture:** Strict separation of concerns. Physics calculations, collision detection, and procedural rendering are isolated in dedicated helper modules (`utils/play_update_helpers.py` and `utils/play_render_helpers.py`) to keep the State Machine pristine.
* **Procedural VFX:** Advanced visual effects like dynamic lightning chains and laser shields are rendered purely through math and code in real-time, avoiding the overhead of heavy sprite sheets.

---

##  Custom Power-Ups & Mechanics

This game features a robust power-up system. When a brick is destroyed, there is a chance it will drop one of the following game-changing abilities:

### 1. Two More Balls (Multi-ball)
Injects pure chaos into the arena by instantly spawning two additional balls from the paddle's current position. Perfect for clearing out massive clusters of bricks.

### 2. Sticky Paddle (Tactical Aim) [Activity 1]
The paddle becomes coated in a high-friction adhesive. When the ball makes contact, it gets stuck to the paddle. A rotating aiming arrow appears, allowing the player to strategically calculate and fire the ball at a specific angle to snipe hard-to-reach bricks.

### 3. Radioactive Ball (Armor Piercing) [Activity 3]
The ball is infused with radioactive energy. Instead of bouncing off the first brick it hits, it deals massive penetrating damage, instantly melting through multiple defensive layers and standard bricks in a single strike.

### 4. Rocket Launcher (Heavy Artillery) [Activity 2]
Arms the paddle with a dual-missile launcher, granting the player 4 manual shots. 
* Includes **Special Rockets** that deal Area of Effect (AoE) damage. 
* Features procedural smoke trails, screen-shake mechanics, and explosive particle systems upon impact.

### 5. Extra Life (+1 UP) [Activity 3]
Grants the player an additional life to stay in the fight. If the player already has the maximum of 3 lives, this power-up grants a flat 150 bonus score instead.

### 6. Electro Storm (Chain Lightning) [Activity 3]
A highly advanced procedural power-up. It infuses the active balls with electrical charges (represented by a chaotic, code-generated visual aura). 
* **Mechanic:** When a charged ball hits a brick, it triggers a chain-lightning strike that instantly zaps and destroys the 3 nearest active bricks.
* **Tech:** Uses the Pythagorean theorem to calculate the closest geometric neighbors in real-time and draws chaotic, branching lightning bolts connecting the impact epicenter to its targets.

### 7. Quantum Defense Matrix (Procedural Shield) [Activity 3]
The ultimate defensive ability that alters the physical space of the game. 
* **Mechanic:** Deploys 4 unstable energy nodes that anchor to the bottom of the screen. The system calculates a real-time **Convex Hull** (using the Monotone Chain algorithm) to project a solid neon laser shield connecting the nodes to the paddle.
* **Physics:** If a ball falls towards the abyss, it collides with the dynamic edges of this shield. The game computes the exact normal vector of the shield's slope at the point of impact and applies a perfect mathematical vector reflection ($\vec{v}_{f}=\vec{v}_{i}-2(\vec{v}_{i}\cdot\hat{n})\hat{n}$) to bounce the ball back into the action.

---

##  Project Overview & Architecture
This project focused on transforming a basic monolithic game loop into a professional, decoupled software architecture. The primary goal was to implement the **Abstract Factory Pattern** for dynamic power-up generation and to separate physics calculations, rendering processes, and state management into distinct utility modules. This approach ensures the codebase remains highly scalable, readable, and strictly follows the Single Responsibility Principle.

##  Directory & File Structure
The following core files and directories were created or heavily modified to achieve this architectural overhaul:

*   **`src/states/PlayState.py`**: Refactored to act purely as a state director, delegating complex math and drawing logic to external helper modules.
*   **`src/states/PauseState.py`**: Updated to properly pack and unpack dynamic variables (like Quantum nodes and active timers) to perfectly maintain the game state across pauses.
*   **`src/utils/play_update_helpers.py`**: A newly created physics module handling collision detection, vector reflections, bounding logic, and real-time computational geometry.
*   **`src/utils/play_render_helpers.py`**: A dedicated graphics module responsible for procedural VFX, Convex Hull polygon drawing, alpha-blended flashes, and screen-shake effects.
*   **`src/powerups/`**: A fully expanded directory utilizing the Abstract Factory pattern, containing perfectly encapsulated classes for each ability (e.g., `QuantumPowerUp.py`, `ElectroPowerUp.py`, `RocketPowerUp.py`).

## 🎮 Game Controls, Sounds and Graphics
The input handling was expanded to support the new tactical mechanics seamlessly:

*   **Left / Right Arrows**: Move the paddle horizontally across the screen.
*   **Spacebar (Action/Shot)**: Fire heavy artillery missiles when the Rocket power-up is active, or manually release a stuck ball when the Sticky Paddle is equipped.
*   **Enter / Return**: Pause the game and open the pause menu without losing active power-up states, timers, or procedural geometry configurations.
*   **New sounds**: A lot of new music was added
*   **New sprites**: A lot of new sprites for each powerup was added

## 💻 Author
**Ricardo Felzani Olmedillo**
*Developed as a comprehensive study in Game Architecture, Computational Geometry, and Linear Algebra applied to 2D Game Development.*