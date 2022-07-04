"""
Module land_development_loss_fertility
Translated using PySD version 3.4.0
"""


@component.add(
    name="Arable Land",
    units="hectare",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_arable_land": 1},
    other_deps={
        "_integ_arable_land": {
            "initial": {"initial_arable_land": 1},
            "step": {
                "land_development_rate": 1,
                "land_erosion_rate": 1,
                "land_removal_for_urban_and_industrial_use": 1,
            },
        }
    },
)
def arable_land():
    """
    Arable land (AL#85).
    """
    return _integ_arable_land()


_integ_arable_land = Integ(
    lambda: land_development_rate()
    - land_erosion_rate()
    - land_removal_for_urban_and_industrial_use(),
    lambda: initial_arable_land(),
    "_integ_arable_land",
)


@component.add(
    name="initial arable land",
    units="hectare",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_arable_land():
    """
    The initial amount of land that is arable. (ALI#85.2).
    """
    return 900000000.0


@component.add(
    name="development cost per hectare",
    units="$/hectare",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "potentially_arable_land": 1,
        "potentially_arable_land_total": 1,
        "development_cost_per_hectare_table": 1,
    },
)
def development_cost_per_hectare():
    """
    Development cost per hectare (DCPH#97).
    """
    return development_cost_per_hectare_table(
        potentially_arable_land() / potentially_arable_land_total()
    )


@component.add(
    name="development cost per hectare table",
    units="$/hectare",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_development_cost_per_hectare_table"},
)
def development_cost_per_hectare_table(x, final_subs=None):
    """
    Table relating undeveloped land to the cost of land development (DCPHT#97.1).
    """
    return _hardcodedlookup_development_cost_per_hectare_table(x, final_subs)


_hardcodedlookup_development_cost_per_hectare_table = HardcodedLookups(
    [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    [
        1.0e05,
        7.4e03,
        5.2e03,
        3.5e03,
        2.4e03,
        1.5e03,
        7.5e02,
        3.0e02,
        1.5e02,
        7.5e01,
        5.0e01,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_development_cost_per_hectare_table",
)


@component.add(
    name="land development rate",
    units="hectare/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "total_agricultural_investment": 1,
        "fraction_of_agricultural_inputs_allocated_to_land_development": 1,
        "development_cost_per_hectare": 1,
    },
)
def land_development_rate():
    """
    The land developmen rate (LDR#96).
    """
    return (
        total_agricultural_investment()
        * fraction_of_agricultural_inputs_allocated_to_land_development()
        / development_cost_per_hectare()
    )


@component.add(
    name="Potentially Arable Land",
    units="hectare",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_potentially_arable_land": 1},
    other_deps={
        "_integ_potentially_arable_land": {
            "initial": {"initial_potentially_arable_land": 1},
            "step": {"land_development_rate": 1},
        }
    },
)
def potentially_arable_land():
    """
    POTENTIALLY ARABLE LAND (PAL#86).
    """
    return _integ_potentially_arable_land()


_integ_potentially_arable_land = Integ(
    lambda: -land_development_rate(),
    lambda: initial_potentially_arable_land(),
    "_integ_potentially_arable_land",
)


@component.add(
    name="initial potentially arable land",
    units="hectare",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_potentially_arable_land():
    """
    The initial amount of potentially arable land (PALI#86.2).
    """
    return 2300000000.0


@component.add(
    name="potentially arable land total",
    units="hectare",
    comp_type="Constant",
    comp_subtype="Normal",
)
def potentially_arable_land_total():
    """
    POTENTIALLY ARABLE LAND TOTAL (PALT#84.1).
    """
    return 3200000000.0


@component.add(
    name="land life multiplier from land yield",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"land_life_multiplier_from_land_yield_1": 1},
)
def land_life_multiplier_from_land_yield():
    """
    LAND LIFE MULTIPLIER FROM YIELD (LLMY#113).
    """
    return land_life_multiplier_from_land_yield_1()


@component.add(
    name="average life of land",
    units="year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "average_life_of_land_normal": 1,
        "land_life_multiplier_from_land_yield": 1,
    },
)
def average_life_of_land():
    """
    Average life of land (ALL#112).
    """
    return average_life_of_land_normal() * land_life_multiplier_from_land_yield()


