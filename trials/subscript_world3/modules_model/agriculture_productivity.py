"""
Module agriculture_productivity
Translated using PySD version 3.4.0
"""


@component.add(
    name="land yield multiplier from air pollution",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"land_yield_multipler_from_air_pollution_1": 1},
)
def land_yield_multiplier_from_air_pollution():
    """
    Land yield multiplier from air pollution (LYMAP#105).
    """
    return land_yield_multipler_from_air_pollution_1()


@component.add(
    name="land yield multiplier from technology",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"land_yield_factor_1": 1},
)
def land_yield_multiplier_from_technology():
    """
    Land Yield factor (LYF#104)
    """
    return land_yield_factor_1()


@component.add(
    name="land yield technology change rate",
    units="1/year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def land_yield_technology_change_rate():
    """
    Land yield from technology change rate (LYTDR#--)
    """
    return 0


@component.add(
    name="desired food ratio", units="Dmnl", comp_type="Constant", comp_subtype="Normal"
)
def desired_food_ratio():
    """
    desired food ratio (DFR#--)
    """
    return 2


@component.add(
    name="IND OUT IN 1970", units="$/year", comp_type="Constant", comp_subtype="Normal"
)
def ind_out_in_1970():
    """
    INDUSTRIAL OUTPUT IN 1970 (IO70#107.2)
    """
    return 790000000000.0


@component.add(
    name="land yield",
    units="Veg equiv kg/(year*hectare)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "land_yield_multiplier_from_technology": 1,
        "land_fertility": 1,
        "land_yield_multiplier_from_capital": 1,
        "land_yield_multiplier_from_air_pollution": 1,
    },
)
def land_yield():
    """
    LAND YIELD (LY#103)
    """
    return (
        land_yield_multiplier_from_technology()
        * land_fertility()
        * land_yield_multiplier_from_capital()
        * land_yield_multiplier_from_air_pollution()
    )


@component.add(
    name="land yield multiplier from capital",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "agricultural_input_per_hectare": 1,
        "unit_agricultural_input": 1,
        "land_yield_multiplier_from_capital_table": 1,
    },
)
def land_yield_multiplier_from_capital():
    """
    LAND YIELD MULTIPLIER FROM CAPITAL (LYMC#102)
    """
    return land_yield_multiplier_from_capital_table(
        agricultural_input_per_hectare() / unit_agricultural_input()
    )


@component.add(
    name="land yield multiplier from capital table",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_land_yield_multiplier_from_capital_table"
    },
)
def land_yield_multiplier_from_capital_table(x, final_subs=None):
    """
    Table relating agricultural inputs to land yeild (LYMCT#102.1).
    """
    return _hardcodedlookup_land_yield_multiplier_from_capital_table(x, final_subs)


_hardcodedlookup_land_yield_multiplier_from_capital_table = HardcodedLookups(
    [
        0.0,
        40.0,
        80.0,
        120.0,
        160.0,
        200.0,
        240.0,
        280.0,
        320.0,
        360.0,
        400.0,
        440.0,
        480.0,
        520.0,
        560.0,
        600.0,
        640.0,
        680.0,
        720.0,
        760.0,
        800.0,
        840.0,
        880.0,
        920.0,
        960.0,
        1000.0,
    ],
    [
        1.0,
        3.0,
        4.5,
        5.0,
        5.3,
        5.6,
        5.9,
        6.1,
        6.35,
        6.6,
        6.9,
        7.2,
        7.4,
        7.6,
        7.8,
        8.0,
        8.2,
        8.4,
        8.6,
        8.8,
        9.0,
        9.2,
        9.4,
        9.6,
        9.8,
        10.0,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_land_yield_multiplier_from_capital_table",
)


@component.add(
    name="land yield factor 1",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def land_yield_factor_1():
    """
    Land yield factor before policy year (LYF1#104.1).
    """
    return 1


@component.add(
    name="land yield factor 2",
    units="Dmnl",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_land_yield_factor_2": 1},
    other_deps={
        "_smooth_land_yield_factor_2": {
            "initial": {"land_yield_technology": 1, "technology_development_delay": 1},
            "step": {"land_yield_technology": 1, "technology_development_delay": 1},
        }
    },
)
def land_yield_factor_2():
    """
    Land yield factor after policy year (LYF1#104.2).
    """
    return _smooth_land_yield_factor_2()


_smooth_land_yield_factor_2 = Smooth(
    lambda: land_yield_technology(),
    lambda: technology_development_delay(),
    lambda: land_yield_technology(),
    lambda: 3,
    "_smooth_land_yield_factor_2",
)


@component.add(
    name="land yield multipler from air pollution 1",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "industrial_output": 1,
        "ind_out_in_1970": 1,
        "land_yield_multipler_from_air_pollution_table_1": 1,
    },
)
def land_yield_multipler_from_air_pollution_1():
    """
    Land yield multiplier from air pollution before air poll time (LYMAP1#106).
    """
    return land_yield_multipler_from_air_pollution_table_1(
        industrial_output() / ind_out_in_1970()
    )


@component.add(
    name="land yield multipler from air pollution table 1",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_land_yield_multipler_from_air_pollution_table_1"
    },
)
def land_yield_multipler_from_air_pollution_table_1(x, final_subs=None):
    """
    Table relating non-persistent pollution from industry to agricultural output (LYMAPT#106.1).
    """
    return _hardcodedlookup_land_yield_multipler_from_air_pollution_table_1(
        x, final_subs
    )


