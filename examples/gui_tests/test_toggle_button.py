import pygame
import pygame_gui

import sys
import os

# setting path
sys.path.append(os.path.join("."))

from pysdgame.utils.gui_utils import UI_TOGGLEBUTTON_TOGGLED, UIToggleButton


pygame.init()


pygame.display.set_caption("Quick Start")
window_surface = pygame.display.set_mode((1400, 1000))
manager = pygame_gui.UIManager(
    (1400, 1000),
    theme_path=os.path.join(os.path.dirname(__file__), "theme.json"),
)


background = pygame.Surface((1400, 1000))
background.fill(manager.ui_theme.get_colour("dark_bg"))

toggle_button = UIToggleButton(
    pygame.Rect(200, 100, 150, 50), "toggle", manager
)

hello_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((0, 0), (150, 40)),
    text="Hello",
    manager=manager,
)


clock = pygame.time.Clock()
is_running = True


while is_running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        if (
            event.type == pygame.USEREVENT
            and event.user_type == pygame_gui.UI_BUTTON_PRESSED
            and event.ui_element == hello_button
        ):
            print("Hello World!")
        if (
            event.type == pygame.USEREVENT
            and event.ui_element == toggle_button
        ):
            print(event)
        if (
            event.type == pygame.USEREVENT
            and event.user_type == UI_TOGGLEBUTTON_TOGGLED
        ):
            print(event)
            print("Toggled ", event.value)
        ##if event.type == pygame.USEREVENT:
        # print(event)
        manager.process_events(event)

    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)

    # print(hello_button.hovered, menu.hovered)
    # print(hello_button.layer, menu.layer)
    # print(hello_button.alive(), menu.layer)
    #
    pygame.display.update()