@component.add(
    name="average life of land normal",
    units="year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def average_life_of_land_normal():
    """
    AVERAGE LIFE OF LAND NORMAL (ALLN#112.1).
    """
    return 1000


@component.add(
    name="land erosion rate",
    units="hectare/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"arable_land": 1, "average_life_of_land": 1},
)
def land_erosion_rate():
    """
    Land erosion rate (LER#
    """
    return arable_land() / average_life_of_land()


@component.add(
    name="land removal for urban and industrial use",
    units="hectare/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "urban_and_industrial_land_required": 1,
        "urban_and_industrial_land": 1,
        "urban_and_industrial_land_development_time": 1,
    },
)
def land_removal_for_urban_and_industrial_use():
    """
    LAND REMOVAL FOR URBAN-INDUSTRIAL USE (LRUI#119).
    """
    return (
        np.maximum(
            0, urban_and_industrial_land_required() - urban_and_industrial_land()
        )
        / urban_and_industrial_land_development_time()
    )


@component.add(
    name="urban and industrial land development time",
    units="year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def urban_and_industrial_land_development_time():
    """
    Urban industrial land development time (UILDT#119.1).
    """
    return 10


@component.add(
    name="urban and industrial land required per capita",
    units="hectare/Person",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "industrial_output_per_capita": 1,
        "gdp_pc_unit": 1,
        "urban_and_industrial_land_required_per_capita_table": 1,
    },
)
def urban_and_industrial_land_required_per_capita():
    """
    Urban industrial land per capita (UILPC#117).
    """
    return urban_and_industrial_land_required_per_capita_table(
        industrial_output_per_capita() / gdp_pc_unit()
    )


@component.add(
    name="urban and industrial land required per capita table",
    units="hectare/Person",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_urban_and_industrial_land_required_per_capita_table"
    },
)
def urban_and_industrial_land_required_per_capita_table(x, final_subs=None):
    """
    Table relating industrial output to urban industrial land (UILPCT#117.1)
    """
    return _hardcodedlookup_urban_and_industrial_land_required_per_capita_table(
        x, final_subs
    )


_hardcodedlookup_urban_and_industrial_land_required_per_capita_table = HardcodedLookups(
    [0.0, 200.0, 400.0, 600.0, 800.0, 1000.0, 1200.0, 1400.0, 1600.0],
    [0.005, 0.008, 0.015, 0.025, 0.04, 0.055, 0.07, 0.08, 0.09],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_urban_and_industrial_land_required_per_capita_table",
)


@component.add(
    name="urban and industrial land required",
    units="hectare",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"urban_and_industrial_land_required_per_capita": 1, "population": 1},
)
def urban_and_industrial_land_required():
    """
    Urban industrial land required (UILR#118).
    """
    return urban_and_industrial_land_required_per_capita() * population()


@component.add(
    name="Urban and Industrial Land",
    units="hectare",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_urban_and_industrial_land": 1},
    other_deps={
        "_integ_urban_and_industrial_land": {
            "initial": {"initial_urban_and_industrial_land": 1},
            "step": {"land_removal_for_urban_and_industrial_use": 1},
        }
    },
)
def urban_and_industrial_land():
    """
    URBAN-INDUSTRIAL LAND (UIL#120).
    """
    return _integ_urban_and_industrial_land()


_integ_urban_and_industrial_land = Integ(
    lambda: land_removal_for_urban_and_industrial_use(),
    lambda: initial_urban_and_industrial_land(),
    "_integ_urban_and_industrial_land",
)


@component.add(
    name="initial urban and industrial land",
    units="hectare",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_urban_and_industrial_land():
    """
    URBAN-INDUSTRIAL LAND INITIAL (UILI#120.1).
    """
    return 8200000.0


@component.add(
    name="land fertility degredation",
    units="Veg equiv kg/(year*year*hectare)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"land_fertility": 1, "land_fertility_degredation_rate": 1},
)
def land_fertility_degredation():
    """
    LAND FERTILITY DEGRADATION (LFD#123).
    """
    return land_fertility() * land_fertility_degredation_rate()


@component.add(
    name="land fertility degredation rate",
    units="1/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "persistent_pollution_index": 1,
        "land_fertility_degredation_rate_table": 1,
    },
)
def land_fertility_degredation_rate():
    """
    Land fertility degradation rate (LFDR#122).
    """
    return land_fertility_degredation_rate_table(persistent_pollution_index())


@component.add(
    name="land fertility degredation rate table",
    units="1/year",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_land_fertility_degredation_rate_table"},
)
def land_fertility_degredation_rate_table(x, final_subs=None):
    """
    Table relating persistent pollution to land fertility degradation (LFDRT#122.1).
    """
    return _hardcodedlookup_land_fertility_degredation_rate_table(x, final_subs)


_hardcodedlookup_land_fertility_degredation_rate_table = HardcodedLookups(
    [0.0, 10.0, 20.0, 30.0],
    [0.0, 0.1, 0.3, 0.5],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_land_fertility_degredation_rate_table",
)


