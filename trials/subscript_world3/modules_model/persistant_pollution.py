"""
Module persistant_pollution
Translated using PySD version 3.4.0
"""


@component.add(
    name="industrial capital output ratio multiplier from pollution technology",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "persistent_pollution_generation_factor": 1,
        "industrial_capital_output_ratio_multiplier_from_pollution_table": 1,
    },
)
def industrial_capital_output_ratio_multiplier_from_pollution_technology():
    """
    Pollution control technology multiplier for capital output ratio (COPM#--).
    """
    return industrial_capital_output_ratio_multiplier_from_pollution_table(
        persistent_pollution_generation_factor()
    )


@component.add(
    name="industrial capital output ratio multiplier from pollution table",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_industrial_capital_output_ratio_multiplier_from_pollution_table"
    },
)
def industrial_capital_output_ratio_multiplier_from_pollution_table(x, final_subs=None):
    """
    Table relating pollution correction technology to the capital output ratio (COPMT#--)
    """
    return _hardcodedlookup_industrial_capital_output_ratio_multiplier_from_pollution_table(
        x, final_subs
    )


_hardcodedlookup_industrial_capital_output_ratio_multiplier_from_pollution_table = HardcodedLookups(
    [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    [1.25, 1.2, 1.15, 1.11, 1.08, 1.05, 1.03, 1.02, 1.01, 1.0, 1.0],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_industrial_capital_output_ratio_multiplier_from_pollution_table",
)


@component.add(
    name="persistent pollution technology change rate",
    units="1/year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def persistent_pollution_technology_change_rate():
    """
    pollution control technology change rate (PTDR#--)
    """
    return 0


@component.add(
    name="persistent pollution generation factor",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"persistent_pollution_generation_factor_1": 1},
)
def persistent_pollution_generation_factor():
    """
    PERSISTENT POLLUTION GENERATED FACTOR (PPGF#138).
    """
    return persistent_pollution_generation_factor_1()


@component.add(
    name="agricultural material toxicity index",
    units="Pollution units/$",
    comp_type="Constant",
    comp_subtype="Normal",
)
def agricultural_material_toxicity_index():
    """
    Agricultural material toxicity index (AMTI#140.2).
    """
    return 1


@component.add(
    name="assimilation half life",
    units="year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "assimilation_half_life_in_1970": 1,
        "assimilation_half_life_multiplier": 1,
    },
)
def assimilation_half_life():
    """
    ASSIMILATION HALF-LIFE (AHL#146).
    """
    return assimilation_half_life_in_1970() * assimilation_half_life_multiplier()


@component.add(
    name="assimilation half life in 1970",
    units="year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def assimilation_half_life_in_1970():
    """
    Assimilation half life of persistent pollution int 1970 (AHL70#146.1).
    """
    return 1.5


@component.add(
    name="assimilation half life multiplier",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "persistent_pollution_index": 1,
        "assimilation_half_life_mult_table": 1,
    },
)
def assimilation_half_life_multiplier():
    """
    Assimilation half life of multiplier of persistent pollution (AHLM#145)
    """
    return assimilation_half_life_mult_table(persistent_pollution_index())


@component.add(
    name="assimilation half life mult table",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_assimilation_half_life_mult_table"},
)
def assimilation_half_life_mult_table(x, final_subs=None):
    """
    Table relating the level of persisten pollution to its assimilation rate (AHLMT#145.1).
    """
    return _hardcodedlookup_assimilation_half_life_mult_table(x, final_subs)


_hardcodedlookup_assimilation_half_life_mult_table = HardcodedLookups(
    [1, 251, 501, 751, 1001],
    [1, 11, 21, 31, 41],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_assimilation_half_life_mult_table",
)


