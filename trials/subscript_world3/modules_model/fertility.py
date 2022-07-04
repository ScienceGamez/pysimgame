"""
Module fertility
Translated using PySD version 3.4.0
"""


@component.add(
    name="fertility control effectiveness",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "fertility_control_facilities_per_capita": 1,
        "gdp_pc_unit": 1,
        "fertility_control_effectiveness_table": 1,
    },
)
def fertility_control_effectiveness():
    """
    Fertility control effectiveness (FCE#45).
    """
    return fertility_control_effectiveness_table(
        fertility_control_facilities_per_capita() / gdp_pc_unit()
    )


@component.add(
    name="desired completed family size",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "desired_completed_family_size_normal": 1,
        "family_response_to_social_norm": 1,
        "social_family_size_normal": 1,
    },
)
def desired_completed_family_size():
    """
    Desired completed family size (DCFS#38)
    """
    return (
        desired_completed_family_size_normal()
        * family_response_to_social_norm()
        * social_family_size_normal()
    )


@component.add(
    name="average industrial output per capita",
    units="$/(Person*year)",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_average_industrial_output_per_capita": 1},
    other_deps={
        "_smooth_average_industrial_output_per_capita": {
            "initial": {
                "industrial_output_per_capita": 1,
                "income_expectation_averaging_time": 1,
            },
            "step": {
                "industrial_output_per_capita": 1,
                "income_expectation_averaging_time": 1,
            },
        }
    },
)
def average_industrial_output_per_capita():
    """
    Average industrial output per capita (AIOPC#43).
    """
    return _smooth_average_industrial_output_per_capita()


_smooth_average_industrial_output_per_capita = Smooth(
    lambda: industrial_output_per_capita(),
    lambda: income_expectation_averaging_time(),
    lambda: industrial_output_per_capita(),
    lambda: 1,
    "_smooth_average_industrial_output_per_capita",
)


@component.add(
    name="completed multiplier from perceived lifetime",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "perceived_life_expectancy": 1,
        "one_year": 1,
        "completed_multiplier_from_perceived_lifetime_table": 1,
    },
)
def completed_multiplier_from_perceived_lifetime():
    """
    COMPENSATORY MULTIPLIER FROM PERCEIVED LIFE EXPECTANCY (CMPLE#36).
    """
    return completed_multiplier_from_perceived_lifetime_table(
        perceived_life_expectancy() / one_year()
    )


@component.add(
    name="completed multiplier from perceived lifetime table",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_completed_multiplier_from_perceived_lifetime_table"
    },
)
def completed_multiplier_from_perceived_lifetime_table(x, final_subs=None):
    """
    Table relating perceived life expectancy to birth rate compensation (CMPLET#36.1).
    """
    return _hardcodedlookup_completed_multiplier_from_perceived_lifetime_table(
        x, final_subs
    )


_hardcodedlookup_completed_multiplier_from_perceived_lifetime_table = HardcodedLookups(
    [0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0],
    [3.0, 2.1, 1.6, 1.4, 1.3, 1.2, 1.1, 1.05, 1.0],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_completed_multiplier_from_perceived_lifetime_table",
)


@component.add(
    name="delayed industrial output per capita",
    units="$/(Person*year)",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_delayed_industrial_output_per_capita": 1},
    other_deps={
        "_smooth_delayed_industrial_output_per_capita": {
            "initial": {
                "industrial_output_per_capita": 1,
                "social_adjustment_delay": 1,
            },
            "step": {"industrial_output_per_capita": 1, "social_adjustment_delay": 1},
        }
    },
)
def delayed_industrial_output_per_capita():
    """
    Delayed industrial output per capita (DIOPC#40).
    """
    return _smooth_delayed_industrial_output_per_capita()


_smooth_delayed_industrial_output_per_capita = Smooth(
    lambda: industrial_output_per_capita(),
    lambda: social_adjustment_delay(),
    lambda: industrial_output_per_capita(),
    lambda: 3,
    "_smooth_delayed_industrial_output_per_capita",
)


@component.add(
    name="desired completed family size normal",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def desired_completed_family_size_normal():
    """
    DESIRED COMPLETED FAMILY SIZE NORMAL (DCFSN#38.2).
    """
    return 3.8


@component.add(
    name="desired total fertility",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "desired_completed_family_size": 1,
        "completed_multiplier_from_perceived_lifetime": 1,
    },
)
def desired_total_fertility():
    """
    DESIRED TOTAL FERTILITY (DTF#35).
    """
    return (
        desired_completed_family_size() * completed_multiplier_from_perceived_lifetime()
    )


