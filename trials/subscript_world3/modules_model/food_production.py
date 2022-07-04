"""
Module food_production
Translated using PySD version 3.4.0
"""


@component.add(
    name="fraction of industrial output allocated to agriculture",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"fraction_of_industrial_output_allocated_to_agriculture_1": 1},
)
def fraction_of_industrial_output_allocated_to_agriculture():
    """
    FRACTION OF INDUSTRIAL OUTPUT ALLOCATED TO AGRICULTURE (FIOAA#93).
    """
    return fraction_of_industrial_output_allocated_to_agriculture_1()


@component.add(
    name="indicated food per capita",
    units="Veg equiv kg/(Person*year)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"indicated_food_per_capita_1": 1},
)
def indicated_food_per_capita():
    """
    Indicated food per capita (IFPC#89).
    """
    return indicated_food_per_capita_1()


@component.add(
    name="food",
    units="Veg equiv kg/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "land_yield": 1,
        "arable_land": 1,
        "land_fraction_harvested": 1,
        "processing_loss": 1,
    },
)
def food():
    """
    The total amount of usable food (F#87).
    """
    return (
        land_yield()
        * arable_land()
        * land_fraction_harvested()
        * (1 - processing_loss())
    )


@component.add(
    name="food per capita",
    units="Veg equiv kg/(Person*year)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"food": 1, "population": 1},
)
def food_per_capita():
    """
    Food per capita (FPC#88)
    """
    return food() / population()


@component.add(
    name="land fraction harvested",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def land_fraction_harvested():
    """
    Land fraction harvested (LFH#87.1).
    """
    return 0.7


@component.add(
    name="fraction of industrial output allocated to agriculture 1",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "food_per_capita": 1,
        "indicated_food_per_capita": 1,
        "fraction_industrial_output_allocated_to_agriculture_table_1": 1,
    },
)
def fraction_of_industrial_output_allocated_to_agriculture_1():
    """
    Fraction of industrial output allocated to agriculture before policy time (FIOAA1#94).
    """
    return fraction_industrial_output_allocated_to_agriculture_table_1(
        food_per_capita() / indicated_food_per_capita()
    )


@component.add(
    name="fraction industrial output allocated to agriculture table 1",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_fraction_industrial_output_allocated_to_agriculture_table_1"
    },
)
def fraction_industrial_output_allocated_to_agriculture_table_1(
    x, final_subs={"Region": _subscript_ds["Region"]}
):
    """
    Table relating food per capita to the fraction of industrial output allocated to agriculture (FIOAA1T#94.1).
    """
    return _hardcodedlookup_fraction_industrial_output_allocated_to_agriculture_table_1(
        x, final_subs
    )


_hardcodedlookup_fraction_industrial_output_allocated_to_agriculture_table_1 = HardcodedLookups(
    [0.0, 0.5, 1.0, 1.5, 2.0, 2.5],
    [0.4, 0.2, 0.1, 0.025, 0.0, 0.0],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_fraction_industrial_output_allocated_to_agriculture_table_1",
)


@component.add(
    name="fraction of industrial output allocated to agriculture 2",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "food_per_capita": 1,
        "indicated_food_per_capita": 1,
        "fraction_industrial_output_allocated_to_agriculture_table_2": 1,
    },
)
def fraction_of_industrial_output_allocated_to_agriculture_2():
    """
    Fraction of industrial output allocated to agriculture after policy time (FIOAA2#95).
    """
    return fraction_industrial_output_allocated_to_agriculture_table_2(
        food_per_capita() / indicated_food_per_capita()
    )


@component.add(
    name="fraction industrial output allocated to agriculture table 2",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_fraction_industrial_output_allocated_to_agriculture_table_2"
    },
)
def fraction_industrial_output_allocated_to_agriculture_table_2(
    x, final_subs=None
):
    """
    Table relating food per capita to the fraction of industrial output allocated to agriculture (FIOAA2T#95.1).
    """
    return _hardcodedlookup_fraction_industrial_output_allocated_to_agriculture_table_2(
        x, final_subs
    )


