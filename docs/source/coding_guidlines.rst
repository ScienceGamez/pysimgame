Coding Guidlines
================


Casing
------

PySimGame used lower_snake_case convention for variables.
CamelCase is used for class names.
UPPER_SNAKE_CASE is used for some class variables are instantiated once in the
game and intented to be called by other classes. (ex. managers, displays, ...)

Typing
-----------

typing module should be used for all attributes and arguments.

Docstrings
-----------

Used to document every class and methods.
We use sphinx RST syntax and don't specify the types as all the
attributes and arguments are typed.