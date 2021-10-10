"""Script used to store points for a region.

A pygame interface pops with the map.
You can then click at points on the map to create a polygon of a particular
region.
The points are printed out in the terminal.
You can press space if you want to keep track of different regions
"""

import os
import sys

import pygame
from pygame import display, event, mouse
from pygame.constants import MOUSEBUTTONDOWN


FPS = 30
clock = pygame.time.Clock()
MAIN_DISPLAY = display.set_mode((2100, 1080))

img_file_path = os.path.join(
    "earth_maps", "world_bluemarble.jpg_2100x1080.jpg"
)
img = pygame.image.load(img_file_path)

MAIN_DISPLAY.blit(img, (0, 0))

mouse_previous_state = mouse.get_pressed()[0]
while True:
    events = event.get()
    # Loop for quit events
    for ev in events:
        if ev.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if ev.type == pygame.TEXTINPUT:
            print(ev.text)
    if mouse_previous_state and mouse.get_pressed()[0]:
        print(','.join([str(i) for i in mouse.get_pos()]))
    mouse_previous_state = mouse.get_pressed()[0]
    MAIN_DISPLAY.blit(img, (0, 0))

    pygame.display.update()
    clock.tick(FPS)