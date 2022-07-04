"""
Module demographics
Translated using PySD version 3.4.0
"""


@component.add(
    name="labor force",
    units="Person",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "population_15_to_44": 1,
        "population_45_to_64": 1,
        "labor_force_participation_fraction": 1,
    },
)
def labor_force():
    """
    LABOR FORCE (LF#80).
    """
    return (
        population_15_to_44() + population_45_to_64()
    ) * labor_force_participation_fraction()


@component.add(
    name="labor force participation fraction",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def labor_force_participation_fraction():
    """
    LABOR FORCE PARTICIPATION FRACTION (LFPF#80.1)
    """
    return 0.75


@component.add(
    name="deaths 0 to 14",
    units="Person/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"population_0_to_14": 1, "mortality_0_to_14": 1},
)
def deaths_0_to_14():
    """
    The number of deaths per year among people 0 to 14 years of age (D1#3).
    """
    return population_0_to_14() * mortality_0_to_14()


@component.add(
    name="deaths 15 to 44",
    units="Person/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"population_15_to_44": 1, "mortality_15_to_44": 1},
)
def deaths_15_to_44():
    """
    The number of deaths per year among people 15 to 44 years of age (D2#7).
    """
    return population_15_to_44() * mortality_15_to_44()


@component.add(
    name="deaths 45 to 64",
    units="Person/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"population_45_to_64": 1, "mortality_45_to_64": 1},
)
def deaths_45_to_64():
    """
    The number of deaths per year among people 55 to 64 years of age (D3#11).
    """
    return population_45_to_64() * mortality_45_to_64()


@component.add(
    name="deaths 65 plus",
    units="Person/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"population_65_plus": 1, "mortality_65_plus": 1},
)
def deaths_65_plus():
    """
    The number of deaths per year among people 65 and older (D4#15).
    """
    return population_65_plus() * mortality_65_plus()


@component.add(
    name="maturation 14 to 15",
    units="Person/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"population_0_to_14": 1, "mortality_0_to_14": 1},
)
def maturation_14_to_15():
    """
    The fractional rate at which people aged 0-14 mature into the next age cohort (MAT1#5).
    """
    return population_0_to_14() * (1 - mortality_0_to_14()) / 15


@component.add(
    name="maturation 44 to 45",
    units="Person/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"population_15_to_44": 1, "mortality_15_to_44": 1},
)
def maturation_44_to_45():
    """
    The fractional rate at which people aged 15-44 mature into the next age cohort (MAT2#9).
    """
    return population_15_to_44() * (1 - mortality_15_to_44()) / 30


@component.add(
    name="maturation 64 to 65",
    units="Person/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"population_45_to_64": 1, "mortality_45_to_64": 1},
)
def maturation_64_to_65():
    """
    The fractional rate at which people aged 45-64 mature into the next age cohort (MAT3#13).
    """
    return population_45_to_64() * (1 - mortality_45_to_64()) / 20


@component.add(
    name="mortality 45 to 64",
    units="1/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "life_expectancy": 1,
        "one_year": 1,
        "mortality_45_to_64_table": 1,
    },
)
def mortality_45_to_64():
    """
    The fractional mortality rate for people aged 45-64 (M3#12).
    """
    return mortality_45_to_64_table(life_expectancy() / one_year())


@component.add(
    name="mortality 45 to 64 table",
    units="1/year",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_mortality_45_to_64_table"},
)
def mortality_45_to_64_table(x, final_subs=None):
    """
    The table relating average life to mortality in the 45 to 64 age group (M2T#12.1).
    """
    return _hardcodedlookup_mortality_45_to_64_table(x, final_subs)


_hardcodedlookup_mortality_45_to_64_table = HardcodedLookups(
    [20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0],
    [0.0562, 0.0373, 0.0252, 0.0171, 0.0118, 0.0083, 0.006],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_mortality_45_to_64_table",
)


