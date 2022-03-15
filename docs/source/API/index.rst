pysimgame offers a basic api for game components.
It uses object oriented programming for creating
components that interact together.

Components are all charge of handling a special part of
the game.

One main component, the :py:class:`pysimgame.GameManager` is in charge
of bringing all the components together.


The different component interact together using pygame events.
This will help future implementation that handle online communcation,
using proxy managers for the online data transfers.

At the initialization, the GameManager initalize all the other components,
calling the :py:method:`__init__` method.
Once all the classes are initialized, it calls the :py:method:`connect`
method of each component, during which every component will read information
from the others.
During these 2 phases, the game manager will show a loading screen to
the player.
After that, the game is ready to go.

Typcially, all the manager inherit form the :py:class:`AbstractManager` that
provides a bone for each manager.
To simplify the modding capabilities, each component described below
should have in the future an AbstractManager as well, with
the basic features already implemmented. (reading events, initialization, ...)

Different components handle each part of the game.
In the base configuration the following components are used:

1. The Game Manager:
    It is the main component of the game, putting together all other
    components
2. The Model Manager:
    In charge of running the simulation, it handles model steps.
    It usually runs on a separate thread/process for performances.
3. The UI manager:
    This one is special, as it does not inherit from :py:class:`AbstractManager`
    but comes from the :py:module:`pygame_gui` library.
    It is used to show all the GUI components such as menus, buttons, widgets, ...
4. The PlotManager:
    Handles all the computation required for showing the plots on the picture.
    Mainly listen on the ModelManager and updates the plot after a step.
5. Actions Manager:
    There are several manager for the different actions available for the
    player. They manage the modifications of the model once the player select
    any action.
6. SpeedManager:
    The :py:class:`pysimgame.SpeedManager` handles the speed at which the
    model is run, from the UI to the backend.
7. StatisticsDisplayManager:
    The statistics are read from the ModelManager and then displayed to
    the user thanks to the :py:class:`pysimgage.StatisticsDisplayManager`
8. RegionsManager:
    This manager is very special as it allows the selection of the different
    regions of the model.
    This one will change on each game, as region can represent some totally
    different ideas depending on what the model is running on.
    See the region documentation for more information.
