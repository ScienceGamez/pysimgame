Future ideas and Improvements
=============================


Multiplayer
-----------

Different modes:
Coop: both players can play on the same model
Versus: player play different regions of the model and play against the other

Plot with other tools
---------------------

We want to be able to provide a simple api that connects plot modding
API in pysimgame and external plotting library.

Achievement system
------------------

Include the possibility to set achievements from a modding file, with
easy rules to write achievements.

More Modding:
-------------
* Game Scenario
* Events (hard coded or random)
* model modifications
* initial conditions


Games
-----
* Fighting covid
* Learning of Neural network or ML algos




Technical improvements:
-----------------------

UIHorizontalSlider should send moved event only at the end of the movement.

Make a loading screen for importing model.

Make an abstract model manager and one dedicated to pysd models instead of
pysd being the main one.

Make it possible for each region to simulate a different model type.

Add a 'Values' logging level

Adding stopping conditions (time, funciton of something, target value, ...)

Make the possibility to show custom plots.
Think whether improving the pygame matplotlib backend or just
copying the output of another backend.