@component.add(
    name="mortality 65 plus",
    units="1/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "life_expectancy": 1,
        "one_year": 1,
        "mortality_65_plus_table": 1,
    },
)
def mortality_65_plus():
    """
    The fractional mortality rate for people over 65 (M4#16).
    """
    return mortality_65_plus_table(life_expectancy() / one_year())


@component.add(
    name="mortality 65 plus table",
    units="1/year",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_mortality_65_plus_table"},
)
def mortality_65_plus_table(x, final_subs=None):
    """
    The table relating average life expectancy to mortality among people over 65 (M4T#16.1)
    """
    return _hardcodedlookup_mortality_65_plus_table(x, final_subs)


_hardcodedlookup_mortality_65_plus_table = HardcodedLookups(
    [20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0],
    [0.13, 0.11, 0.09, 0.07, 0.06, 0.05, 0.04],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_mortality_65_plus_table",
)


@component.add(
    name="mortality 0 to 14",
    units="1/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "life_expectancy": 1,
        "one_year": 1,
        "mortality_0_to_14_table": 1,
    },
)
def mortality_0_to_14():
    """
    The fractional mortality rate for people aged 0-14 (M1#4).
    """
    return mortality_0_to_14_table(life_expectancy() / one_year())


@component.add(
    name="mortality 0 to 14 table",
    units="1/year",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_mortality_0_to_14_table"},
)
def mortality_0_to_14_table(x, final_subs=None):
    """
    The table relating average life to mortality in the 0 to 14 age group (M1T#4.1).
    """
    return _hardcodedlookup_mortality_0_to_14_table(x, final_subs)


_hardcodedlookup_mortality_0_to_14_table = HardcodedLookups(
    [20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0],
    [0.0567, 0.0366, 0.0243, 0.0155, 0.0082, 0.0023, 0.001],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_mortality_0_to_14_table",
)


@component.add(
    name="mortality 15 to 44",
    units="1/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "life_expectancy": 1,
        "one_year": 1,
        "mortality_15_to_44_table": 1,
    },
)
def mortality_15_to_44():
    """
    The fractional mortality rate for people aged 15-44 (M2#8).
    """
    return mortality_15_to_44_table(life_expectancy() / one_year())


@component.add(
    name="mortality 15 to 44 table",
    units="1/year",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_mortality_15_to_44_table"},
)
def mortality_15_to_44_table(x, final_subs=None):
    """
    The table relating average life to mortality in the 15 to 44 age group (M2T#8.1).
    """
    return _hardcodedlookup_mortality_15_to_44_table(x, final_subs)


_hardcodedlookup_mortality_15_to_44_table = HardcodedLookups(
    [20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0],
    [0.0266, 0.0171, 0.011, 0.0065, 0.004, 0.0016, 0.0008],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_mortality_15_to_44_table",
)


@component.add(
    name="Population 0 To 14",
    units="Person",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_population_0_to_14": 1},
    other_deps={
        "_integ_population_0_to_14": {
            "initial": {"initial_population_0_to_14": 1},
            "step": {
                "births": 1,
                "deaths_0_to_14": 1,
                "maturation_14_to_15": 1,
            },
        }
    },
)
def population_0_to_14():
    """
    World population, AGES 0-14 (P1#2)
    """
    return _integ_population_0_to_14()


_integ_population_0_to_14 = Integ(
    lambda: births() - deaths_0_to_14() - maturation_14_to_15(),
    lambda: initial_population_0_to_14(),
    "_integ_population_0_to_14",
)