@component.add(
    name="Land Fertility",
    units="Veg equiv kg/(year*hectare)",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_land_fertility": 1},
    other_deps={
        "_integ_land_fertility": {
            "initial": {"initial_land_fertility": 1},
            "step": {"land_fertility_regeneration": 1, "land_fertility_degredation": 1},
        }
    },
)
def land_fertility():
    """
    Land fertility (LFERT#121).
    """
    return _integ_land_fertility()


_integ_land_fertility = Integ(
    lambda: land_fertility_regeneration() - land_fertility_degredation(),
    lambda: initial_land_fertility(),
    "_integ_land_fertility",
)


@component.add(
    name="initial land fertility",
    units="Veg equiv kg/(year*hectare)",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_land_fertility():
    """
    LAND FERTILITY INITIAL (LFERTI#121.2)
    """
    return 600


@component.add(
    name="inherent land fertility",
    units="Veg equiv kg/(year*hectare)",
    comp_type="Constant",
    comp_subtype="Normal",
)
def inherent_land_fertility():
    """
    INHERENT LAND FERTILITY (ILF#124.1).
    """
    return 600


@component.add(
    name="land fertility regeneration",
    units="Veg equiv kg/(year*year*hectare)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "inherent_land_fertility": 1,
        "land_fertility": 1,
        "land_fertility_regeneration_time": 1,
    },
)
def land_fertility_regeneration():
    """
    Land fertility regeneration (LFR#124).
    """
    return (
        inherent_land_fertility() - land_fertility()
    ) / land_fertility_regeneration_time()


@component.add(
    name="land fertility regeneration time",
    units="year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "fraction_of_agricultural_inputs_for_land_maintenance": 1,
        "land_fertility_regeneration_time_table": 1,
    },
)
def land_fertility_regeneration_time():
    """
    LAND FERTILITY REGENERATION TIME (LFRT#125)
    """
    return land_fertility_regeneration_time_table(
        fraction_of_agricultural_inputs_for_land_maintenance()
    )


@component.add(
    name="land fertility regeneration time table",
    units="year",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_land_fertility_regeneration_time_table"
    },
)
def land_fertility_regeneration_time_table(x, final_subs=None):
    """
    Table relating inputs to land maintenance to land fertility regeneration (LFRTT#125.1).
    """
    return _hardcodedlookup_land_fertility_regeneration_time_table(x, final_subs)


_hardcodedlookup_land_fertility_regeneration_time_table = HardcodedLookups(
    [0.0, 0.02, 0.04, 0.06, 0.08, 0.1],
    [20.0, 13.0, 8.0, 4.0, 2.0, 2.0],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_land_fertility_regeneration_time_table",
)


@component.add(
    name="fraction of agricultural inputs allocated to land development",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "marginal_productivity_of_land_development": 1,
        "marginal_productivity_of_agricultural_inputs": 1,
        "fraction_of_agricultural_inputs_allocated_to_land_development_table": 1,
    },
)
def fraction_of_agricultural_inputs_allocated_to_land_development():
    """
    Fraction of inputs allocated to land devlelopment (FIALD#108).
    """
    return fraction_of_agricultural_inputs_allocated_to_land_development_table(
        marginal_productivity_of_land_development()
        / marginal_productivity_of_agricultural_inputs()
    )


@component.add(
    name="fraction of agricultural inputs allocated to land development table",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_fraction_of_agricultural_inputs_allocated_to_land_development_table"
    },
)
def fraction_of_agricultural_inputs_allocated_to_land_development_table(
    x, final_subs=None
):
    """
    Table relating the marginal productivity of land to the fraction of inputs allocated to new land development (FIALDT#108.1).
    """
    return _hardcodedlookup_fraction_of_agricultural_inputs_allocated_to_land_development_table(
        x, final_subs
    )


_hardcodedlookup_fraction_of_agricultural_inputs_allocated_to_land_development_table = HardcodedLookups(
    [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0],
    [0.0, 0.05, 0.15, 0.3, 0.5, 0.7, 0.85, 0.95, 1.0],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_fraction_of_agricultural_inputs_allocated_to_land_development_table",
)


@component.add(
    name="marginal productivity of land development",
    units="Veg equiv kg/$",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "land_yield": 1,
        "development_cost_per_hectare": 1,
        "social_discount": 1,
    },
)
def marginal_productivity_of_land_development():
    """
    The marginal productivity of land development (MPLD#109)
    """
    return land_yield() / (development_cost_per_hectare() * social_discount())


@component.add(
    name="social discount", units="1/year", comp_type="Constant", comp_subtype="Normal"
)
def social_discount():
    """
    SOCIAL DISCOUNT (SD#109.1)
    """
    return 0.07
