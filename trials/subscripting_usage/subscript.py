"""
Python model 'subscript.py'
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


_subscript_dict = {"One Dimensional Subscript": ["Entry 1", "Entry 2", "Entry 3"]}

component = Component()

#######################################################################
#                          CONTROL VARIABLES                          #
#######################################################################

_control_vars = {
    "initial_time": lambda: 0,
    "final_time": lambda: 100,
    "time_step": lambda: 1,
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
    name="FINAL TIME", units="Month", comp_type="Constant", comp_subtype="Normal"
)
def final_time():
    """
    The final time for the simulation.
    """
    return __data["time"].final_time()


@component.add(
    name="INITIAL TIME", units="Month", comp_type="Constant", comp_subtype="Normal"
)
def initial_time():
    """
    The initial time for the simulation.
    """
    return __data["time"].initial_time()


@component.add(
    name="SAVEPER",
    units="Month",
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
    units="Month",
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
    name="Inflow A",
    subscripts=["One Dimensional Subscript"],
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"rate_a": 1},
)
def inflow_a():
    return rate_a()


@component.add(
    name="Stock A",
    subscripts=["One Dimensional Subscript"],
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_stock_a": 1},
    other_deps={"_integ_stock_a": {"initial": {}, "step": {"inflow_a": 1}}},
)
def stock_a():
    return _integ_stock_a()


_integ_stock_a = Integ(
    lambda: inflow_a(),
    lambda: xr.DataArray(
        0,
        {"One Dimensional Subscript": _subscript_dict["One Dimensional Subscript"]},
        ["One Dimensional Subscript"],
    ),
    "_integ_stock_a",
)


@component.add(
    name="Rate A",
    subscripts=["One Dimensional Subscript"],
    comp_type="Constant",
    comp_subtype="Normal",
)
def rate_a():
    return xr.DataArray(
        [0.01, 0.02, 0.03],
        {"One Dimensional Subscript": _subscript_dict["One Dimensional Subscript"]},
        ["One Dimensional Subscript"],
    )