_hardcodedlookup_land_yield_multipler_from_air_pollution_table_1 = HardcodedLookups(
    [0.0, 10.0, 20.0, 30.0],
    [1.0, 1.0, 0.7, 0.4],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_land_yield_multipler_from_air_pollution_table_1",
)


@component.add(
    name="land yield multiplier from air pollution 2",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "industrial_output": 1,
        "ind_out_in_1970": 1,
        "land_yield_multipler_from_air_pollution_table_2": 1,
    },
)
def land_yield_multiplier_from_air_pollution_2():
    """
    Land yield multiplier from air pollution after air poll time (LYMAP2#107).
    """
    return land_yield_multipler_from_air_pollution_table_2(
        industrial_output() / ind_out_in_1970()
    )


@component.add(
    name="land yield multipler from air pollution table 2",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_land_yield_multipler_from_air_pollution_table_2"
    },
)
def land_yield_multipler_from_air_pollution_table_2(x, final_subs=None):
    """
    Table relating non-persistent pollution from industry to agricultural output (LYMAPT#107.1).
    """
    return _hardcodedlookup_land_yield_multipler_from_air_pollution_table_2(
        x, final_subs
    )


_hardcodedlookup_land_yield_multipler_from_air_pollution_table_2 = HardcodedLookups(
    [0.0, 10.0, 20.0, 30.0],
    [1.0, 1.0, 0.98, 0.95],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_land_yield_multipler_from_air_pollution_table_2",
)


@component.add(
    name="land yield technology change rate multiplier",
    units="1/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "desired_food_ratio": 1,
        "food_ratio": 1,
        "land_yield_technology_change_rate_multiplier_table": 1,
    },
)
def land_yield_technology_change_rate_multiplier():
    """
    Land yield from technology change multiplier (LYCM#--)
    """
    return land_yield_technology_change_rate_multiplier_table(
        desired_food_ratio() - food_ratio()
    )


@component.add(
    name="land yield technology change rate multiplier table",
    units="1/year",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_land_yield_technology_change_rate_multiplier_table"
    },
)
def land_yield_technology_change_rate_multiplier_table(x, final_subs=None):
    """
    Table relating the food ratio gap to the change in agricultural technology (LYCMT#--).
    """
    return _hardcodedlookup_land_yield_technology_change_rate_multiplier_table(
        x, final_subs
    )


_hardcodedlookup_land_yield_technology_change_rate_multiplier_table = HardcodedLookups(
    [0, 1],
    [0, 0],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_land_yield_technology_change_rate_multiplier_table",
)


@component.add(
    name="Land Yield Technology",
    units="Dmnl",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_land_yield_technology": 1},
    other_deps={
        "_integ_land_yield_technology": {
            "initial": {},
            "step": {"land_yield_technology_change_rate": 1},
        }
    },
)
def land_yield_technology():
    """
    LAND YIELD TECHNOLOGY INITIATED (LYTD#--)
    """
    return _integ_land_yield_technology()


_integ_land_yield_technology = Integ(
    lambda: land_yield_technology_change_rate(),
    lambda: 1,
    "_integ_land_yield_technology",
)


@component.add(
    name="land life multiplier from land yield 1",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "land_yield": 1,
        "inherent_land_fertility": 1,
        "land_life_multiplier_from_land_yield_table_1": 1,
    },
)
def land_life_multiplier_from_land_yield_1():
    """
    Land life multiplier from yield before switch time (LLMY1#114).
    """
    return land_life_multiplier_from_land_yield_table_1(
        land_yield() / inherent_land_fertility()
    )


@component.add(
    name="land life multiplier from land yield table 1",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_land_life_multiplier_from_land_yield_table_1"
    },
)
def land_life_multiplier_from_land_yield_table_1(x, final_subs=None):
    """
    Table relating yield to the effect on land life (LLMY1T#114.1).
    """
    return _hardcodedlookup_land_life_multiplier_from_land_yield_table_1(x, final_subs)


