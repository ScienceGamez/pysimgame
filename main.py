"""Open pysdgame main menu.

The main menu loop.
"""
import sys
from typing import List

import pygame
from pygame import display, time
import pygame_gui
from pygame_gui.ui_manager import UIManager
from pygame_gui.elements import UIButton, UITextEntryLine
from pygame_gui.windows.ui_file_dialog import UIFileDialog

from pysdgame import PYSDGAME_SETTINGS
from pysdgame.utils.directories import DESKTOP_DIR, find_theme_file
from pysdgame.utils.dynamic_menu import UIFormLayout


FPS = PYSDGAME_SETTINGS["FPS"]

pygame.init()
MAIN_DISPLAY = display.set_mode(PYSDGAME_SETTINGS["Resolution"])
BACK_GROUND_COLOR = "black"

CLOCK = time.Clock()
UI_MANAGER = UIManager(
    PYSDGAME_SETTINGS["Resolution"],
    theme_path=find_theme_file(PYSDGAME_SETTINGS["Themes"]["Main Menu"]),
)

# Helpers for buttons positions
n_buttons = 3  # Number of buttons
x_size = PYSDGAME_SETTINGS["Resolution"][0]
y_size = PYSDGAME_SETTINGS["Resolution"][1]
x_center = int(x_size / 2)
button_width = x_size / 4
button_left = x_center - button_width / 2
y_positions = [(0.6 + i) * y_size / (n_buttons + 1) for i in range(n_buttons)]
button_height = y_size / 4 / n_buttons
buttons: List[UIButton] = []

##############################################
# Adds widgets buttons and their next loops
##############################################
buttons.append(
    load_game_button := UIButton(
        pygame.Rect(button_left, y_positions[0], button_width, button_height),
        "Load Game",
        UI_MANAGER,
        tool_tip_text="Load an existing saved game.",
        object_id="#main_menu_button",
    )
)
buttons.append(
    new_game_button := UIButton(
        pygame.Rect(button_left, y_positions[1], button_width, button_height),
        "New Game",
        UI_MANAGER,
        tool_tip_text="Create a new game.",
        object_id="#main_menu_button",
    )
)
buttons.append(
    import_model_button := UIButton(
        pygame.Rect(button_left, y_positions[2], button_width, button_height),
        "Import Game Model",
        UI_MANAGER,
        tool_tip_text=(
            "Import a new kind of game from a pysd compatible model file."
        ),
        object_id="#main_menu_button",
    )
)


def start_import_model_loop():
    """Game loop for importing new model."""
    continue_loop = True

    layout = UIFormLayout(MAIN_DISPLAY.get_rect(), UI_MANAGER)

    layout.add_row("Import New Model")
    layout.add_row("")  # Empty row
    layout.add_row("")  # Empty row
    layout.add_row("From Local Files")
    layout.add_row("")  # Empty row
    layout.add_row(
        "Game Name",
        game_name_entry := UITextEntryLine(
            pygame.Rect(0, 0, 100, 100),
            UI_MANAGER,
            container=layout,
            parent_element=layout,
        ),
    )
    layout.add_row(
        "Model File Path",
        file_name_entry := UITextEntryLine(
            pygame.Rect(0, 0, 100, 100),
            UI_MANAGER,
            container=layout,
            parent_element=layout,
        ),
        choose_file_button := UIButton(
            pygame.Rect(0, 0, 100, 100),
            "Choose File",
            UI_MANAGER,
            container=layout,
            parent_element=layout,
        ),
    )
    layout.add_row("")  # Empty row
    layout.add_row("Download")
    layout.add_row("")  # Empty row
    layout.add_row("Not Available Yet")

    while continue_loop:

        time_delta = CLOCK.tick(PYSDGAME_SETTINGS["FPS"]) / 1000.0
        events = pygame.event.get()
        # Look for quit events
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == choose_file_button:
                        file_dialog = UIFileDialog(
                            pygame.Rect(160, 50, 440, 500),
                            UI_MANAGER,
                            window_title="Load Model File ...",
                            initial_file_path=DESKTOP_DIR,
                            allow_existing_files_only=True,
                        )
                        ## TODO I waws doing the file dialog to read the model

            UI_MANAGER.process_events(event)

        # Handles the actions for pygame widgets
        UI_MANAGER.update(time_delta)

        # Draw methods
        MAIN_DISPLAY.fill(BACK_GROUND_COLOR)
        UI_MANAGER.draw_ui(MAIN_DISPLAY)

        display.update()


##############################################
# Starts the game main loop
##############################################


while True:

    time_delta = CLOCK.tick(PYSDGAME_SETTINGS["FPS"]) / 1000.0
    events = pygame.event.get()
    # Look for quit events
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                for button in buttons:
                    button.hide()
                if event.ui_element == load_game_button:
                    print("Hello load_game_button!")
                if event.ui_element == new_game_button:
                    print("Hello new_game_button!")
                if event.ui_element == import_model_button:
                    start_import_model_loop()
                for button in buttons:
                    button.show()

        UI_MANAGER.process_events(event)

    # Handles the actions for pygame widgets
    UI_MANAGER.update(time_delta)

    # Draw methods
    MAIN_DISPLAY.fill(BACK_GROUND_COLOR)
    UI_MANAGER.draw_ui(MAIN_DISPLAY)

    display.update()
