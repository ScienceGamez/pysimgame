"""
Module industrial_output
Translated using PySD version 3.4.0
"""


@component.add(
    name="fraction of industrial output allocated to consumption",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def fraction_of_industrial_output_allocated_to_consumption():
    """
    Fraction of industrial output allocated to consumption (FIAOC#58)
    """
    return 0.43


@component.add(
    name="industrial capital output ratio",
    units="year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def industrial_capital_output_ratio():
    """
    INDUSTRIAL CAPITAL-OUTPUT RATIO (ICOR#51)
    """
    return 3


@component.add(
    name="average life of industrial capital",
    units="year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def average_life_of_industrial_capital():
    """
    AVERAGE LIFETIME OF INDUSTRIAL CAPITAL (ALIC#54).
    """
    return 14


@component.add(
    name="fraction of industrial output allocated to investment",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "fraction_of_industrial_output_allocated_to_agriculture": 1,
        "fraction_of_industrial_output_allocated_to_services": 1,
        "fraction_of_industrial_output_allocated_to_consumption": 1,
    },
)
def fraction_of_industrial_output_allocated_to_investment():
    """
    Fraction of industrial output allocated to industry (FIAOI#56).
    """
    return (
        1
        - fraction_of_industrial_output_allocated_to_agriculture()
        - fraction_of_industrial_output_allocated_to_services()
        - fraction_of_industrial_output_allocated_to_consumption()
    )


@component.add(
    name="industrial capital depreciation",
    units="$/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"industrial_capital": 1, "average_life_of_industrial_capital": 1},
)
def industrial_capital_depreciation():
    """
    Industrial capital depreciation rate (ICDR#53).
    """
    return industrial_capital() / average_life_of_industrial_capital()


@component.add(
    name="industrial capital investment",
    units="$/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "industrial_output": 1,
        "fraction_of_industrial_output_allocated_to_investment": 1,
    },
)
def industrial_capital_investment():
    """
    Industrial capital investment rate (ICIR#55).
    """
    return industrial_output() * fraction_of_industrial_output_allocated_to_investment()


@component.add(
    name="industrial output per capita",
    units="$/(Person*year)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"industrial_output": 1, "population": 1},
)
def industrial_output_per_capita():
    """
    INDUSTRIAL OUTPUT PER CAPITA (IOPC#49)
    """
    return industrial_output() / population()


@component.add(
    name="industrial output per capita desired",
    units="$/(Person*year)",
    comp_type="Constant",
    comp_subtype="Normal",
)
def industrial_output_per_capita_desired():
    """
    Industrial output per capita desired (IOPCD#59.2).
    """
    return 400


@component.add(
    name="Industrial Capital",
    units="$",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_industrial_capital": 1},
    other_deps={
        "_integ_industrial_capital": {
            "initial": {"initial_industrial_capital": 1},
            "step": {
                "industrial_capital_investment": 1,
                "industrial_capital_depreciation": 1,
            },
        }
    },
)
def industrial_capital():
    """
    INDUSTRIAL CAPITAL (IC#52).
    """
    return _integ_industrial_capital()


_integ_industrial_capital = Integ(
    lambda: industrial_capital_investment() - industrial_capital_depreciation(),
    lambda: initial_industrial_capital(),
    "_integ_industrial_capital",
)


@component.add(
    name="initial industrial capital",
    units="$",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_industrial_capital():
    """
    INDUSTRIAL CAPITAL INITIAL (ICI#52.1).
    """
    return 210000000000.0


@component.add(
    name="industrial output",
    units="$/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "industrial_capital": 1,
        "fraction_of_industrial_capital_allocated_to_obtaining_resources": 1,
        "capacity_utilization_fraction": 1,
        "industrial_capital_output_ratio": 1,
    },
)
def industrial_output():
    """
    Industrial output (IO#50)
    """
    return (
        (
            industrial_capital()
            * (1 - fraction_of_industrial_capital_allocated_to_obtaining_resources())
        )
        * capacity_utilization_fraction()
        / industrial_capital_output_ratio()
    )


@component.add(
    name="fraction of industrial output allocated to consumption variable",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "industrial_output_per_capita": 1,
        "industrial_output_per_capita_desired": 1,
        "fraction_of_industrial_output_allocated_to_consumption_variable_table": 1,
    },
)
def fraction_of_industrial_output_allocated_to_consumption_variable():
    """
    Fraction industrial output allocated to consumption variable (FIAOCV#59)
    """
    return fraction_of_industrial_output_allocated_to_consumption_variable_table(
        industrial_output_per_capita() / industrial_output_per_capita_desired()
    )


@component.add(
    name="fraction of industrial output allocated to consumption variable table",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_fraction_of_industrial_output_allocated_to_consumption_variable_table"
    },
)
def fraction_of_industrial_output_allocated_to_consumption_variable_table(
    x, final_subs=None
):
    """
    Fraction of industrial output allocated to consumption variable TABLE (FIAOCVT#59.1)
    """
    return _hardcodedlookup_fraction_of_industrial_output_allocated_to_consumption_variable_table(
        x, final_subs
    )


_hardcodedlookup_fraction_of_industrial_output_allocated_to_consumption_variable_table = HardcodedLookups(
    [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
    [0.3, 0.32, 0.34, 0.36, 0.38, 0.43, 0.73, 0.77, 0.81, 0.82, 0.83],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_fraction_of_industrial_output_allocated_to_consumption_variable_table",
)


@component.add(
    name="industrial capital output ratio 2",
    units="year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "industrial_capital_output_ratio_multiplier_from_resource_conservation_technology": 1,
        "industrial_capital_output_ratio_multiplier_from_land_yield_technology": 1,
        "industrial_capital_output_ratio_multiplier_from_pollution_technology": 1,
    },
)
def industrial_capital_output_ratio_2():
    """
    Industrial capital output ratio after the policy year (ICOR2#51.2)
    """
    return (
        industrial_capital_output_ratio_multiplier_from_resource_conservation_technology()
        * industrial_capital_output_ratio_multiplier_from_land_yield_technology()
        * industrial_capital_output_ratio_multiplier_from_pollution_technology()
    )