@component.add(
    name="family income expectation",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "industrial_output_per_capita": 1,
        "average_industrial_output_per_capita": 2,
    },
)
def family_income_expectation():
    """
    Family income expectations (FIE#42).
    """
    return (
        industrial_output_per_capita() - average_industrial_output_per_capita()
    ) / average_industrial_output_per_capita()


@component.add(
    name="family response to social norm",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "family_income_expectation": 1,
        "family_response_to_social_norm_table": 1,
    },
)
def family_response_to_social_norm():
    """
    FAMILY RESPONSE TO SOCIAL NORM (FRSN#41).
    """
    return family_response_to_social_norm_table(family_income_expectation())


@component.add(
    name="family response to social norm table",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_family_response_to_social_norm_table"},
)
def family_response_to_social_norm_table(x, final_subs=None):
    """
    The table relating income expectations to family size (FRSNT#41.1).
    """
    return _hardcodedlookup_family_response_to_social_norm_table(x, final_subs)


_hardcodedlookup_family_response_to_social_norm_table = HardcodedLookups(
    [-0.2, -0.1, 0.0, 0.1, 0.2],
    [0.5, 0.6, 0.7, 0.85, 1.0],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_family_response_to_social_norm_table",
)


@component.add(
    name="fecundity multiplier",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"life_expectancy": 1, "one_year": 1, "fecundity_multiplier_table": 1},
)
def fecundity_multiplier():
    """
    FECUNDITY MULTIPLIER (FM#34).
    """
    return fecundity_multiplier_table(life_expectancy() / one_year())


@component.add(
    name="fecundity multiplier table",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_fecundity_multiplier_table"},
)
def fecundity_multiplier_table(x, final_subs=None):
    """
    Table relating life expectancy to fecundity (FMT#34.1).
    """
    return _hardcodedlookup_fecundity_multiplier_table(x, final_subs)


_hardcodedlookup_fecundity_multiplier_table = HardcodedLookups(
    [0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0],
    [0.0, 0.2, 0.4, 0.6, 0.7, 0.75, 0.79, 0.84, 0.87],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_fecundity_multiplier_table",
)


@component.add(
    name="fertility control allocation per capita",
    units="$/(Person*year)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "fraction_services_allocated_to_fertility_control": 1,
        "service_output_per_capita": 1,
    },
)
def fertility_control_allocation_per_capita():
    """
    FERTILITY CONTROL ALLOCATIONS PER CAPITA (FCAPC#47).
    """
    return (
        fraction_services_allocated_to_fertility_control() * service_output_per_capita()
    )


@component.add(
    name="fertility control effectiveness table",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_fertility_control_effectiveness_table"},
)
def fertility_control_effectiveness_table(x, final_subs=None):
    """
    Fertility control effectiveness table (FCET#45.2).
    """
    return _hardcodedlookup_fertility_control_effectiveness_table(x, final_subs)


_hardcodedlookup_fertility_control_effectiveness_table = HardcodedLookups(
    [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
    [0.75, 0.85, 0.9, 0.95, 0.98, 0.99, 1.0],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_fertility_control_effectiveness_table",
)


@component.add(
    name="fertility control facilities per capita",
    units="$/(Person*year)",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_fertility_control_facilities_per_capita": 1},
    other_deps={
        "_smooth_fertility_control_facilities_per_capita": {
            "initial": {
                "fertility_control_allocation_per_capita": 1,
                "health_services_impact_delay": 1,
            },
            "step": {
                "fertility_control_allocation_per_capita": 1,
                "health_services_impact_delay": 1,
            },
        }
    },
)
def fertility_control_facilities_per_capita():
    """
    FERTILITY CONTROL FACILITIES PER CAPITA (FCFPC#46).
    """
    return _smooth_fertility_control_facilities_per_capita()


_smooth_fertility_control_facilities_per_capita = Smooth(
    lambda: fertility_control_allocation_per_capita(),
    lambda: health_services_impact_delay(),
    lambda: fertility_control_allocation_per_capita(),
    lambda: 3,
    "_smooth_fertility_control_facilities_per_capita",
)


@component.add(
    name="fraction services allocated to fertility control",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "need_for_fertility_control": 1,
        "fraction_services_allocated_to_fertility_control_table": 1,
    },
)
def fraction_services_allocated_to_fertility_control():
    """
    FRACTION OF SERVICES ALLOCATED TO FERTILITY CONTROL (FSAFC#48).
    """
    return fraction_services_allocated_to_fertility_control_table(
        need_for_fertility_control()
    )


