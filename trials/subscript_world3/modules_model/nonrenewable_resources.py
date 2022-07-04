"""
Module nonrenewable_resources
Translated using PySD version 3.4.0
"""


@component.add(
    name="industrial capital output ratio multiplier from resource conservation technology",
    units="year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "resource_use_factor": 1,
        "industrial_capital_output_ratio_multiplier_from_resource_table": 1,
    },
)
def industrial_capital_output_ratio_multiplier_from_resource_conservation_technology():
    """
    Technology driven industrial capital output ratio (ICOR2T#--)
    """
    return industrial_capital_output_ratio_multiplier_from_resource_table(
        resource_use_factor()
    )


@component.add(
    name="industrial capital output ratio multiplier from resource table",
    units="year",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_industrial_capital_output_ratio_multiplier_from_resource_table"
    },
)
def industrial_capital_output_ratio_multiplier_from_resource_table(x, final_subs=None):
    """
    CAPITAL OUTPUT FROM RESOURCES technology multiplier TABLE (ICOR2TT#--)
    """
    return (
        _hardcodedlookup_industrial_capital_output_ratio_multiplier_from_resource_table(
            x, final_subs
        )
    )


_hardcodedlookup_industrial_capital_output_ratio_multiplier_from_resource_table = HardcodedLookups(
    [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    [3.75, 3.6, 3.47, 3.36, 3.25, 3.16, 3.1, 3.06, 3.02, 3.01, 3.0],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_industrial_capital_output_ratio_multiplier_from_resource_table",
)


@component.add(
    name="resource technology change rate",
    units="1/year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def resource_technology_change_rate():
    """
    RESOURCE TECHNOLOGY IMPROVEMENT RATE (NRATE-##).
    """
    return 0


@component.add(
    name="fraction of industrial capital allocated to obtaining resources",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"fraction_of_capital_allocated_to_obtaining_resources_1": 1},
)
def fraction_of_industrial_capital_allocated_to_obtaining_resources():
    """
    FRACTION OF CAPITAL ALLOCATED TO OBTAINING RESOURCES (FCAOR#134).
    """
    return fraction_of_capital_allocated_to_obtaining_resources_1()


@component.add(
    name="resource use factor",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def resource_use_factor():
    """
    NONRENEWABLE RESOURCE USAGE FACTOR (NRUF#131).
    """
    return 1


@component.add(
    name="desired resource use rate",
    units="Resource units/year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def desired_resource_use_rate():
    """
    Desired non-renewable resource usage rate (DNRUR#--)
    """
    return 4800000000.0


@component.add(
    name="fraction of resources remaining",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"nonrenewable_resources": 1, "initial_nonrenewable_resources": 1},
)
def fraction_of_resources_remaining():
    """
    Non-renewable resource fraction remaining (NRFR#133).
    """
    return nonrenewable_resources() / initial_nonrenewable_resources()


@component.add(
    name="resource usage rate",
    units="Resource units/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "population": 1,
        "per_capita_resource_use_multiplier": 1,
        "resource_use_factor": 1,
    },
)
def resource_usage_rate():
    """
    Non-renewable resource use rate (NRUR#130).
    """
    return (population() * per_capita_resource_use_multiplier()) * resource_use_factor()


@component.add(
    name="initial nonrenewable resources",
    units="Resource units",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_nonrenewable_resources():
    """
    NONRENEWABLE RESOURCE INITIAL (NR#129.2).
    """
    return 1000000000000.0


@component.add(
    name="Nonrenewable Resources",
    units="Resource units",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_nonrenewable_resources": 1},
    other_deps={
        "_integ_nonrenewable_resources": {
            "initial": {"initial_nonrenewable_resources": 1},
            "step": {"resource_usage_rate": 1},
        }
    },
)
def nonrenewable_resources():
    """
    Non-renewable resource (NR#129)
    """
    return _integ_nonrenewable_resources()


_integ_nonrenewable_resources = Integ(
    lambda: -resource_usage_rate(),
    lambda: initial_nonrenewable_resources(),
    "_integ_nonrenewable_resources",
)


@component.add(
    name="fraction of capital allocated to obtaining resources 1",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "fraction_of_resources_remaining": 1,
        "fraction_of_capital_allocated_to_obtaining_resources_1_table": 1,
    },
)
def fraction_of_capital_allocated_to_obtaining_resources_1():
    """
    Fraction of capital allocated to obtaining resources before switch time (FCAOR1#135).
    """
    return fraction_of_capital_allocated_to_obtaining_resources_1_table(
        fraction_of_resources_remaining()
    )


@component.add(
    name="fraction of capital allocated to obtaining resources 1 table",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_fraction_of_capital_allocated_to_obtaining_resources_1_table"
    },
)
def fraction_of_capital_allocated_to_obtaining_resources_1_table(x, final_subs=None):
    """
    Table relating the fraction of resources remaining to capital allocated to resource extraction (FCAOR1T#135.1).
    """
    return (
        _hardcodedlookup_fraction_of_capital_allocated_to_obtaining_resources_1_table(
            x, final_subs
        )
    )