_hardcodedlookup_fraction_industrial_output_allocated_to_agriculture_table_2 = HardcodedLookups(
    [0.0, 0.5, 1.0, 1.5, 2.0, 2.5],
    [0.4, 0.2, 0.1, 0.025, 0.0, 0.0],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_fraction_industrial_output_allocated_to_agriculture_table_2",
)


@component.add(
    name="indicated food per capita 1",
    units="Veg equiv kg/(Person*year)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "industrial_output_per_capita": 1,
        "gdp_pc_unit": 1,
        "indicated_food_per_capita_table_1": 1,
    },
)
def indicated_food_per_capita_1():
    """
    Indicated foord per capita befor policy time (IFPC1#90).
    """
    return indicated_food_per_capita_table_1(
        industrial_output_per_capita() / gdp_pc_unit()
    )


@component.add(
    name="indicated food per capita table 1",
    units="Veg equiv kg/(Person*year)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_indicated_food_per_capita_table_1"
    },
)
def indicated_food_per_capita_table_1(x, final_subs=None):
    """
    Table relating industrial output to indicated food requirements 1 (IFPC1T#90.1).
    """
    return _hardcodedlookup_indicated_food_per_capita_table_1(x, final_subs)


_hardcodedlookup_indicated_food_per_capita_table_1 = HardcodedLookups(
    [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600],
    [230, 480, 690, 850, 970, 1070, 1150, 1210, 1250],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_indicated_food_per_capita_table_1",
)


@component.add(
    name="indicated food per capita 2",
    units="Veg equiv kg/(Person*year)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "industrial_output_per_capita": 1,
        "gdp_pc_unit": 1,
        "indicated_food_per_capita_table_2": 1,
    },
)
def indicated_food_per_capita_2():
    """
    Indicated foord per capita after policy time (IFPC1#90).
    """
    return indicated_food_per_capita_table_2(
        industrial_output_per_capita() / gdp_pc_unit()
    )


@component.add(
    name="indicated food per capita table 2",
    units="Veg equiv kg/(Person*year)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_indicated_food_per_capita_table_2"
    },
)
def indicated_food_per_capita_table_2(x, final_subs=None):
    """
    Table relating industrial output to indicated food requirements 2 (IFPC1T#90.1).
    """
    return _hardcodedlookup_indicated_food_per_capita_table_2(x, final_subs)


_hardcodedlookup_indicated_food_per_capita_table_2 = HardcodedLookups(
    [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600],
    [230, 480, 690, 850, 970, 1070, 1150, 1210, 1250],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_indicated_food_per_capita_table_2",
)


@component.add(
    name="processing loss",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def processing_loss():
    """
    PROCESSING LOSS (PL#87.2)
    """
    return 0.1


@component.add(
    name="total agricultural investment",
    units="$/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "industrial_output": 1,
        "fraction_of_industrial_output_allocated_to_agriculture": 1,
    },
)
def total_agricultural_investment():
    """
    TOTAL AGRICULTURAL INVESTMENT (TAI#92)
    """
    return (
        industrial_output()
        * fraction_of_industrial_output_allocated_to_agriculture()
    )


@component.add(
    name="average life agricultural inputs",
    units="year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def average_life_agricultural_inputs():
    """
    AVERAGE LIFETIME OF AGRICULTURAL INPUTS (ALAI#100)
    """
    return 2


@component.add(
    name="Agricultural Inputs",
    units="$/year",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_agricultural_inputs": 1},
    other_deps={
        "_smooth_agricultural_inputs": {
            "initial": {
                "current_agricultural_inputs": 1,
                "average_life_agricultural_inputs": 1,
            },
            "step": {
                "current_agricultural_inputs": 1,
                "average_life_agricultural_inputs": 1,
            },
        }
    },
)
def agricultural_inputs():
    """
    AGRICULTURAL INPUTS (AI#99)
    """
    return _smooth_agricultural_inputs()


_smooth_agricultural_inputs = Smooth(
    lambda: current_agricultural_inputs(),
    lambda: average_life_agricultural_inputs(),
    lambda: current_agricultural_inputs(),
    lambda: 1,
    "_smooth_agricultural_inputs",
)


@component.add(
    name="agricultural input per hectare",
    units="$/(year*hectare)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "agricultural_inputs": 1,
        "fraction_of_agricultural_inputs_for_land_maintenance": 1,
        "arable_land": 1,
    },
)
def agricultural_input_per_hectare():
    """
    AGRICULTURAL INPUTS PER HECTARE (AIPH#101)
    """
    return (
        agricultural_inputs()
        * (1 - fraction_of_agricultural_inputs_for_land_maintenance())
        / arable_land()
    )


