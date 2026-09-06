# The Legend of the Princess - Boss Fight Update 

This repository features an expanded and heavily polished version of the "Legend of the Princess" ARPG study case. The core highlight of this update is the implementation of a fully functional, multi-phase Boss encounter along with significant improvements to the game's progression loop and overall "Game Feel".

## Key Features Implemented

### Epic Boss Fight (Fire Worm)
A custom-built boss entity driven by a robust State Machine (Idle, Walk, Attack, Hit, Death) and advanced AI behaviors:
* **Attack Roulette:** The boss randomly selects between three distinct projectile patterns to keep the player on their toes:
  * *Single Shot:* A direct fireball aimed at the player.
  * *Spread Shot:* A 4-way fan of fireballs shot towards the player's general direction.
  * *Nova Explosion:* A brutal 360-degree ring of 8 fireballs.
* **Phase 2 (Enrage Mode):** Upon reaching critical health, the boss enters a second phase where its movement speed doubles, its resting time between attacks is drastically reduced, and it gains "Super Armor" (ignoring hit-stun during attack animations).
* **Smart Bounding Box:** Custom arena clamping ensures the boss never clips through the environment while maintaining fluid movement.

### Dynamic Boss Room & Infinite Loop
* **Seamless Audio Transitions:** The dungeon music dynamically shifts to a specific "Boss Theme" upon entering the arena, and transitions into a "Victory Theme" once the boss is defeated.
* **Progression Loop:** Defeating the boss triggers a cinematic death animation, after which a custom **Boss Key** is spawned. Collecting this key unlocks the arena doors, allowing the player to escape and continue the dungeon cycle infinitely.
* **Custom UI:** Added a dynamic shield icon to the player's HUD to indicate when the boss has temporary immunity frames.

### Game Feel & Polish
* **Particle System:** Implemented a highly optimized particle effect system. Projectile impacts against walls or enemies generate a subtle, 360-degree burst of colored sparks to emphasize the hit.
* **Enhanced Interaction Hitboxes:** Re-engineered the interaction system with a directional "Reach Box". This allows for smooth, forgiving item collection (like picking up the Bow from a chest).
* **Audio Cues:** Added custom sound effects for damaging the boss and player impacts to increase combat weight.