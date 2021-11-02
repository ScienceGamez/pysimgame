"""Open pysdgame main menu.

The main menu loop.
"""
import sys

import pygame
from pygame import display, time
from pygame_gui.ui_manager import UIManager
from pygame_gui.elements import UIButton

from pysdgame import PYSDGAME_SETTINGS


FPS = PYSDGAME_SETTINGS["FPS"]

pygame.init()
MAIN_DISPLAY = display.set_mode(PYSDGAME_SETTINGS["Resolution"])

CLOCK = time.Clock()
UI_MANAGER = UIManager(PYSDGAME_SETTINGS["Resolution"])

# Helpers for buttons positions
x_size = PYSDGAME_SETTINGS["Resolution"][0]
y_size = PYSDGAME_SETTINGS["Resolution"][1]
x_center = int(x_size / 2)
button_width = x_size / 4
button_left = x_center - button_width / 2
n_buttons = 3  # Number of buttons
y_positions = [0.5 * i * y_size / n_buttons for i in range(n_buttons)]

# Adds widgets
load_game_button = UIButton(
    pygame.Rect(button_left, y_positions[0], button_width, y_size / n_buttons),
    "Load Game",
    UI_MANAGER,
)
# TODO add the other buttons


while True:

    time_delta = CLOCK.tick(PYSDGAME_SETTINGS["FPS"]) / 1000.0
    events = pygame.event.get()
    # Lood for quit events
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        UI_MANAGER.process_events(event)

    # Handles the actions for pygame widgets
    UI_MANAGER.update(time_delta)

    UI_MANAGER.draw_ui(MAIN_DISPLAY)

    display.update()