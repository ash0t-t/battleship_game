# Battleship — terminal version

## Overview
This project implements a simplified Battleship game playable in the terminal. Board is 10×10 (rows A–J, cols 1–10). Ships configuration:
- 1 ship of size 4
- 2 ships of size 3
- 3 ships of size 2
- 4 ships of size 1
Ships must not touch (including diagonally).

## Input format
Player places ships by entering space-separated coordinates for each ship (example for a size-3 ship): `A1 A2 A3`. The program prompts for ships in descending sizes.

## Validation rules
- Ships must match reaquired sizes.
- Ships must be contiguous and straight (horizontal or vertical).
- Ships must be within the 10×10 board.
- Ships cannot touch any other ship, including diagonally.
Invalid placements are rejected and the user is prompted to re-enter.

## Game state update & display
- After each turn the program updates `data/game_state.csv` with turn number, both moves, and flattened board states.
- The terminal prints two 10×10 boards: the player's board (shows ships, hits, misses) and the known bot board (shows hits and misses only).
- When a ship is destroyed, all surrounding 8 cells are automatically marked as misses.

## Bot AI
- Starts shooting randomly among untried cells.
- After a first hit (ship size > 1), bot enters targeting mode: tries adjacent cells.
- After a second consecutive hit, bot locks to that axis and continues along it.
- When a ship is destroyed, bot returns to random mode.

## How to run
1. Create virtual environment `python3 -m venv venv`
2. Activate virtual environment `source venv/bin/activate`
3. Install requirements: `pip install -r requirements.txt`
4. Run: `python main.py`
5. Follow prompts in terminal. All data files are saved into `data/`.

## Design decisions
- CSV ship format: each row is one ship with `ship_id,size,cells`.
- Boards stored as flat strings in `game_state.csv` for simplicity.
- Bot AI uses simple deterministic axis locking after two hits for reliable hunting.
