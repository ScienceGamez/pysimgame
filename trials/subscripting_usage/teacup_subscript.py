"""
Python model 'teacup.py'
Translated using PySD
"""

from pathlib import Path
import numpy as np
import xarray as xr

from pysd.py_backend.statefuls import Integ
from pysd import Component

__pysd_version__ = "3.0.0"

__data = {"scope": None, "time": lambda: 0}

_root = Path(__file__).parent

# Added the subsrcipt used
_subscript_dict = {"teatype": ["Mint", "Green", "Berries", "Black"]}

component = Component()

#######################################################################
#                          CONTROL VARIABLES                          #
#######################################################################

_control_vars = {
    "initial_time": lambda: 0,
    "final_time": lambda: 30,
    "time_step": lambda: 0.125,
    "saveper": lambda: time_step(),
}


def _init_outer_references(data):
    for key in data:
        __data[key] = data[key]


@component.add(name="Time")
def time():
    """
    Current time of the model.
    """
    return __data["time"]()


@component.add(
    name="FINAL TIME",
    units="Minute",
    comp_type="Constant",
    comp_subtype="Normal",
)
def final_time():
    """
    The final time for the simulation.
    """
    return __data["time"].final_time()


@component.add(
    name="INITIAL TIME",
    units="Minute",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_time():
    """
    The initial time for the simulation.
    """
    return __data["time"].initial_time()


@component.add(
    name="SAVEPER",
    units="Minute",
    limits=(0.0, np.nan),
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_step": 1},
)
def saveper():
    """
    The frequency with which output is stored.
    """
    return __data["time"].saveper()


@component.add(
    name="TIME STEP",
    units="Minute",
    limits=(0.0, np.nan),
    comp_type="Constant",
    comp_subtype="Normal",
)
def time_step():
    """
    The time step for the simulation.
    """
    return __data["time"].time_step()


#######################################################################
#                           MODEL VARIABLES                           #
#######################################################################


@component.add(
    name="Characteristic Time",
    units="Minutes",
    limits=(0.0, np.nan),
    comp_type="Constant",
    comp_subtype="Normal",
)
def characteristic_time():
    """
    How long will it take the teacup to cool 1/e of the way to equilibrium?
    """
    return 10


@component.add(
    name="Heat Loss to Room",
    units="Degrees Celsius/Minute",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "teacup_temperature": 1,
        "room_temperature": 1,
        "characteristic_time": 1,
    },
)
def heat_loss_to_room():
    """
    This is the rate at which heat flows from the cup into the room. We can ignore it at this point.
    """
    return (teacup_temperature() - room_temperature()) / characteristic_time()


@component.add(
    name="Room Temperature",
    units="Degrees Celsius",
    limits=(-459.67, np.nan),
    comp_type="Constant",
    comp_subtype="Normal",
)
def room_temperature():
    """
    Put in a check to ensure the room temperature is not driven below absolute zero.
    """
    return 20


@component.add(
    name="Teacup Temperature",
    units="Degrees Celsius",
    limits=(0.0, 100.0),
    comp_type="Stateful",
    comp_subtype="Integ",
    subscripts=["teatype"],  # Added the subscript
    depends_on={"_integ_teacup_temperature": 1},
    other_deps={
        "_integ_teacup_temperature": {
            "initial": {},
            "step": {"heat_loss_to_room": 1},
        }
    },
)
def teacup_temperature():
    """
    The model is only valid for the liquid phase of tea. While the tea could theoretically freeze or boil off, we would want an error to be thrown in these cases so that the modeler can identify the issue and decide whether to expand the model. Of course, this refers to standard sea-level conditions...
    """
    return _integ_teacup_temperature()


_integ_teacup_temperature = Integ(
    lambda: -heat_loss_to_room(),
    # Added here a data array
    lambda: xr.DataArray(
        # Add a different temp for each type # Base on my boiler recommendation LOL
        [70, 80, 90, 100],
        {"teatype": _subscript_dict["teatype"]},
        ["teatype"],
    ),
    "_integ_teacup_temperature",
)