# Throw a Bird - Enhanced Edition

A physics-based puzzle game inspired by the classic Angry Birds, developed as an academic project for Universidad de Los Andes. This enhanced version introduces advanced mechanics, specialized bird abilities, and a high level of game feel to elevate the traditional slingshot gameplay into a highly polished arcade experience.

## Features & Mechanics

### The Flock (Randomized Spawns)
The slingshot randomly generates one of four unique birds each turn:
*   **Red Bird:** The classic heavy hitter. Reliable and straightforward for structural damage.
*   **Blue Bird (Splitter):** Press `Space` mid-flight to split into three smaller, lighter birds. The clones spread out at a 30-degree angle, perfect for widespread damage, and leave a glowing blue particle trail.
*   **Black Bird (The Bomb):** Press `Space` to ignite a 3-second fuse. The fuse sparks dynamically track the bird's rotation. Upon detonation, it unleashes a massive radial physics explosion that scales with the mass of surrounding objects, launching heavy blocks into the stratosphere while shaking the screen.
*   **Yellow Bird (Lazer Dash):** Press `Space` to activate. The bird freezes in mid-air for 1 second, automatically calculates the trajectory to the nearest enemy (alien), and fires itself like a missile with extreme velocity, leaving a fiery particle trail.

### Game Feel
*   **Advanced Particle Systems:** Custom particles for explosions, bird abilities (trails), block destruction (wood/stone debris), and enemy defeats.
*   **Screen Shake:** Dynamic camera vibration during explosions to emphasize raw impact and power.
*   **Dynamic Audio:** A complete soundscape including continuous retro background music, slingshot tension sound effects, ability triggers (dash, split, fuse), block breaking crunches (with adjusted volume balancing), and classic arcade enemy death sounds.
*   **Smart Camera Tracking:** The camera automatically zooms and follows the fastest-moving object on the screen, with dynamic FOV scaling based on distance.
*   **UI & Flow:** Live on-screen enemy counter and a cinematic 3-second delay upon clearing a level before transitioning to the victory screen, allowing players to fully admire the physical destruction.

## Controls
*   **Left Mouse Button (Hold & Drag near bird):** Aim and stretch the slingshot.
*   **Left Mouse Button (Drag elsewhere):** Pan the camera manually across the level.
*   **Spacebar:** Activate the special ability of the current bird (Blue, Black, or Yellow) while in flight.
*   **A / D:** Toggle manual camera tracking between birds during flight.
*   **ESC:** Quit the game.

## Built With
*   **Python 3**
*   **Pygame** (Rendering and Audio System)
*   **Pymunk / Box2D** (Rigid body physics and collision calculations)
*   **Gale** (Game engine framework)