@component.add(
    name="fraction services allocated to fertility control table",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_fraction_services_allocated_to_fertility_control_table"
    },
)
def fraction_services_allocated_to_fertility_control_table(x, final_subs=None):
    """
    Table relating the need for fertility control to services allocated. (FSAFCT#48.1).
    """
    return _hardcodedlookup_fraction_services_allocated_to_fertility_control_table(
        x, final_subs
    )


_hardcodedlookup_fraction_services_allocated_to_fertility_control_table = (
    HardcodedLookups(
        [0.0, 2.0, 4.0, 6.0, 8.0, 10.0],
        [0.0, 0.005, 0.015, 0.025, 0.03, 0.035],
        {},
        "interpolate",
        {},
        "_hardcodedlookup_fraction_services_allocated_to_fertility_control_table",
    )
)


@component.add(
    name="income expectation averaging time",
    units="year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def income_expectation_averaging_time():
    """
    Income expectation averaging time (IEAT#43.1)
    """
    return 3


@component.add(
    name="lifetime perception delay",
    units="year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def lifetime_perception_delay():
    """
    Lifetime perception delay (LPD#37.1)
    """
    return 20


@component.add(
    name="maximum total fertility",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"maximum_total_fertility_normal": 1, "fecundity_multiplier": 1},
)
def maximum_total_fertility():
    """
    MAXIMUM TOTAL FERTILITY (MTF#33).
    """
    return maximum_total_fertility_normal() * fecundity_multiplier()


@component.add(
    name="maximum total fertility normal",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def maximum_total_fertility_normal():
    """
    The normal maximum fertility that would be realized if people had sufficient food and perfect health. (MTFN#33)
    """
    return 12


@component.add(
    name="need for fertility control",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"maximum_total_fertility": 1, "desired_total_fertility": 1},
)
def need_for_fertility_control():
    """
    NEED FOR FERTILITY CONTROL (NFC#44).
    """
    return maximum_total_fertility() / desired_total_fertility() - 1


@component.add(
    name="perceived life expectancy",
    units="year",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_perceived_life_expectancy": 1},
    other_deps={
        "_smooth_perceived_life_expectancy": {
            "initial": {"life_expectancy": 1, "lifetime_perception_delay": 1},
            "step": {"life_expectancy": 1, "lifetime_perception_delay": 1},
        }
    },
)
def perceived_life_expectancy():
    """
    Perceived life expectancy (PLE#37)
    """
    return _smooth_perceived_life_expectancy()


_smooth_perceived_life_expectancy = Smooth(
    lambda: life_expectancy(),
    lambda: lifetime_perception_delay(),
    lambda: life_expectancy(),
    lambda: 3,
    "_smooth_perceived_life_expectancy",
)


@component.add(
    name="social family size normal",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "delayed_industrial_output_per_capita": 1,
        "gdp_pc_unit": 1,
        "social_family_size_normal_table": 1,
    },
)
def social_family_size_normal():
    """
    SOCIAL FAMILY SIZE NORM (SFN#39).
    """
    return social_family_size_normal_table(
        delayed_industrial_output_per_capita() / gdp_pc_unit()
    )


@component.add(
    name="social family size normal table",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_social_family_size_normal_table"},
)
def social_family_size_normal_table(x, final_subs=None):
    """
    Table relating material well being to family size (SFNT#39.1)
    """
    return _hardcodedlookup_social_family_size_normal_table(x, final_subs)


_hardcodedlookup_social_family_size_normal_table = HardcodedLookups(
    [0.0, 200.0, 400.0, 600.0, 800.0],
    [1.25, 0.94, 0.715, 0.59, 0.5],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_social_family_size_normal_table",
)


@component.add(
    name="social adjustment delay",
    units="year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def social_adjustment_delay():
    """
    SOCIAL ADJUSTMENT DELAY (SAD#40.1).
    """
    return 20


@component.add(
    name="total fertility",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "maximum_total_fertility": 2,
        "desired_total_fertility": 1,
        "fertility_control_effectiveness": 2,
    },
)
def total_fertility():
    """
    TOTAL FERTILITY (TF#32).
    """
    return np.minimum(
        maximum_total_fertility(),
        maximum_total_fertility() * (1 - fertility_control_effectiveness())
        + desired_total_fertility() * fertility_control_effectiveness(),
    )
