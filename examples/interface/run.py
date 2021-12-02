import sys
import os

# setting path
sys.path.append(os.path.join("."))

from pysdgame.game_manager import GameManager


manager = GameManager("Test")

manager.start_game_loop()
