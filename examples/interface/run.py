import os
import sys

# setting path
sys.path.append(os.path.join("."))

from pysimgame.game_manager import GameManager

manager = GameManager("Test")

manager.start_game_loop()
