from src.ship_input import ensure_player_ships
from src.bot_generation import ensure_bot_ships
from src.gameplay import Game
import os

os.makedirs('data', exist_ok=True)
os.makedirs('outputs', exist_ok=True)

if __name__ == '__main__':
    ensure_player_ships()
    ensure_bot_ships()
    game = Game()
    game.run()