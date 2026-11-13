# Robot Escape

A small Python game built with Pygame. Collect all eight coins,
avoid monsters and fire traps, and reach the unlocked exit.

## Running the game

Install Python, then run these commands from the project folder:

    python -m pip install -r requirements.txt
    python main.py

## Controls

- Arrow keys: move / select menu options
- Enter: confirm / restart
- Escape: return to the menu

## Features

- Monsters with chasing, searching, and returning states
- Tile-based pathfinding and wall collisions
- Fire traps with warning and burning phases
- Coin collection and an unlockable exit
- Five locally saved best completion times

## Project structure

- main.py: starts the game
- game.py: game loop, input, game state, and scoring
- arena.py: map, collisions, fire areas, and pathfinding
- draw.py: rendering and menus
- characters.py: player, monster, and coin classes
- fire_area.py: fire trap timing