@component.add(
    name="current agricultural inputs",
    units="$/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"_active_initial_current_agricultural_inputs": 1},
    other_deps={
        "_active_initial_current_agricultural_inputs": {
            "initial": {},
            "step": {
                "total_agricultural_investment": 1,
                "fraction_of_agricultural_inputs_allocated_to_land_development": 1,
            },
        }
    },
)
def current_agricultural_inputs():
    """
    CURRENT AGRICULTURAL INPUTS (CAI#98).
    """
    return active_initial(
        __data["time"].stage,
        lambda: total_agricultural_investment()
        * (
            1 - fraction_of_agricultural_inputs_allocated_to_land_development()
        ),
        initial_ds("Region", 5000000000.0),
    )


@component.add(
    name="Perceived Food Ratio",
    units="Dmnl",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_perceived_food_ratio": 1},
    other_deps={
        "_smooth_perceived_food_ratio": {
            "initial": {"food_ratio": 1, "food_shortage_perception_delay": 1},
            "step": {"food_ratio": 1, "food_shortage_perception_delay": 1},
        }
    },
)
def perceived_food_ratio():
    """
    PERCEIVED FOOD RATIO (PFR#128).
    """
    return _smooth_perceived_food_ratio()


_smooth_perceived_food_ratio = Smooth(
    lambda: food_ratio(),
    lambda: food_shortage_perception_delay(),
    lambda: food_ratio(),
    lambda: 1,
    "_smooth_perceived_food_ratio",
)


@component.add(
    name="food ratio",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"_active_initial_food_ratio": 1},
    other_deps={
        "_active_initial_food_ratio": {
            "initial": {},
            "step": {"food_per_capita": 1, "subsistence_food_per_capita": 1},
        }
    },
)
def food_ratio():
    """
    FOOD RATIO (FR#127)
    """
    return active_initial(
        __data["time"].stage,
        lambda: food_per_capita() / subsistence_food_per_capita(),
        1,
    )


@component.add(
    name="food shortage perception delay",
    units="year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def food_shortage_perception_delay():
    """
    FOOD SHORTAGE PERCEPTION DELAY (FSPD#128.2)
    """
    return 2


@component.add(
    name="fraction of agricultural inputs for land maintenance",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "perceived_food_ratio": 1,
        "fraction_of_agricultural_inputs_for_land_maintenance_table": 1,
    },
)
def fraction_of_agricultural_inputs_for_land_maintenance():
    """
    FRACTION OF INPUTS ALLOCATED TO LAND MAINTENANCE (FALM#126).
    """
    return fraction_of_agricultural_inputs_for_land_maintenance_table(
        perceived_food_ratio()
    )


@component.add(
    name="fraction of agricultural inputs for land maintenance table",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_fraction_of_agricultural_inputs_for_land_maintenance_table"
    },
)
def fraction_of_agricultural_inputs_for_land_maintenance_table(
    x, final_subs=None
):
    """
    Table relating the perceived food ratio to the fraction of input used for land maintenance (FALMT#126.1).
    """
    return _hardcodedlookup_fraction_of_agricultural_inputs_for_land_maintenance_table(
        x, final_subs
    )


_hardcodedlookup_fraction_of_agricultural_inputs_for_land_maintenance_table = HardcodedLookups(
    [0.0, 1.0, 2.0, 3.0, 4.0],
    [0.0, 0.04, 0.07, 0.09, 0.1],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_fraction_of_agricultural_inputs_for_land_maintenance_table",
)


@component.add(
    name="subsistence food per capita",
    units="Veg equiv kg/(Person*year)",
    comp_type="Constant",
    comp_subtype="Normal",
)
def subsistence_food_per_capita():
    """
    Subsistence food per capita (SFPC#127.1).
    """
    return 230
