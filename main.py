"""Open pysdgame main menu.

The main menu loop.
"""
import os
import pathlib
import shutil
import sys
from typing import Dict, List, Tuple
import numpy as np

import pygame
from pygame import display, time, mouse
from pygame.constants import BUTTON_LEFT
import pygame_gui
from pygame_gui.ui_manager import UIManager
from pygame_gui.elements import UIButton, UITextEntryLine, UILabel
from pygame_gui.windows.ui_file_dialog import UIFileDialog
from pygame_gui.windows import UIColourPickerDialog

from pysdgame import PYSDGAME_SETTINGS, logger
from pysdgame.new_game import error_popup, import_game
from pysdgame.utils import HINT_DISPLAY, close_points
from pysdgame.utils.directories import (
    DESKTOP_DIR,
    PYSDGAME_DIR,
    THEMES_DIR,
    find_theme_file,
)
from pysdgame.utils.dynamic_menu import UIColumnContainer, UIFormLayout
from pysdgame.regions_display import (
    RegionComponent,
    RegionsSurface,
    validate_regions_dict,
)
from pysdgame.utils.gui_utils import set_button_color


FPS = PYSDGAME_SETTINGS["FPS"]

pygame.init()
MAIN_DISPLAY = display.set_mode(PYSDGAME_SETTINGS["Resolution"])
BACK_GROUND_COLOR = "black"

CLOCK = time.Clock()
UI_MANAGER = UIManager(
    PYSDGAME_SETTINGS["Resolution"],
    theme_path=find_theme_file(PYSDGAME_SETTINGS["Themes"]["Main Menu"]),
)

REGIONS_DICT: Dict[str, RegionComponent] = {}


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


def start_template_loop():
    """Use as a template for a loop function."""
    continue_loop = True

    while continue_loop:

        time_delta = CLOCK.tick(PYSDGAME_SETTINGS["FPS"]) / 1000.0
        events = pygame.event.get()
        # Look for quit events
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.USEREVENT:
                print(event)

            UI_MANAGER.process_events(event)

        # Handles the actions for pygame widgets
        UI_MANAGER.update(time_delta)

        # Draw methods
        MAIN_DISPLAY.fill(BACK_GROUND_COLOR)
        UI_MANAGER.draw_ui(MAIN_DISPLAY)

        display.update()


