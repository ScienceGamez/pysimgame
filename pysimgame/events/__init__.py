"""This module contains two things.

Custom pygame events declaration for pysimgame.
"""
import pygame

# When an action is trigger
# {'action', ?}
ActionUsed = pygame.event.custom_type()
# When a pysimgame event is started during the game
# {'event', ?}
EventStarted = pygame.event.custom_type()

# The simulation speed is changed
# {'fps'}
SpeedChanged = pygame.event.custom_type()

# A simulation step has ended
# {}
ModelStepped = pygame.event.custom_type()

# Pause event
# TODO: change other type of communcation of that event
# {}
TogglePaused = pygame.event.custom_type()
Paused = pygame.event.custom_type()
UnPaused = pygame.event.custom_type()
