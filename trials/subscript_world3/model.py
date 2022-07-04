"""
Python model 'model.py'
Translated using PySD
"""

from pathlib import Path
import numpy as np
import xarray as xr

from pysd.py_backend.functions import active_initial, if_then_else
from pysd.py_backend.statefuls import Integ, Smooth, Delay
from pysd.py_backend.lookups import HardcodedLookups
from pysd.py_backend.utils import load_model_data, load_modules
from pysd import Component

__pysd_version__ = "3.4.0"

__data = {"scope": None, "time": lambda: 0}

_root = Path(__file__).parent

_subscript_dict, _modules = load_model_data(_root, "model")

_subscript_ds = xr.Dataset(
    {
        "Region Name": (["Region"], _subscript_dict["Region"]),
    },
    _subscript_dict,
)


def initial_ds(subscript: str, value: int = 1.0) -> xr.DataArray:
    """Generate an automatical initial DataArray with the requested subscripts."""
    size = (
        len(_subscript_ds[subscript])
        if isinstance(subscript, str)
        else tuple([len(_subscript_ds[sub] for sub in subscript)])
    )
    dims = [subscript] if isinstance(subscript, str) else subscript
    coords = {s: _subscript_ds[s] for s in dims}
    return xr.DataArray(np.full(size, value), coords=coords, dims=dims)


component = Component()

#######################################################################
#                          CONTROL VARIABLES                          #
#######################################################################

_control_vars = {
    "initial_time": lambda: 1900,
    "final_time": lambda: 2100,
    "time_step": lambda: 0.5,
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
    units="year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def final_time():
    """
    The time at which simulation stops.
    """
    return __data["time"].final_time()


@component.add(
    name="INITIAL TIME",
    units="year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_time():
    """
    The time at which the simulation begins.
    """
    return __data["time"].initial_time()


@component.add(
    name="SAVEPER",
    units="year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_step": 1},
)
def saveper():
    """
    The frequency with which results are saved.
    """
    return __data["time"].saveper()


@component.add(
    name="TIME STEP", units="year", comp_type="Constant", comp_subtype="Normal"
)
def time_step():
    """
    The time step for computing the model
    """
    return __data["time"].time_step()


#######################################################################
#                           MODEL VARIABLES                           #
#######################################################################

# load modules from modules_model directory
exec(load_modules("modules_model", _modules, _root, []))


@component.add(
    name="GDP pc unit",
    units="$/Person/year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def gdp_pc_unit():
    return 1


@component.add(
    name="unit agricultural input",
    units="$/hectare/year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def unit_agricultural_input():
    return 1


@component.add(
    name="unit population",
    units="Person",
    comp_type="Constant",
    comp_subtype="Normal",
)
def unit_population():
    return 1


@component.add(
    name="one year", units="year", comp_type="Constant", comp_subtype="Normal"
)
def one_year():
    return 1


@component.add(
    name="land fr cult",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"arable_land": 1, "potentially_arable_land_total": 1},
)
def land_fr_cult():
    """
    Land fraction under cultivarion (LFC#84).
    """
    return arable_land() / potentially_arable_land_total()


@component.add(
    name="birth rate",
    units="C/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"thousand": 1, "births": 1, "population": 1},
)
def birth_rate():
    """
    The crude birth rate measured in people per thousand people per year (CBR#31).
    """
    return thousand() * births() / population()


@component.add(
    name="THOUSAND", units="C", comp_type="Constant", comp_subtype="Normal"
)
def thousand():
    """
    Units converted for /1000 rates (--).
    """
    return 1000


@component.add(
    name="death rate",
    units="C/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"thousand": 1, "deaths": 1, "population": 1},
)
def death_rate():
    """
    CRUDE DEATH RATE (CDR#18)
    """
    return thousand() * deaths() / population()


@component.add(
    name="consumed industrial output",
    units="$/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "industrial_output": 1,
        "fraction_of_industrial_output_allocated_to_consumption": 1,
    },
)
def consumed_industrial_output():
    """
    Consumed industrial output (CIO#--).
    """
    return (
        industrial_output()
        * fraction_of_industrial_output_allocated_to_consumption()
    )


@component.add(
    name="consumed industrial output per capita",
    units="$/(Person*year)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"consumed_industrial_output": 1, "population": 1},
)
def consumed_industrial_output_per_capita():
    """
    Consumption Industrial Output per Capita (CIOPC#--)
    """
    return consumed_industrial_output() / population()


@component.add(
    name="fraction of output in agriculture",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "price_of_food": 2,
        "food": 2,
        "industrial_output": 1,
        "service_output": 1,
    },
)
def fraction_of_output_in_agriculture():
    """
    FRACTION OF OUTPUT IN AGRICULTURE (FAO#147)
    """
    return (price_of_food() * food()) / (
        price_of_food() * food() + service_output() + industrial_output()
    )


@component.add(
    name="fraction of output in industry",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "industrial_output": 2,
        "price_of_food": 1,
        "food": 1,
        "service_output": 1,
    },
)
def fraction_of_output_in_industry():
    """
    Fraction of output that is industrial output (FOI#148).
    """
    return industrial_output() / (
        price_of_food() * food() + service_output() + industrial_output()
    )


@component.add(
    name="fraction of output in services",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "service_output": 2,
        "price_of_food": 1,
        "industrial_output": 1,
        "food": 1,
    },
)
def fraction_of_output_in_services():
    """
    FRACTION OF OUTPUT IN SERVICES (FOS#149).
    """
    return service_output() / (
        price_of_food() * food() + service_output() + industrial_output()
    )


@component.add(
    name="PRICE OF FOOD",
    units="$/Veg equiv kg",
    comp_type="Constant",
    comp_subtype="Normal",
)
def price_of_food():
    """
    The price of food used as a basis for comparing agricultural and industrial output. (--).
    """
    return 0.22


@component.add(
    name="resource use intensity",
    units="Resource units/$",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"resource_usage_rate": 1, "industrial_output": 1},
)
def resource_use_intensity():
    """
    ADAPTIVE TECHNOLOGICAL CONTROL CARDS nonrenewable resource usage intensity (RESINT#--)
    """
    return resource_usage_rate() / industrial_output()