def start_regions_loop(background_image_filepath: pathlib.Path = None):
    """Menu for selecting the region."""
    continue_loop = True
    FIRST_POINT: Tuple[int, int] = None
    LEFT_WAS_PRESSED: bool = False
    DRAW_MODE: bool = True  # If the user is drawing smth
    DRAWN_POINTS: List[Tuple] = []

    REGIONS_UI_MANAGER = UIManager(
        PYSDGAME_SETTINGS["Resolution"],
        theme_path=find_theme_file(PYSDGAME_SETTINGS["Themes"]["Main Menu"]),
    )

    main_display_size = MAIN_DISPLAY.get_size()
    menu_width = 200
    name_width = 160
    icons_width = 20
    big_buttons_height = 60

    # Surface to show the background image
    background_surface = (
        pygame.Surface(
            (main_display_size[0] - menu_width, main_display_size[1])
        )
        if background_image_filepath is None
        else pygame.image.load(background_image_filepath)
    )
    # Surface to show the regions on top of it
    regions_surface = pygame.Surface(
        background_surface.get_size(), pygame.SRCALPHA
    )
    background_anchor = (0, 0)

    new_region_button = UIButton(
        pygame.Rect(-menu_width, 0, menu_width, big_buttons_height),
        "New Region",
        REGIONS_UI_MANAGER,
        tool_tip_text="Create a new region",
        anchors={
            "left": "right",
            "right": "right",
            "top": "top",
            "bottom": "bottom",
        },
    )
    stop_drawing_button = UIButton(
        pygame.Rect(
            -menu_width,
            -2 * big_buttons_height,
            menu_width,
            big_buttons_height,
        ),
        "Validate polygon",
        REGIONS_UI_MANAGER,
        tool_tip_text="Stop the current polygon drawing",
        anchors={
            "left": "right",
            "right": "right",
            "top": "bottom",
            "bottom": "bottom",
        },
    )
    stop_drawing_button.hide()

    validate_regions_button = UIButton(
        pygame.Rect(
            -menu_width,
            -big_buttons_height,
            menu_width,
            big_buttons_height,
        ),
        "Validate regions",
        REGIONS_UI_MANAGER,
        anchors={
            "left": "right",
            "right": "right",
            "top": "bottom",
            "bottom": "bottom",
        },
    )

    regions_container = UIColumnContainer(
        pygame.Rect(
            -menu_width,
            big_buttons_height,
            menu_width + 20,
            MAIN_DISPLAY.get_size()[1] - big_buttons_height,
        ),
        REGIONS_UI_MANAGER,
        anchors={
            "left": "right",
            "right": "right",
            "top": "top",
            "bottom": "bottom",
        },
        object_id="regions_container",
    )
    # Add something to remeber the components
    regions_container.component_rows = []

    def _add_region_line(region_component: RegionComponent = None):
        if region_component is None:
            # Create a region component
            name = "Region {}"
            i = 0
            # Ensure the name is not already present
            while name.format(i) in REGIONS_DICT:
                i += 1
            # Find optimal equidistant triangle using x = sqrt(3)/2*y
            # (0,0), (x, 0), (x/2, y)
            region_component = RegionComponent(
                regions_surface,
                pygame.Color(255, 0, 0),
                name=name.format(i),
            )

        # Text Box for the region's name
        region_component.text_box = UITextEntryLine(
            pygame.Rect(0, 0, name_width, 30),
            REGIONS_UI_MANAGER,
            container=regions_container,
        )
        region_component.text_box.set_text(region_component.name)
        region_component.text_box.region_component = region_component

        # Button for region's color selection
        region_component.color_button = UIButton(
            pygame.Rect(name_width, 0, icons_width, 30),
            "",
            REGIONS_UI_MANAGER,
            container=regions_container,
            object_id="color_button",
        )
        # Button for adding polygon
        region_component.new_button = UIButton(
            pygame.Rect(name_width + icons_width, 0, icons_width, 30),
            "+",
            REGIONS_UI_MANAGER,
            container=regions_container,
            object_id="new_poly_button",
        )
        # Set the color of the button to the one of the region
        set_button_color(region_component.color_button, region_component.color)
        region_component.color_button.region_component = region_component
        region_component.new_button.region_component = region_component

        REGIONS_DICT[region_component.name] = region_component
        regions_container.add_row(
            region_component.text_box,
            region_component.color_button,
            region_component.new_button,
        )

    for region in REGIONS_DICT.values():
        # Add existing regions
        _add_region_line(region)
        # Also set the surface for drawing
        region.surface = regions_surface

    while continue_loop:

        time_delta = CLOCK.tick(PYSDGAME_SETTINGS["FPS"]) / 1000.0
        events = pygame.event.get()
        # Look for quit events
        for event in events:
            REGIONS_UI_MANAGER.process_events(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == new_region_button:
                        # Add a new region to be drawn
                        _add_region_line()
                    elif event.ui_element == stop_drawing_button:
                        # Exit the draw mode
                        DRAW_MODE = False
                        # Change available button settings
                        stop_drawing_button.hide()
                        validate_regions_button.show()
                    elif event.ui_element == validate_regions_button:
                        # Register whether the regions chosen are a valid set
                        valid_set = validate_regions_dict(REGIONS_DICT)
                        # Create a new dict to store the regions
                        if valid_set:
                            # Register the region
                            new_REGIONS_DICT = {
                                region.name: region
                                for region in REGIONS_DICT.values()
                            }
                            # Assign the regions to the MAIN dict
                            REGIONS_DICT.clear()
                            for key, item in new_REGIONS_DICT.items():
                                REGIONS_DICT[key] = item
                            # finish start_regions_loop
                            return
                        else:  # Not valid
                            # Problems will already be displayed
                            # by validate_regions_dict()
                            pass
                            # TODO could indicate in the UI what to change

                    elif (
                        event.ui_object_id == "regions_container.color_button"
                    ):
                        # Start a color selection window
                        color_picker = UIColourPickerDialog(
                            pygame.Rect(160, 50, 420, 400),
                            REGIONS_UI_MANAGER,
                            window_title="Change Colour of {}".format(
                                event.ui_element.region_component.name
                            ),
                            initial_colour=pygame.Color(255, 0, 0),
                        )
                        color_picker.region = event.ui_element.region_component
                    elif (
                        event.ui_object_id
                        == "regions_container.new_poly_button"
                    ):
                        # Start to draw a polygon
                        DRAW_MODE = True
                        FIRST_POINT = None
                        event.ui_element.region_component.polygons.append(
                            []  # New list to store the new polygon
                        )
                        # Current polygon points to that list
                        DRAWN_POINTS = (
                            event.ui_element.region_component.polygons[-1]
                        )
                        stop_drawing_button.show()
                        validate_regions_button.hide()

                elif (
                    event.user_type
                    == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED
                ):
                    event.ui_element.region.color = event.colour
                    set_button_color(
                        event.ui_element.region.color_button,
                        event.colour,
                    )
                elif event.user_type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                    text_entry: UITextEntryLine = event.ui_element
                    text_entry.region_component.name = text_entry.get_text()

        if DRAW_MODE:

            # Finds out user mouse movement
            LEFT_PRESSED = mouse.get_pressed()[0]  # 0 is left button
            if not LEFT_PRESSED and LEFT_WAS_PRESSED:  # Release
                # Add the point to polygon
                position = mouse.get_pos()
                if FIRST_POINT is None:
                    FIRST_POINT = position

                bg_size = regions_surface.get_size()
                if position[0] > bg_size[0] or position[1] > bg_size[1]:
                    pass  # out of the drawing screen
                else:
                    # Add the click position to the drawn polygon
                    DRAWN_POINTS.append(position)

            LEFT_WAS_PRESSED = LEFT_PRESSED

        # Handles the actions for pygame widgets
        REGIONS_UI_MANAGER.update(time_delta)

        # Draw methods
        MAIN_DISPLAY.fill(BACK_GROUND_COLOR)
        MAIN_DISPLAY.blit(background_surface, background_anchor)
        regions_surface.fill(pygame.Color(255, 255, 255, 0))
        for key, region in REGIONS_DICT.items():
            region.show()
        MAIN_DISPLAY.blit(regions_surface, background_anchor)
        REGIONS_UI_MANAGER.draw_ui(MAIN_DISPLAY)

        display.update()


def start_newgame_loop():
    """Start a loop for the new game menu."""
    continue_loop = True

    while continue_loop:

        time_delta = CLOCK.tick(PYSDGAME_SETTINGS["FPS"]) / 1000.0
        events = pygame.event.get()
        # Look for quit events
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.USEREVENT:
                print(event)

            UI_MANAGER.process_events(event)

        # Handles the actions for pygame widgets
        UI_MANAGER.update(time_delta)

        # Draw methods
        MAIN_DISPLAY.fill(BACK_GROUND_COLOR)
        UI_MANAGER.draw_ui(MAIN_DISPLAY)

        display.update()


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
        model_file_name_entry := UILabel(
            pygame.Rect(0, 0, 100, 100),
            "",
            UI_MANAGER,
            container=layout,
            parent_element=layout,
        ),
        choose_model_file_button := UIButton(
            pygame.Rect(0, 0, 100, 100),
            "Choose Model File",
            UI_MANAGER,
            container=layout,
            parent_element=layout,
        ),
    )
    model_filepath = None

    layout.add_row(
        "Custom Theme File Path",
        file_name_entry := UILabel(
            pygame.Rect(0, 0, 100, 100),
            "",
            UI_MANAGER,
            container=layout,
            parent_element=layout,
        ),
        choose_theme_file_button := UIButton(
            pygame.Rect(0, 0, 100, 100),
            "Choose Theme File",
            UI_MANAGER,
            container=layout,
            parent_element=layout,
        ),
    )
    theme_filepath = None
    layout.add_row(
        "Background Image",
        background_file_name_entry := UILabel(
            pygame.Rect(0, 0, 100, 100),
            "",
            UI_MANAGER,
            container=layout,
            parent_element=layout,
        ),
        choose_background_file_button := UIButton(
            pygame.Rect(0, 0, 100, 100),
            "Choose Image",
            UI_MANAGER,
            container=layout,
            parent_element=layout,
        ),
    )
    background_filepath = None
    layout.add_row(
        "Regions",
        define_regions_button := UIButton(
            pygame.Rect(0, 0, 100, 100),
            "Define",
            UI_MANAGER,
            container=layout,
            parent_element=layout,
        ),
    )
    layout.add_row("")  # Empty row
    layout.add_row("Download")
    layout.add_row("")  # Empty row
    layout.add_row("Not Available Yet")

    launch_import_button = UIButton(
        pygame.Rect(-250, -150, 200, 100),
        "Launch Import",
        UI_MANAGER,
        tool_tip_text="Will try to import the model into pysdgame",
        anchors={
            "left": "right",
            "right": "right",
            "top": "bottom",
            "bottom": "bottom",
        },
    )

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
                    if event.ui_element == choose_model_file_button:
                        # Choose the file
                        import tkinter as tk
                        from tkinter import filedialog

                        root = tk.Tk()
                        root.withdraw()
                        model_filepath = pathlib.Path(
                            filedialog.askopenfilename(
                                filetypes=[
                                    ("Vensim Model", "*.mdl"),
                                    ("Python PySD", "*.py"),
                                    ("XMILE", "*.xmile"),
                                    ("All Files", "*.*"),
                                ],
                                title="Choose Model File",
                                initialdir=os.environ["HOMEPATH"],
                            )
                        )

                        if os.path.isfile(model_filepath):
                            # Show the file name selected
                            model_file_name_entry.set_text(model_filepath.name)
                    elif event.ui_element == choose_theme_file_button:
                        # Choose the file
                        import tkinter as tk
                        from tkinter import filedialog

                        root = tk.Tk()
                        root.withdraw()
                        theme_filepath = pathlib.Path(
                            filedialog.askopenfilename(
                                filetypes=[
                                    ("Pygamegui theme file", "*.json"),
                                    ("All Files", "*.*"),
                                ],
                                title="Choose Theme File",
                                initialdir=THEMES_DIR,
                            )
                        )

                        if os.path.isfile(theme_filepath):
                            # Show the file name selected
                            file_name_entry.set_text(theme_filepath.stem)
                    elif event.ui_element == choose_background_file_button:
                        # Choose the file
                        import tkinter as tk
                        from tkinter import filedialog

                        root = tk.Tk()
                        root.withdraw()
                        background_filepath = pathlib.Path(
                            filedialog.askopenfilename(
                                filetypes=[
                                    (
                                        "Image Formats Supported by Pygame",
                                        [
                                            "*.jpg",
                                            "*.jpeg",
                                            "*.png",
                                            "*.gif",
                                            "*.bmp",
                                            "*.pcx",
                                            "*.tga",
                                            "*.tif",
                                            "*.lbm",
                                            "*.pbm",
                                            "*.ppm",
                                            "*.xpm",
                                        ],
                                    ),
                                    ("All Files", "*.*"),
                                ],
                                title="Choose Theme File",
                                initialdir=os.environ["HOMEPATH"],
                            )
                        )

                        if os.path.isfile(background_filepath):
                            # Show the file name selected
                            background_file_name_entry.set_text(
                                background_filepath.name
                            )
                    elif event.ui_element == define_regions_button:
                        start_regions_loop(theme_filepath)
                        # Change the name of the button, now that the
                        # regions have been assigned
                        define_regions_button.set_text("Overwrite")
                        logger.debug(
                            "Regions defined: {}".format(REGIONS_DICT)
                        )
                    elif event.ui_element == launch_import_button:
                        try:
                            game_name = game_name_entry.get_text()
                            logger.info("[START] Import new game")
                            import_game(
                                game_name,
                                model_filepath,
                                REGIONS_DICT,
                            )
                        except Exception as exception:
                            # Could not create the new game
                            # Pop the error message to the user
                            error_popup(exception)
                            # Log the exception
                            logger.info("[FAILED] Import new game")
                            logger.exception(exception)

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
