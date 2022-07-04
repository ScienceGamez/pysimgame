"""
Module jobs
Translated using PySD version 3.4.0
"""


@component.add(
    name="Delayed Labor Utilization Fraction",
    units="Dmnl",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_delayed_labor_utilization_fraction": 1},
    other_deps={
        "_smooth_delayed_labor_utilization_fraction": {
            "initial": {"labor_utilization_fraction_delay_time": 1},
            "step": {
                "labor_utilization_fraction": 1,
                "labor_utilization_fraction_delay_time": 1,
            },
        }
    },
)
def delayed_labor_utilization_fraction():
    """
    LABOR UTILIZATION FRACTION DELAYED (LUFD#82)
    """
    return _smooth_delayed_labor_utilization_fraction()


_smooth_delayed_labor_utilization_fraction = Smooth(
    lambda: labor_utilization_fraction(),
    lambda: labor_utilization_fraction_delay_time(),
    lambda: 1,
    lambda: 1,
    "_smooth_delayed_labor_utilization_fraction",
)


@component.add(
    name="capacity utilization fraction",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"_active_initial_capacity_utilization_fraction": 1},
    other_deps={
        "_active_initial_capacity_utilization_fraction": {
            "initial": {},
            "step": {
                "delayed_labor_utilization_fraction": 1,
                "capacity_utilization_fraction_table": 1,
            },
        }
    },
)
def capacity_utilization_fraction():
    """
    CAPITAL UTILIZATION FRACTION (CUF#83)
    """
    return active_initial(
        __data["time"].stage,
        lambda: capacity_utilization_fraction_table(
            delayed_labor_utilization_fraction()
        ),
        1,
    )


@component.add(
    name="capacity utilization fraction table",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_capacity_utilization_fraction_table"},
)
def capacity_utilization_fraction_table(x, final_subs=None):
    """
    Table relating labor utilization to capacity utilization (CUFT#83.2).
    """
    return _hardcodedlookup_capacity_utilization_fraction_table(x, final_subs)


_hardcodedlookup_capacity_utilization_fraction_table = HardcodedLookups(
    [1.0, 3.0, 5.0, 7.0, 9.0, 11.0],
    [1.0, 0.9, 0.7, 0.3, 0.1, 0.1],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_capacity_utilization_fraction_table",
)


@component.add(
    name="jobs",
    units="Person",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "potential_jobs_industrial_sector": 1,
        "potential_jobs_agricultural_sector": 1,
        "potential_jobs_service_sector": 1,
    },
)
def jobs():
    """
    JOBS (J#73).
    """
    return (
        potential_jobs_industrial_sector()
        + potential_jobs_agricultural_sector()
        + potential_jobs_service_sector()
    )


@component.add(
    name="jobs per hectare",
    units="Person/hectare",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "agricultural_input_per_hectare": 1,
        "unit_agricultural_input": 1,
        "jobs_per_hectare_table": 1,
    },
)
def jobs_per_hectare():
    """
    Jobs per hectare in agriculture (JPH#79).
    """
    return jobs_per_hectare_table(
        agricultural_input_per_hectare() / unit_agricultural_input()
    )


@component.add(
    name="jobs per hectare table",
    units="Person/hectare",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_jobs_per_hectare_table"},
)
def jobs_per_hectare_table(x, final_subs=None):
    """
    Table relating agricultural input intensity to the number of jobs per hectare in agriculture (JPHT#79.1).
    """
    return _hardcodedlookup_jobs_per_hectare_table(x, final_subs)


_hardcodedlookup_jobs_per_hectare_table = HardcodedLookups(
    [2.0, 6.0, 10.0, 14.0, 18.0, 22.0, 26.0, 30.0],
    [2.0, 0.5, 0.4, 0.3, 0.27, 0.24, 0.2, 0.2],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_jobs_per_hectare_table",
)


@component.add(
    name="jobs per industrial capital unit",
    units="Person/$",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "industrial_output_per_capita": 1,
        "gdp_pc_unit": 1,
        "jobs_per_industrial_capital_unit_table": 1,
    },
)
def jobs_per_industrial_capital_unit():
    """
    Jobs per industrial capital units (JPICU#75).
    """
    return (
        jobs_per_industrial_capital_unit_table(
            industrial_output_per_capita() / gdp_pc_unit()
        )
        * 0.001
    )


@component.add(
    name="jobs per industrial capital unit table",
    units="Person/$",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_jobs_per_industrial_capital_unit_table"
    },
)
def jobs_per_industrial_capital_unit_table(x, final_subs=None):
    """
    Table relating industrial output per capita to job per industrial capital unit (JPICUT#75.1).
    """
    return _hardcodedlookup_jobs_per_industrial_capital_unit_table(x, final_subs)


_hardcodedlookup_jobs_per_industrial_capital_unit_table = HardcodedLookups(
    [50.0, 200.0, 350.0, 500.0, 650.0, 800.0],
    [0.37, 0.18, 0.12, 0.09, 0.07, 0.06],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_jobs_per_industrial_capital_unit_table",
)


@component.add(
    name="jobs per service capital unit",
    units="Person/$",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "service_output_per_capita": 1,
        "gdp_pc_unit": 1,
        "jobs_per_service_capital_unit_table": 1,
    },
)
def jobs_per_service_capital_unit():
    """
    Jobs per service capital unit (JPSCU#77).
    """
    return (
        jobs_per_service_capital_unit_table(service_output_per_capita() / gdp_pc_unit())
        * 0.001
    )


@component.add(
    name="jobs per service capital unit table",
    units="Person/$",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_jobs_per_service_capital_unit_table"},
)
def jobs_per_service_capital_unit_table(x, final_subs=None):
    """
    Table relating service output per capita to job per service capital unit (JPICUT#77.1).
    """
    return _hardcodedlookup_jobs_per_service_capital_unit_table(x, final_subs)


_hardcodedlookup_jobs_per_service_capital_unit_table = HardcodedLookups(
    [50.0, 200.0, 350.0, 500.0, 650.0, 800.0],
    [1.1, 0.6, 0.35, 0.2, 0.15, 0.15],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_jobs_per_service_capital_unit_table",
)


@component.add(
    name="labor utilization fraction",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"jobs": 1, "labor_force": 1},
)
def labor_utilization_fraction():
    """
    Labor utilization fraction (LUF#81).
    """
    return jobs() / labor_force()


@component.add(
    name="labor utilization fraction delay time",
    units="year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def labor_utilization_fraction_delay_time():
    """
    Labor utilization fraction delay time (LUFDT#82.1)
    """
    return 2


@component.add(
    name="potential jobs agricultural sector",
    units="Person",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"jobs_per_hectare": 1, "arable_land": 1},
)
def potential_jobs_agricultural_sector():
    """
    Potential jobs in the agricultural sector (PJAS#78).
    """
    return jobs_per_hectare() * arable_land()


@component.add(
    name="potential jobs industrial sector",
    units="Person",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"industrial_capital": 1, "jobs_per_industrial_capital_unit": 1},
)
def potential_jobs_industrial_sector():
    """
    POTENTIAL JOBS IN INDUSTRIAL SECTOR (PKIS#74).
    """
    return industrial_capital() * jobs_per_industrial_capital_unit()


@component.add(
    name="potential jobs service sector",
    units="Person",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"service_capital": 1, "jobs_per_service_capital_unit": 1},
)
def potential_jobs_service_sector():
    """
    Potential jobs in the service sector (PJSS#76).
    """
    return service_capital() * jobs_per_service_capital_unit()