@component.add(
    name="initial population 0 to 14",
    units="Person",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_population_0_to_14():
    """
    The initial number of people aged 0 to 14 (P1I#2.2).
    """
    # return initial_ds("Region")
    return initial_ds("Region")


@component.add(
    name="Population 15 To 44",
    units="Person",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_population_15_to_44": 1},
    other_deps={
        "_integ_population_15_to_44": {
            "initial": {"initial_population_15_to_44": 1},
            "step": {
                "maturation_14_to_15": 1,
                "deaths_15_to_44": 1,
                "maturation_44_to_45": 1,
            },
        }
    },
)
def population_15_to_44():
    """
    World population, AGES 15-44 (P2#6)
    """
    return _integ_population_15_to_44()


_integ_population_15_to_44 = Integ(
    lambda: maturation_14_to_15() - deaths_15_to_44() - maturation_44_to_45(),
    lambda: initial_population_15_to_44(),
    "_integ_population_15_to_44",
)


@component.add(
    name="initial population 15 to 44",
    units="Person",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_population_15_to_44():
    """
    The initial number of people aged 15 to 44 (P2I#6.2).
    """
    return initial_ds("Region")


@component.add(
    name="Population 45 To 64",
    units="Person",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_population_45_to_64": 1},
    other_deps={
        "_integ_population_45_to_64": {
            "initial": {"initial_population_54_to_64": 1},
            "step": {
                "maturation_44_to_45": 1,
                "deaths_45_to_64": 1,
                "maturation_64_to_65": 1,
            },
        }
    },
)
def population_45_to_64():
    """
    The world population aged 0 to 14 (P3#10).
    """
    return _integ_population_45_to_64()


_integ_population_45_to_64 = Integ(
    lambda: maturation_44_to_45() - deaths_45_to_64() - maturation_64_to_65(),
    lambda: initial_population_54_to_64(),
    "_integ_population_45_to_64",
)


@component.add(
    name="initial population 54 to 64",
    units="Person",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_population_54_to_64():
    """
    The initial number of people aged 45 to 64 (P3I#10.2).
    """
    return initial_ds("Region")


@component.add(
    name="Population 65 Plus",
    units="Person",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_population_65_plus": 1},
    other_deps={
        "_integ_population_65_plus": {
            "initial": {"initial_population_65_plus": 1},
            "step": {"maturation_64_to_65": 1, "deaths_65_plus": 1},
        }
    },
)
def population_65_plus():
    """
    The world population aged 65 and over (P4#14).
    """
    return _integ_population_65_plus()


_integ_population_65_plus = Integ(
    lambda: maturation_64_to_65() - deaths_65_plus(),
    lambda: initial_population_65_plus(),
    "_integ_population_65_plus",
)


@component.add(
    name="initial population 65 plus",
    units="Person",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_population_65_plus():
    """
    The initial number of people aged 65 and over (P4I#14.2)
    """
    return initial_ds("Region")


@component.add(
    name="population",
    units="Person",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "population_0_to_14": 1,
        "population_15_to_44": 1,
        "population_45_to_64": 1,
        "population_65_plus": 1,
    },
)
def population():
    """
    Total world population in all age groups (POP#1).
    """
    return (
        population_0_to_14()
        + population_15_to_44()
        + population_45_to_64()
        + population_65_plus()
    )


@component.add(
    name="births",
    units="Person/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "total_fertility": 1,
        "population_15_to_44": 1,
        "reproductive_lifetime": 1,
    },
)
def births():
    """
    The total number of births in the world (B#30).
    """
    return (
        total_fertility()
        * population_15_to_44()
        * 0.5
        / reproductive_lifetime()
    )


@component.add(
    name="reproductive lifetime",
    units="year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def reproductive_lifetime():
    """
    The number of years people can reproduce (RLT#30.1)
    """
    return 30


@component.add(
    name="deaths",
    units="Person/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "deaths_0_to_14": 1,
        "deaths_15_to_44": 1,
        "deaths_45_to_64": 1,
        "deaths_65_plus": 1,
    },
)
def deaths():
    """
    The total number of deaths per year for all age groups (D#17).
    """
    return (
        deaths_0_to_14()
        + deaths_15_to_44()
        + deaths_45_to_64()
        + deaths_65_plus()
    )
