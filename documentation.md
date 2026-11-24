# Development of Robot Escape

Robot Escape was developed as a final project for the University of Helsinki Advanced Course in Programming (Python MOOC). The aim was to make a more substantial Pygame game: guide a robot through an arena, collect eight coins, survive fire traps and monsters, and reach the exit. Development proceeded feature by feature, with attention to understanding the code, separating responsibilities, and revisiting designs when gameplay exposed problems.

## Establishing the game structure

The project began with a central `Game` class. It owns the 960 × 640 window's game state, the main loop, input handling, game updates, and the mutable data for each run. The loop caps itself at 60 frames per second with `pygame.time.Clock`, then handles events, updates the game, and draws the current screen. A single loop and a state variable made it possible to add screens without creating a separate loop for each one. The current states are `menu`, `playing`, `highscores`, `game_over`, `enter_name`, and `victory`.

Rendering was extracted into `Draw`, while `Arena` manages the map, collision checks, fire regions, and pathfinding. `Player`, `Monster`, and `Coin` are separate classes, and `FireArea` manages a hazard's timing. This division keeps the main loop readable and gives each part of the game a clearer responsibility. Persistent resources such as sprites, fonts, and the clock are created once; a new run resets mutable objects and values through `restart_game()`.

The menu was an early example of the state-based design. Up and down change a selected index with modulo arithmetic, so selection wraps around. Both main Enter and keypad Enter confirm a choice. Text size is measured before drawing the yellow outline, which lets the outline fit the selected option. The highscore screen and end screens use the same drawing helpers.

## Building the arena and movement

The playable area is a 14-row, 24-column matrix of 40 × 40 pixel tiles beneath an 80-pixel HUD. Tiles are marked as normal (`N`), wall (`W`), or fire (`F`); colour definitions also include `S`, although no `S` tiles are placed in the current map. The matrix provides one source of truth for the arena's appearance, wall collision, line of sight, and monster navigation. Converting between tile coordinates and screen pixels requires adding or removing the HUD offset. Keeping those conversions in `Arena` helps avoid mixing row and column indices with pixel positions.

The robot uses a sprite and a `pygame.Rect` for its position. Holding an arrow key moves it continuously. Movement first produces a copy of the rectangle; `Arena.wall_slide()` then checks horizontal and vertical movement separately, accepting each axis only when the proposed position stays inside the arena and its body hitbox does not overlap a wall. This permits sliding along a wall instead of stopping all movement on contact. The player also has a smaller feet rectangle for ground hazards, so fire damage is based on where the robot stands rather than the full sprite image. Map spacing and hitbox sizes were refined together as movement was tested.

The HUD displays health, elapsed time, and the number of coins collected. The game starts its timer when a run begins, using `time.monotonic()` so the result reflects real elapsed time rather than a frame count. The coin counter currently displays the collected count, without an explicit “out of eight” total.

## Adding hazards and objectives

Fire regions were introduced as rectangular groups of tiles. Each `FireArea` randomly chooses durations for an inactive period, a warning period, and a burning period when it is created. It uses elapsed game time modulo the total duration to repeat those phases without pausing the loop. Warning areas are orange, burning areas are red, and inactive areas have no overlay. A burning area damages the player at 25 health points per second when it intersects the feet hitbox. The current implementation has no separate cooldown phase or randomly placed surprise hazard.

Coins are placed at fixed tile locations when a run starts. A coin is collected when its 40 × 40 collision rectangle intersects the player's position rectangle. Removing collected coins from the list both updates the HUD and provides a simple completion condition. Once the list is empty, `Game.unlock_door()` replaces the blocking wall tiles near the exit with normal tiles. Reaching the door then ends the run and records the elapsed time. The door sprite itself is drawn throughout the run; access is controlled by the wall tiles and the `door_unlocked` flag.

Defeat occurs if health reaches zero or a monster's collision rectangle touches the player. The end screens support retrying or returning to the menu. Restarting restores health and position, resets the timer, coins, and monsters, and closes the exit again. Centralising those changes prevents a new run from inheriting most of the previous run's state.

## Developing monster behaviour

Monsters introduced a problem that simple direct movement could not solve: they must react to the robot without seeing or passing through walls. Detection first checks whether the player is within 200 pixels, using `pygame.Vector2.distance_to()`. `Arena.has_los()` then draws an imaginary line between the centres of the monster and player rectangles and tests it against each wall rectangle with `pygame.Rect.clipline()`. Proximity alone therefore does not reveal a player behind a wall.

Each monster has a behaviour state. A visible player in range causes `chasing`; after sight is lost, the monster uses the last seen position while `searching`. Idle monsters can wait three seconds and then enter `returning` to move back to their spawn. These decisions are separate from the movement method. `pygame.Vector2` supplies direction and distance calculations, while movement towards a target is capped at two pixels per update. The same wall-sliding collision check used for the player prevents monsters from passing through solid tiles.

Wall sliding alone cannot find a route around a large obstacle. The final code therefore includes breadth-first search in `Arena.find_path()`. It treats traversable tiles as connected nodes, visits their four cardinal neighbours, and reconstructs a route from the destination back to the start. The monster follows tile-centre waypoints and can recalculate a path when its goal changes. A blocked destination or collision can still interrupt movement, so this is a practical tile-based navigation system rather than a guarantee that every pursuit succeeds. Developing it required careful conversion among pixel positions, tile coordinates, and matrix indices.

## Completing the highscore flow

The highscore screen loads results from JSON. After a victory, a run qualifies for name entry if fewer than five scores are stored or its time is faster than the current fifth score. Text input accepts up to 15 characters; Enter saves a nonblank name. Scores are sorted by ascending completion time and only the fastest five are written back to `highscores.json`. A non-qualifying victory goes straight to the victory screen.

One implementation detail to be aware of is that the score file is opened by its bare filename, unlike sprites, which are loaded relative to their source file. Scores therefore read and write in the process's current working directory. Running the game from this project folder uses the included `highscores.json`; launching it from elsewhere can create or use a different file.

## What the project taught

The project brought together object-oriented design, game and enemy state machines, continuous input, tile and pixel coordinate systems, specialised collision rectangles, real-time hazard timing, vector movement, line of sight, graph search, and JSON persistence. The incremental process mattered: testing a feature in play exposed issues with corridor widths, hitboxes, and monster movement that were difficult to settle from a design sketch alone. Extracting responsibilities into classes and methods made those interactions easier to reason about as the game grew.
