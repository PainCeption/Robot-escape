# Debugging and problem solving in Robot Escape

This is a record of problems encountered while developing Robot Escape, how they were investigated, and what the fixes taught me. The broader development story is in [documentation.md](./documentation.md).

## Getting Pygame to run

The first obstacle was outside the game code. VS Code reported `ModuleNotFoundError: No module named 'pygame'` even though Pygame had been installed. Running the game with an explicit Python executable showed that the editor was using a different interpreter from the one containing the package. Checking interpreter selection and launch configuration was the relevant fix. This was a reminder to verify the execution environment before changing source code in response to an import error.

## Fixing the menu highlight

The yellow selection rectangle initially covered the option text because `pygame.draw.rect()` fills a rectangle when its outline-width argument is omitted. Supplying a width made it an outline. The menu then measured each option with `font.size()` and calculated the rectangle's padded size from the text dimensions. That made the highlight follow the selected label instead of depending on a fixed box size. The final code centres it using the window width.

## Making the arena fit its characters

Some corridors looked passable but blocked the robot. The cause was a mismatch between visible map spacing and the player's collision dimensions. Widening passages was part of the fix; collision code alone could not make an undersized corridor playable. The same issue mattered when placing monsters and the exit. This connected level design to the actual rectangles used by the game, rather than to sprite appearance alone.

The full sprite rectangle was also too coarse for every interaction. The player now has a body rectangle for wall checks and a smaller feet rectangle for ground fire. Both are positioned relative to the player's main rectangle, so they move with it. Testing approaches from different directions helped refine their sizes. This distinguishes standing in a hazard from merely having part of the sprite image overlap it.

## Keeping coordinate systems straight

The game uses screen pixels, tile coordinates, and row/column indices in a matrix. The arena begins 80 pixels below the HUD, so a screen `y` coordinate must have that offset removed before division by the 40-pixel tile size. The `Arena.tile_rect()` and `Arena.position_to_tile()` methods encode the two directions of conversion. When navigation or placement appeared incorrect, checking whether a value represented `(x, y)`, `(row, column)`, or `(column, row)` was essential. Centralising the conversions reduced opportunities for inconsistent offsets.

## Testing defeat and restart

Waiting for normal fire damage made repeated defeat-screen tests slow. During development, fire damage was temporarily raised to 100 health points per second to reach defeat quickly. A kill shortcut was considered but was not added. The current `Arena.fire_dmg` value is 25 health points per second. Temporary parameter changes like this made a particular transition easier to exercise.

Testing a second run revealed that resetting health alone was insufficient. The robot also needed its spawn position restored, the timer restarted, coins and monsters recreated, and the exit closed again. The game now keeps the spawn location in `Game.player_spawn` and collects those reset steps in `Game.restart_game()`. Both standard Enter and keypad Enter are accepted on the relevant menu and end screens. This showed the difference between configuration that persists across runs and state that belongs to one run.

## Separating monster sight from distance

An early proximity-only approach let monsters detect the player through walls. The current detection condition combines a 200-pixel range check with `Arena.has_los()`. That method tests a line between the centres of the monster and player rectangles against wall rectangles using `pygame.Rect.clipline()`. The monster has 360-degree awareness when the line is clear; no directional vision cone was implemented. The key distinction is that being nearby does not mean the player is visible.

## Handling walls, corners, and routes

Moving directly toward a target with a vector caused monsters to press against obstacles. Rejecting a whole proposed move when one axis hit a wall also discarded movement that was still possible on the other axis. `Arena.wall_slide()` checks horizontal and vertical movement separately, allowing a character to slide along an unobstructed direction. Gameplay testing around walls and corners showed that this improves collision response but cannot choose a route around an obstacle.

The navigation system was built on the existing tile matrix. `Arena.get_neightbours()` checks the four adjacent row/column positions, rejects out-of-bounds coordinates, and excludes wall tiles. `Arena.find_path()` then performs breadth-first search and reconstructs a path through reachable tiles. Early work on neighbours exposed smaller syntax, naming, and value-selection mistakes; examining what each loop iteration represented helped resolve them. The current monster code converts between pixels and tiles, follows tile-centre waypoints, and recalculates a path when the goal changes. This was a practical lesson in treating a tile map as a graph.

## Keeping monster behaviour understandable

Detection, decision-making, and movement became easier to investigate when they were separated into dedicated methods.

Monster behaviour is organized into four distinct states: idle, chasing, searching, and returning. `Game.update_monster_state()` evaluates detection range, visibility, and the player's last known position, while `Game.move_monster()` handles destination selection, path-based movement, and returning to the original position.

Storing the player's last seen position allows monsters to continue searching after losing direct visibility. If the player is not found, the monster returns to its original position before becoming idle again.

During development, a small distance threshold was considered for determining whether a monster had reached its destination. The final implementation instead checks whether the centre of the monster's collision rectangle matches the target coordinates.

The development notes mention using a small distance threshold to decide whether a destination was reached. The current `Game.move_monster()` instead compares rectangle centres with the target coordinates for exact equality. The documentation describes the implemented check rather than presenting the earlier idea as final behaviour.

## Testing approach and possible improvements

Manual playtesting was the main way to expose movement, collision, layout, and state-transition problems. The useful pattern was to reproduce one behaviour, inspect the methods responsible, make a focused change, and replay the situation. Temporary gameplay-value changes shortened slow scenarios. Testing existing behaviour again after adding a new feature helped catch interactions between systems. Occasional print statements were used to inspect runtime behaviour, verify whether specific methods were being called, and determine whether monsters were genuinely stuck or repeatedly moving back and forth between positions.
