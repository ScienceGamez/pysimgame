"""This module contains two things.

Custom pygame events declaration for pysimgame.
"""
import pygame

# The following file will list all the events from pysimgame
# It is important to register all the events there so that
# when we use networking, the events are register in the same
# order for the clients and server, thus ensuring consistency


# When another region is selected
# {'region': RegionComponent, ?}
RegionFocusChanged = pygame.event.custom_type()
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

# Plotting events
OpenPlot = pygame.event.custom_type()
ClosePlot = pygame.event.custom_type()