_hardcodedlookup_fraction_of_capital_allocated_to_obtaining_resources_1_table = (
    HardcodedLookups(
        [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        [1.0, 0.9, 0.7, 0.5, 0.2, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05],
        {},
        "interpolate",
        {},
        "_hardcodedlookup_fraction_of_capital_allocated_to_obtaining_resources_1_table",
    )
)


@component.add(
    name="fraction of capital allocated to obtaining resources 2",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "fraction_of_resources_remaining": 1,
        "fraction_of_capital_allocated_to_obtaining_resources_2_table": 1,
    },
)
def fraction_of_capital_allocated_to_obtaining_resources_2():
    """
    Fraction of capital allocated to obtaining resources after switch time (FCAOR2#136).
    """
    return fraction_of_capital_allocated_to_obtaining_resources_2_table(
        fraction_of_resources_remaining()
    )


@component.add(
    name="fraction of capital allocated to obtaining resources 2 table",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_fraction_of_capital_allocated_to_obtaining_resources_2_table"
    },
)
def fraction_of_capital_allocated_to_obtaining_resources_2_table(x, final_subs=None):
    """
    Table relating the fraction of resources remaining to capital allocated to resource extraction (FCAOR2T#136.1).
    """
    return (
        _hardcodedlookup_fraction_of_capital_allocated_to_obtaining_resources_2_table(
            x, final_subs
        )
    )


_hardcodedlookup_fraction_of_capital_allocated_to_obtaining_resources_2_table = (
    HardcodedLookups(
        [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        [1.0, 0.2, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05],
        {},
        "interpolate",
        {},
        "_hardcodedlookup_fraction_of_capital_allocated_to_obtaining_resources_2_table",
    )
)


@component.add(
    name="resource use fact 2",
    units="Dmnl",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_resource_use_fact_2": 1},
    other_deps={
        "_smooth_resource_use_fact_2": {
            "initial": {
                "resource_conservation_technology": 1,
                "technology_development_delay": 1,
            },
            "step": {
                "resource_conservation_technology": 1,
                "technology_development_delay": 1,
            },
        }
    },
)
def resource_use_fact_2():
    """
    The nonrenewable resource usage factor after the policy year (NRUF2#131.2).
    """
    return _smooth_resource_use_fact_2()


_smooth_resource_use_fact_2 = Smooth(
    lambda: resource_conservation_technology(),
    lambda: technology_development_delay(),
    lambda: resource_conservation_technology(),
    lambda: 3,
    "_smooth_resource_use_fact_2",
)


@component.add(
    name="resource technology change rate multiplier",
    units="Dmnl/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "resource_usage_rate": 1,
        "desired_resource_use_rate": 1,
        "resource_technology_change_mult_table": 1,
    },
)
def resource_technology_change_rate_multiplier():
    """
    Resource technology change multiplier (NRCM#--)
    """
    return resource_technology_change_mult_table(
        1 - resource_usage_rate() / desired_resource_use_rate()
    )


@component.add(
    name="resource technology change mult table",
    units="Dmnl/year",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_resource_technology_change_mult_table"},
)
def resource_technology_change_mult_table(x, final_subs=None):
    """
    Table relating resource use to technological change. (NRCMT#--)
    """
    return _hardcodedlookup_resource_technology_change_mult_table(x, final_subs)


_hardcodedlookup_resource_technology_change_mult_table = HardcodedLookups(
    [-1, 0],
    [0, 0],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_resource_technology_change_mult_table",
)


@component.add(
    name="per capita resource use multiplier",
    units="Resource unit/(Person*year)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "industrial_output_per_capita": 1,
        "gdp_pc_unit": 1,
        "per_capita_resource_use_mult_table": 1,
    },
)
def per_capita_resource_use_multiplier():
    """
    Per capita resource usage multiplier (PCRUM#132).
    """
    return per_capita_resource_use_mult_table(
        industrial_output_per_capita() / gdp_pc_unit()
    )


@component.add(
    name="per capita resource use mult table",
    units="Resource units/(Person*year)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_per_capita_resource_use_mult_table"},
)
def per_capita_resource_use_mult_table(x, final_subs=None):
    """
    Table relating industrial output to resource usage per capita (PCRUMT#132.1).
    """
    return _hardcodedlookup_per_capita_resource_use_mult_table(x, final_subs)


_hardcodedlookup_per_capita_resource_use_mult_table = HardcodedLookups(
    [0.0, 200.0, 400.0, 600.0, 800.0, 1000.0, 1200.0, 1400.0, 1600.0],
    [0.0, 0.85, 2.6, 3.4, 3.8, 4.1, 4.4, 4.7, 5.0],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_per_capita_resource_use_mult_table",
)


@component.add(
    name="Resource Conservation Technology",
    units="Dmnl",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_resource_conservation_technology": 1},
    other_deps={
        "_integ_resource_conservation_technology": {
            "initial": {},
            "step": {"resource_technology_change_rate": 1},
        }
    },
)
def resource_conservation_technology():
    """
    Non-renewable resource technology (NRTD#--)
    """
    return _integ_resource_conservation_technology()


_integ_resource_conservation_technology = Integ(
    lambda: resource_technology_change_rate(),
    lambda: 1,
    "_integ_resource_conservation_technology",
)
