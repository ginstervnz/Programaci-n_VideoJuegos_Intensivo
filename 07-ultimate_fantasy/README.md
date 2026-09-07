# Ultimate Fantasy - Enhanced RPG Edition

**Original Author:** Alejandro Mujica  
**Extended & Modified by:** Ricardo Felzani Olmedillo 
**Institution:** Universidad de Los Andes

## Overview
This project is an extended version of the "Ultimate Fantasy" RPG case study. It introduces a variety of new mechanics aimed at deepening the combat system, enhancing enemy AI, and expanding the overworld with interactive buildings and resource management. 

## Implemented Features & Requirements

### Active Time Battle (ATB) Combat System
The static turn-based round system was completely overhauled and replaced with a real-time ATB engine.
* **Speed Stat Integration:** Every character and enemy now possesses a "Speed" stat. This stat determines how fast their ATB gauge fills.
* **Level Scaling:** To maintain mid-to-late game balance, the Speed stat dynamically increases by 1 to 2 points upon leveling up.
* **Vertical ATB UI:** A custom vertical blue progress bar was implemented on the outer flanks of the combatants (left for the party, right for enemies) to track turn readiness cleanly without cluttering the main character sprites.

### Fatigue and Stamina Economy
A stamina system was introduced to prevent action spamming and add tactical depth to the combat.
* **Action Costs:** Every attack or spell consumes a specific amount of fatigue. 
* **Passive Recovery:** When a combatant's ATB gauge reaches 100%, their fatigue is passively reduced in 3.5, allowing them to recover breath over time.
* **Enemy AI Rest Logic:** Enemies are fully bound by the stamina system. If an enemy lacks the required stamina to perform an action, its AI automatically aborts the attack and executes a "Resting" turn to recover energy, balancing fierce enemy encounters.

### The Guild Hall (Overworld Expansion)
A new explorable building was integrated into the central town region, featuring both an exterior map presence and a fully custom interior.
* **Overworld Integration:** The Guild Hall exterior was placed in the top-left corner of the town. Collision bounds were adjusted mathematically to make the building completely solid, and NPC/flower spawns were disabled in its perimeter.
* **Side-Scrolling Interior:** Entering the Guild transitions the camera to a 2D side-scrolling perspective. The interior was custom-built using the medieval tileset.
* **Cinematic Transitions:** Entering and leaving the Guild triggers smooth fade-to-black transitions, accompanied by floating text ("Guild" or "center") and context-aware music swapping.

### Guild Receptionist & Resource Management
Inside the Guild, the party can interact with a Receptionist NPC who offers a strict, limited-use survival menu to aid in long playthroughs.
* **Revive Ally (1 Use per Game):** Brings the first dead party member back to life with 5 HP.
* **Rest Party (2 Uses per Game):** Fully resets the fatigue/stamina levels of all living party members to 0.
* **Field Restrictions:** Dead characters are strictly prohibited from using field abilities (like healing) from the pause menu, enforcing the need for the Guild's revive mechanic.

### UI and Menu Enhancements
* **Expanded Character Profiles:** The exploration menu panels were dynamically resized to accommodate the display of the new Speed stat, alongside HP, EXP, Attack, Defense, Magic, and Rest Time.
* **Level-Up Screen:** The post-battle victory screen now accurately displays the RNG-based growth of the Speed stat alongside core attributes.