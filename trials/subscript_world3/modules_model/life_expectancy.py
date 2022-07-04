"""
Module life_expectancy
Translated using PySD version 3.4.0
"""


@component.add(
    name="crowding multiplier from industry",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "industrial_output_per_capita": 1,
        "gdp_pc_unit": 1,
        "crowding_multiplier_from_industry_table": 1,
    },
)
def crowding_multiplier_from_industry():
    """
    CROWDING MULTIPLIER FROM INDUSTRIALIZATION (CMI#27).
    """
    return crowding_multiplier_from_industry_table(
        industrial_output_per_capita() / gdp_pc_unit()
    )


@component.add(
    name="crowding multiplier from industry table",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_crowding_multiplier_from_industry_table"
    },
)
def crowding_multiplier_from_industry_table(x, final_subs=None):
    """
    Table relating industrial output to crowding (CMIT#27.1).
    """
    return _hardcodedlookup_crowding_multiplier_from_industry_table(x, final_subs)


_hardcodedlookup_crowding_multiplier_from_industry_table = HardcodedLookups(
    [0.0, 200.0, 400.0, 600.0, 800.0, 1000.0, 1200.0, 1400.0, 1600.0],
    [0.5, 0.05, -0.1, -0.08, -0.02, 0.05, 0.1, 0.15, 0.2],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_crowding_multiplier_from_industry_table",
)


@component.add(
    name="effective health services per capita",
    units="$/(Person*year)",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_effective_health_services_per_capita": 1},
    other_deps={
        "_smooth_effective_health_services_per_capita": {
            "initial": {
                "health_services_per_capita": 1,
                "health_services_impact_delay": 1,
            },
            "step": {
                "health_services_per_capita": 1,
                "health_services_impact_delay": 1,
            },
        }
    },
)
def effective_health_services_per_capita():
    """
    Effective health services per capita - delayed from allocation (EHSPC#22)
    """
    return _smooth_effective_health_services_per_capita()


_smooth_effective_health_services_per_capita = Smooth(
    lambda: health_services_per_capita(),
    lambda: health_services_impact_delay(),
    lambda: health_services_per_capita(),
    lambda: 1,
    "_smooth_effective_health_services_per_capita",
)


@component.add(
    name="fraction of population urban",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "population": 1,
        "unit_population": 1,
        "fraction_of_population_urban_table": 1,
    },
)
def fraction_of_population_urban():
    """
    FRACTION OF POPULATION URBAN (FPU#26).
    """
    return fraction_of_population_urban_table(population() / unit_population())


@component.add(
    name="fraction of population urban table",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_fraction_of_population_urban_table"},
)
def fraction_of_population_urban_table(x, final_subs=None):
    """
    Table relating population to the fraction of population that is urban (FPUT#26.1).
    """
    return _hardcodedlookup_fraction_of_population_urban_table(x, final_subs)


_hardcodedlookup_fraction_of_population_urban_table = HardcodedLookups(
    [0.0e00, 2.0e09, 4.0e09, 6.0e09, 8.0e09, 1.0e10, 1.2e10, 1.4e10, 1.6e10],
    [0.0, 0.2, 0.4, 0.5, 0.58, 0.65, 0.72, 0.78, 0.8],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_fraction_of_population_urban_table",
)


@component.add(
    name="health services per capita",
    units="$/(Person*year)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "service_output_per_capita": 1,
        "gdp_pc_unit": 1,
        "health_services_per_capita_table": 1,
    },
)
def health_services_per_capita():
    """
    Health services allocation per capita (HSAPC#21).
    """
    return health_services_per_capita_table(service_output_per_capita() / gdp_pc_unit())


@component.add(
    name="health services per capita table",
    units="$/(Person*year)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_health_services_per_capita_table"},
)
def health_services_per_capita_table(x, final_subs=None):
    """
    The table relating service output to health services (HSAPCT#21.1).
    """
    return _hardcodedlookup_health_services_per_capita_table(x, final_subs)


_hardcodedlookup_health_services_per_capita_table = HardcodedLookups(
    [0, 250, 500, 750, 1000, 1250, 1500, 1750, 2000],
    [0, 20, 50, 95, 140, 175, 200, 220, 230],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_health_services_per_capita_table",
)


@component.add(
    name="health services impact delay",
    units="year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def health_services_impact_delay():
    """
    The delay between allocating health services, and realizing the benefit (HSID#22.1).
    """
    return 20


@component.add(
    name="life expectancy normal",
    units="year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def life_expectancy_normal():
    """
    The normal life expectancy with subsistance food, no medical care and no industrialization (LEN#19.1)
    """
    return 28


@component.add(
    name="life expectancy",
    units="year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "life_expectancy_normal": 1,
        "lifetime_multiplier_from_food": 1,
        "lifetime_multiplier_from_health_services": 1,
        "lifetime_multiplier_from_persistent_pollution": 1,
        "lifetime_multiplier_from_crowding": 1,
    },
)
def life_expectancy():
    """
    The average life expectancy (LE#19).
    """
    return (
        life_expectancy_normal()
        * lifetime_multiplier_from_food()
        * lifetime_multiplier_from_health_services()
        * lifetime_multiplier_from_persistent_pollution()
        * lifetime_multiplier_from_crowding()
    )


@component.add(
    name="lifetime multiplier from crowding",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "crowding_multiplier_from_industry": 1,
        "fraction_of_population_urban": 1,
    },
)
def lifetime_multiplier_from_crowding():
    """
    LIFETIME MULTIPLIER FROM CROWDING (LMC#28)
    """
    return 1 - crowding_multiplier_from_industry() * fraction_of_population_urban()