@component.add(
    name="desired persistent pollution index",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def desired_persistent_pollution_index():
    """
    Desires persistent pollution index (DPOLX#--).
    """
    return 1.2


@component.add(
    name="fraction of agricultural inputs from persistent materials",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def fraction_of_agricultural_inputs_from_persistent_materials():
    """
    Fraction of inputs as persistent materials (FIPM#140.1).
    """
    return 0.001


@component.add(
    name="fraction of resources from persistent materials",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def fraction_of_resources_from_persistent_materials():
    """
    Fraction of resources as persistent materials (FRPM#139.1)
    """
    return 0.02


@component.add(
    name="industrial material toxicity index",
    units="Pollution units/Resource unit",
    comp_type="Constant",
    comp_subtype="Normal",
)
def industrial_material_toxicity_index():
    """
    Industrial materials toxicity index (IMTI#139.3)
    """
    return 10


@component.add(
    name="industrial material emissions factor",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def industrial_material_emissions_factor():
    """
    Industrial materials emission factor (IMEF#139.2).
    """
    return 0.1


@component.add(
    name="persistent pollution generation factor 1",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def persistent_pollution_generation_factor_1():
    """
    Persistent pollution generation factor before policy time (PPGF1#138.1).
    """
    return 1


@component.add(
    name="persistent pollution generation factor 2",
    units="Dmnl",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_persistent_pollution_generation_factor_2": 1},
    other_deps={
        "_smooth_persistent_pollution_generation_factor_2": {
            "initial": {
                "persistent_pollution_technology": 1,
                "technology_development_delay": 1,
            },
            "step": {
                "persistent_pollution_technology": 1,
                "technology_development_delay": 1,
            },
        }
    },
)
def persistent_pollution_generation_factor_2():
    """
    Persistent pollution generation factor after policy time (PPGF1#138.2).
    """
    return _smooth_persistent_pollution_generation_factor_2()


_smooth_persistent_pollution_generation_factor_2 = Smooth(
    lambda: persistent_pollution_technology(),
    lambda: technology_development_delay(),
    lambda: persistent_pollution_technology(),
    lambda: 3,
    "_smooth_persistent_pollution_generation_factor_2",
)


@component.add(
    name="persistent pollution technology change multiplier",
    units="1/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "persistent_pollution_index": 1,
        "desired_persistent_pollution_index": 1,
        "persistent_pollution_technology_change_mult_table": 1,
    },
)
def persistent_pollution_technology_change_multiplier():
    """
    POLLUTION CONTROL TECHNOLOGY CHANGE MULTIPLIER (POLGFM#--).
    """
    return persistent_pollution_technology_change_mult_table(
        1 - persistent_pollution_index() / desired_persistent_pollution_index()
    )


@component.add(
    name="persistent pollution technology change mult table",
    units="1/year",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_persistent_pollution_technology_change_mult_table"
    },
)
def persistent_pollution_technology_change_mult_table(x, final_subs=None):
    """
    Table relating persisten pollution to changes due to technology (POLGFMT#--).
    """
    return _hardcodedlookup_persistent_pollution_technology_change_mult_table(
        x, final_subs
    )


_hardcodedlookup_persistent_pollution_technology_change_mult_table = HardcodedLookups(
    [-1, 0],
    [0, 0],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_persistent_pollution_technology_change_mult_table",
)


@component.add(
    name="Persistent Pollution",
    units="Pollution units",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_persistent_pollution": 1},
    other_deps={
        "_integ_persistent_pollution": {
            "initial": {"initial_persistent_pollution": 1},
            "step": {
                "persistent_pollution_appearance_rate": 1,
                "persistent_pollution_assimilation_rate": 1,
            },
        }
    },
)
def persistent_pollution():
    """
    Persistent pollution (PPOL#142).
    """
    return _integ_persistent_pollution()


_integ_persistent_pollution = Integ(
    lambda: persistent_pollution_appearance_rate()
    - persistent_pollution_assimilation_rate(),
    lambda: initial_persistent_pollution(),
    "_integ_persistent_pollution",
)


@component.add(
    name="initial persistent pollution",
    units="Pollution units",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_persistent_pollution():
    """
    persistent pollution initial (PPOLI#142.2
    """
    return 25000000.0


@component.add(
    name="persistent pollution generation industry",
    units="Pollution units/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "per_capita_resource_use_multiplier": 1,
        "population": 1,
        "fraction_of_resources_from_persistent_materials": 1,
        "industrial_material_emissions_factor": 1,
        "industrial_material_toxicity_index": 1,
    },
)
def persistent_pollution_generation_industry():
    """
    Persistent pollution generated by industrial output. (PPGIO#139)
    """
    return (
        per_capita_resource_use_multiplier()
        * population()
        * fraction_of_resources_from_persistent_materials()
        * industrial_material_emissions_factor()
        * industrial_material_toxicity_index()
    )


@component.add(
    name="persistent pollution generation agriculture",
    units="Pollution units/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "agricultural_input_per_hectare": 1,
        "arable_land": 1,
        "fraction_of_agricultural_inputs_from_persistent_materials": 1,
        "agricultural_material_toxicity_index": 1,
    },
)
def persistent_pollution_generation_agriculture():
    """
    Persistent pollution generated by agriculture (PPGAO#140)
    """
    return (
        agricultural_input_per_hectare()
        * arable_land()
        * fraction_of_agricultural_inputs_from_persistent_materials()
        * agricultural_material_toxicity_index()
    )


@component.add(
    name="persistent pollution generation rate",
    units="Pollution units/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "persistent_pollution_generation_industry": 1,
        "persistent_pollution_generation_agriculture": 1,
        "persistent_pollution_generation_factor": 1,
    },
)
def persistent_pollution_generation_rate():
    """
    PERSISTENT POLLUTION GENERATION RATE (PPGR#137).
    """
    return (
        persistent_pollution_generation_industry()
        + persistent_pollution_generation_agriculture()
    ) * persistent_pollution_generation_factor()


@component.add(
    name="persistent pollution appearance rate",
    units="Pollution units/year",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delay_persistent_pollution_appearance_rate": 1},
    other_deps={
        "_delay_persistent_pollution_appearance_rate": {
            "initial": {
                "persistent_pollution_generation_rate": 1,
                "persistent_pollution_transmission_delay": 1,
            },
            "step": {
                "persistent_pollution_generation_rate": 1,
                "persistent_pollution_transmission_delay": 1,
            },
        }
    },
)
def persistent_pollution_appearance_rate():
    """
    Persistent pollution appearance rate (PPAPR#141)
    """
    return _delay_persistent_pollution_appearance_rate()


_delay_persistent_pollution_appearance_rate = Delay(
    lambda: persistent_pollution_generation_rate(),
    lambda: persistent_pollution_transmission_delay(),
    lambda: persistent_pollution_generation_rate(),
    lambda: 3,
    time_step,
    "_delay_persistent_pollution_appearance_rate",
)


@component.add(
    name="persistent pollution assimilation rate",
    units="Pollution units/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"persistent_pollution": 1, "assimilation_half_life": 1},
)
def persistent_pollution_assimilation_rate():
    """
    PERSISTENT POLLUTION ASSIMILATION RATE (PPASR#144).
    """
    return persistent_pollution() / (assimilation_half_life() * 1.4)


@component.add(
    name="persistent pollution in 1970",
    units="Pollution units",
    comp_type="Constant",
    comp_subtype="Normal",
)
def persistent_pollution_in_1970():
    """
    PERSISTENT POLLUTION IN 1970 (PPOL70#143.1).
    """
    return 136000000.0


@component.add(
    name="persistent pollution index",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"persistent_pollution": 1, "persistent_pollution_in_1970": 1},
)
def persistent_pollution_index():
    """
    Persistent pollution index relative to 1970 (PPOLX#143).
    """
    return persistent_pollution() / persistent_pollution_in_1970()


