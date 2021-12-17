import os
import sys

import pygame
import pygame_gui

# setting path
sys.path.append(os.path.join("."))

from pysimgame.utils.dynamic_menu import UISettingsMenu

pygame.init()


pygame.display.set_caption("Quick Start")
window_surface = pygame.display.set_mode((1400, 1000))
manager = pygame_gui.UIManager((1400, 1000))


background = pygame.Surface((1400, 1000))
background.fill(manager.ui_theme.get_colour("dark_bg"))

menu = UISettingsMenu(pygame.Rect(100, 100, 1000, 700), manager)

hello_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((0, 0), (150, 40)),
    text="Hello",
    manager=manager,
)

menu.add_setting("Menu", None)
menu.add_setting("Make swag", True)
menu.add_setting("Make swag 2", True)
menu.add_setting("Integer", 5)
menu.add_setting("list of string", ["a", "b", "c"])
menu.add_setting("A file path", "README.md")
menu.add_setting("Another file path", "README.md")
menu.values_container.add_row(hello_button)

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