@component.add(
    name="lifetime multiplier from food",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "food_per_capita": 1,
        "subsistence_food_per_capita": 1,
        "lifetime_multiplier_from_food_table": 1,
    },
)
def lifetime_multiplier_from_food():
    """
    The life expectancy multiplier from food (LMF#20)
    """
    return lifetime_multiplier_from_food_table(
        food_per_capita() / subsistence_food_per_capita()
    )


@component.add(
    name="lifetime multiplier from food table",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_lifetime_multiplier_from_food_table"},
)
def lifetime_multiplier_from_food_table(x, final_subs=None):
    """
    The table ralating relative food to the life expectancy multiplier for food (LMFT#20.1)
    """
    return _hardcodedlookup_lifetime_multiplier_from_food_table(x, final_subs)


_hardcodedlookup_lifetime_multiplier_from_food_table = HardcodedLookups(
    [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
    [0.0, 1.0, 1.43, 1.5, 1.5, 1.5],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_lifetime_multiplier_from_food_table",
)


@component.add(
    name="lifetime multiplier from health services",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "lifetime_multiplier_from_health_services_2": 1,
        "lifetime_multiplier_from_health_services_1": 1,
    },
)
def lifetime_multiplier_from_health_services():
    """
    The life expectancy multiplier from health services (LMHS#23).
    """
    return if_then_else(
        time() > 1940,
        lambda: lifetime_multiplier_from_health_services_2(),
        lambda: lifetime_multiplier_from_health_services_1(),
    )


@component.add(
    name="lifetime multiplier from health services 1",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "effective_health_services_per_capita": 1,
        "gdp_pc_unit": 1,
        "lifetime_multiplier_from_health_services_1_table": 1,
    },
)
def lifetime_multiplier_from_health_services_1():
    """
    The life expectancy multiplier from health services before 1940 (LMHS1#24).
    """
    return lifetime_multiplier_from_health_services_1_table(
        effective_health_services_per_capita() / gdp_pc_unit()
    )


@component.add(
    name="lifetime multiplier from health services 1 table",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_lifetime_multiplier_from_health_services_1_table"
    },
)
def lifetime_multiplier_from_health_services_1_table(x, final_subs=None):
    """
    Table relating effective health care to life expectancy (LMHS1T#24.1).
    """
    return _hardcodedlookup_lifetime_multiplier_from_health_services_1_table(
        x, final_subs
    )


_hardcodedlookup_lifetime_multiplier_from_health_services_1_table = HardcodedLookups(
    [0.0, 20.0, 40.0, 60.0, 80.0, 100.0],
    [1.0, 1.1, 1.4, 1.6, 1.7, 1.8],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_lifetime_multiplier_from_health_services_1_table",
)


@component.add(
    name="lifetime multiplier from health services 2",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "effective_health_services_per_capita": 1,
        "gdp_pc_unit": 1,
        "lifetime_multiplier_from_health_services_2_table": 1,
    },
)
def lifetime_multiplier_from_health_services_2():
    """
    The life expectancy multipier from health services value after 1940 (LMHS2#25).
    """
    return lifetime_multiplier_from_health_services_2_table(
        effective_health_services_per_capita() / gdp_pc_unit()
    )


@component.add(
    name="lifetime multiplier from health services 2 table",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_lifetime_multiplier_from_health_services_2_table"
    },
)
def lifetime_multiplier_from_health_services_2_table(x, final_subs=None):
    """
    Table relating effective health care to life expectancy (LMHS2T#25.1)
    """
    return _hardcodedlookup_lifetime_multiplier_from_health_services_2_table(
        x, final_subs
    )


_hardcodedlookup_lifetime_multiplier_from_health_services_2_table = HardcodedLookups(
    [0.0, 20.0, 40.0, 60.0, 80.0, 100.0],
    [1.0, 1.5, 1.9, 2.0, 2.0, 2.0],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_lifetime_multiplier_from_health_services_2_table",
)


@component.add(
    name="lifetime multiplier from persistent pollution",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "persistent_pollution_index": 1,
        "lifetime_multiplier_from_persistent_pollution_table": 1,
    },
)
def lifetime_multiplier_from_persistent_pollution():
    """
    LIFETIME MULTIPLIER FROM PERSISTENT POLLUTION (LMP#29)
    """
    return lifetime_multiplier_from_persistent_pollution_table(
        persistent_pollution_index()
    )


@component.add(
    name="lifetime multiplier from persistent pollution table",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_lifetime_multiplier_from_persistent_pollution_table"
    },
)
def lifetime_multiplier_from_persistent_pollution_table(x, final_subs=None):
    """
    Table relating persistent pollution to life expectancy (LMPT#29.1)
    """
    return _hardcodedlookup_lifetime_multiplier_from_persistent_pollution_table(
        x, final_subs
    )


_hardcodedlookup_lifetime_multiplier_from_persistent_pollution_table = HardcodedLookups(
    [0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0],
    [1.0, 0.99, 0.97, 0.95, 0.9, 0.85, 0.75, 0.65, 0.55, 0.4, 0.2],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_lifetime_multiplier_from_persistent_pollution_table",
)