_hardcodedlookup_land_life_multiplier_from_land_yield_table_1 = HardcodedLookups(
    [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0],
    [1.2, 1.0, 0.63, 0.36, 0.16, 0.055, 0.04, 0.025, 0.015, 0.01],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_land_life_multiplier_from_land_yield_table_1",
)


@component.add(
    name="land life multiplier from land yield 2",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "land_yield": 1,
        "inherent_land_fertility": 1,
        "land_life_multiplier_from_land_yield_table_2": 1,
    },
)
def land_life_multiplier_from_land_yield_2():
    """
    Land life multiplier from yield after switch time (LLMY2#115).
    """
    return land_life_multiplier_from_land_yield_table_2(
        land_yield() / inherent_land_fertility()
    )


@component.add(
    name="land life multiplier from land yield table 2",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_land_life_multiplier_from_land_yield_table_2"
    },
)
def land_life_multiplier_from_land_yield_table_2(x, final_subs=None):
    """
    Table relating yield to the effect on land life (LLMY2T#115.1).
    """
    return _hardcodedlookup_land_life_multiplier_from_land_yield_table_2(x, final_subs)


_hardcodedlookup_land_life_multiplier_from_land_yield_table_2 = HardcodedLookups(
    [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0],
    [1.2, 1.0, 0.63, 0.36, 0.29, 0.26, 0.24, 0.22, 0.21, 0.2],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_land_life_multiplier_from_land_yield_table_2",
)


@component.add(
    name="marginal land yield multiplier from capital",
    units="hectare/$",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "agricultural_input_per_hectare": 1,
        "unit_agricultural_input": 1,
        "marginal_land_yield_multiplier_from_capital_table": 1,
    },
)
def marginal_land_yield_multiplier_from_capital():
    """
    MARGINAL LAND YIELD MULTIPLIER FROM CAPITAL (MLYMC#111).
    """
    return marginal_land_yield_multiplier_from_capital_table(
        agricultural_input_per_hectare() / unit_agricultural_input()
    )


@component.add(
    name="marginal land yield multiplier from capital table",
    units="hectare/$",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_marginal_land_yield_multiplier_from_capital_table"
    },
)
def marginal_land_yield_multiplier_from_capital_table(x, final_subs=None):
    """
    Table relating agricultural inputs to marginal land yield (MLYMCT#111.1).
    """
    return _hardcodedlookup_marginal_land_yield_multiplier_from_capital_table(
        x, final_subs
    )


_hardcodedlookup_marginal_land_yield_multiplier_from_capital_table = HardcodedLookups(
    [
        0.0,
        40.0,
        80.0,
        120.0,
        160.0,
        200.0,
        240.0,
        280.0,
        320.0,
        360.0,
        400.0,
        440.0,
        480.0,
        520.0,
        560.0,
        600.0,
    ],
    [
        0.075,
        0.03,
        0.015,
        0.011,
        0.009,
        0.008,
        0.007,
        0.006,
        0.005,
        0.005,
        0.005,
        0.005,
        0.005,
        0.005,
        0.005,
        0.005,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_marginal_land_yield_multiplier_from_capital_table",
)


@component.add(
    name="marginal productivity of agricultural inputs",
    units="Veg equiv kg/$",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "average_life_agricultural_inputs": 1,
        "land_yield": 1,
        "marginal_land_yield_multiplier_from_capital": 1,
        "land_yield_multiplier_from_capital": 1,
    },
)
def marginal_productivity_of_agricultural_inputs():
    """
    MARGINAL PRODUCTIVITY OF AGRICULTURAL INPUTS (MPAI#110).
    """
    return (
        average_life_agricultural_inputs()
        * land_yield()
        * marginal_land_yield_multiplier_from_capital()
        / land_yield_multiplier_from_capital()
    )


@component.add(
    name="industrial capital output ratio multiplier from land yield technology",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "land_yield_multiplier_from_technology": 1,
        "industrial_capital_output_ratio_multiplier_table": 1,
    },
)
def industrial_capital_output_ratio_multiplier_from_land_yield_technology():
    """
    CAPITAL OUTPUT YIELD MULTIPLIER (COYM#--)
    """
    return industrial_capital_output_ratio_multiplier_table(
        land_yield_multiplier_from_technology()
    )


@component.add(
    name="industrial capital output ratio multiplier table",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_industrial_capital_output_ratio_multiplier_table"
    },
)
def industrial_capital_output_ratio_multiplier_table(x, final_subs=None):
    """
    Table relating the yield of technology to the effect on the capital output ratio (COYMT#--)
    !
    !
    """
    return _hardcodedlookup_industrial_capital_output_ratio_multiplier_table(
        x, final_subs
    )


_hardcodedlookup_industrial_capital_output_ratio_multiplier_table = HardcodedLookups(
    [1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
    [1.0, 1.05, 1.12, 1.25, 1.35, 1.5],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_industrial_capital_output_ratio_multiplier_table",
)