@component.add(
    name="Persistent Pollution Technology",
    units="Dmnl",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_persistent_pollution_technology": 1},
    other_deps={
        "_integ_persistent_pollution_technology": {
            "initial": {},
            "step": {"persistent_pollution_technology_change_rate": 1},
        }
    },
)
def persistent_pollution_technology():
    """
    Pollution control technology initiated (PTD#--)
    """
    return _integ_persistent_pollution_technology()


_integ_persistent_pollution_technology = Integ(
    lambda: persistent_pollution_technology_change_rate(),
    lambda: 1,
    "_integ_persistent_pollution_technology",
)


@component.add(
    name="persistent pollution transmission delay",
    units="year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def persistent_pollution_transmission_delay():
    """
    Persistent pollution transmission delay (PPTD#141.1).
    """
    return 20


@component.add(
    name="technology development delay",
    units="year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def technology_development_delay():
    """
    The technology development delay (TDD#--)
    """
    return 20


@component.add(
    name="persistent pollution intensity industry",
    units="Pollution units/$",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "persistent_pollution_generation_industry": 1,
        "persistent_pollution_generation_factor": 1,
        "industrial_output": 1,
    },
)
def persistent_pollution_intensity_industry():
    """
    pollution intensity indicator (PLINID#--).
    """
    return (
        persistent_pollution_generation_industry()
        * persistent_pollution_generation_factor()
        / industrial_output()
    )
