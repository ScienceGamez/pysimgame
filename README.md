# PySimGame

[![Documentation Status](https://readthedocs.org/projects/pysimgame/badge/?version=latest)](https://pysimgame.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
<a href="http://www.wtfpl.net/"><img
       src="http://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-4.png"
       width="80" height="15" alt="WTFPL" /></a>


A simple pygame interface that allows to run, visualize and interact
with simulation models.

It has been developped for running pysd models, but the plan is
to make it compatible with other simulation packages.

A full documentation is available on [read the docs](https://pysimgame.readthedocs.io/en/latest/)

## Current developpement
The package is still under developpement so nothing is guaranted
to work yet, but if you are interested you are welcome to contact
us to see whether we can improve something or implement your ideas.

## Principles

The goal is to be able to play with a simulation. A player can select some options that will modify some components of the simulation such that every game can be a different story made on the simulation.

If you want to play with World models that simulate the future of humanity, want to play the role of a governement fighting a pandemic or simply mess around with a basic predator-pray model,
you are at the right place !

Our goal is to make it as easy as possible to create interaction capabilities with simulations.

pysimgame has been developped with the idea of making modding as easy
as possible, such that one can implement new models, but also
ways to interact with the models during the game and control
of the graphics.

All the code is written in python and uses python libraries for
running the games.

The pygame model can run multiple models in parallel in the simulation.
We call *regions* the different models running in parallel.

Regions can communicate between each other using Links which
It is possible to change parameters of the model using Actions which
are usable by the players.


### License



The licence is called a Do What the Fuck You Want to Public Licence.
So you can Do What the Fuck You Want with the code.
