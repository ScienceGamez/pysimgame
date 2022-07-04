"""
Module services_output
Translated using PySD version 3.4.0
"""


@component.add(
    name="indicated services output per capita",
    units="$/(Person*year)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"indicated_services_output_per_capita_1": 1},
)
def indicated_services_output_per_capita():
    """
    Indicated service output per capita (ISOPC#60).
    """
    return indicated_services_output_per_capita_1()


@component.add(
    name="fraction of industrial output allocated to services",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"fraction_of_industrial_output_allocated_to_services_1": 1},
)
def fraction_of_industrial_output_allocated_to_services():
    """
    FRACTION OF INDUSTRIAL OUTPUT ALLOCATED TO SERVICES (FIOAS#63).
    """
    return fraction_of_industrial_output_allocated_to_services_1()


@component.add(
    name="average life of service capital",
    units="year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def average_life_of_service_capital():
    """
    AVERAGE LIFETIME OF SERVICE CAPITAL (ALSC#69)
    """
    return 20


@component.add(
    name="service capital output ratio",
    units="year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def service_capital_output_ratio():
    """
    Service capital output ratio (SCOR#72).
    """
    return 1


@component.add(
    name="fraction of industrial output allocated to services 1",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "service_output_per_capita": 1,
        "indicated_services_output_per_capita": 1,
        "fraction_of_industrial_output_allocated_to_services_table_1": 1,
    },
)
def fraction_of_industrial_output_allocated_to_services_1():
    """
    FRACTION OF INDUSTRIAL OUTPUT ALLOCATED TO SERVICES before policy year (FIOAS1#64).
    """
    return fraction_of_industrial_output_allocated_to_services_table_1(
        service_output_per_capita() / indicated_services_output_per_capita()
    )


@component.add(
    name="fraction of industrial output allocated to services table 1",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_fraction_of_industrial_output_allocated_to_services_table_1"
    },
)
def fraction_of_industrial_output_allocated_to_services_table_1(x, final_subs=None):
    """
    Table relating service output to the fraction of industrial output allocated to service (FIOAS1T#64.1).
    """
    return _hardcodedlookup_fraction_of_industrial_output_allocated_to_services_table_1(
        x, final_subs
    )


_hardcodedlookup_fraction_of_industrial_output_allocated_to_services_table_1 = (
    HardcodedLookups(
        [0.0, 0.5, 1.0, 1.5, 2.0],
        [0.3, 0.2, 0.1, 0.05, 0.0],
        {},
        "interpolate",
        {},
        "_hardcodedlookup_fraction_of_industrial_output_allocated_to_services_table_1",
    )
)


@component.add(
    name="fraction of industrial output allocated to services 2",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "service_output_per_capita": 1,
        "indicated_services_output_per_capita": 1,
        "fraction_of_industrial_output_allocated_to_services_table_2": 1,
    },
)
def fraction_of_industrial_output_allocated_to_services_2():
    """
    FRACTION OF INDUSTRIAL OUTPUT ALLOCATED TO SERVICES after policy year (FIOAS2#65).
    """
    return fraction_of_industrial_output_allocated_to_services_table_2(
        service_output_per_capita() / indicated_services_output_per_capita()
    )


@component.add(
    name="fraction of industrial output allocated to services table 2",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_fraction_of_industrial_output_allocated_to_services_table_2"
    },
)
def fraction_of_industrial_output_allocated_to_services_table_2(x, final_subs=None):
    """
    Table relating service output to the fraction of industrial output allocated to service (FIOAS2T#65.1).
    """
    return _hardcodedlookup_fraction_of_industrial_output_allocated_to_services_table_2(
        x, final_subs
    )


_hardcodedlookup_fraction_of_industrial_output_allocated_to_services_table_2 = (
    HardcodedLookups(
        [0.0, 0.5, 1.0, 1.5, 2.0],
        [0.3, 0.2, 0.1, 0.05, 0.0],
        {},
        "interpolate",
        {},
        "_hardcodedlookup_fraction_of_industrial_output_allocated_to_services_table_2",
    )
)


@component.add(
    name="indicated services output per capita 1",
    units="$/(Person*year)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "industrial_output_per_capita": 1,
        "gdp_pc_unit": 1,
        "indicated_services_output_per_capita_table_1": 1,
    },
)
def indicated_services_output_per_capita_1():
    """
    Indicated service output per capita before policy year (ISOPC1#61).
    """
    return indicated_services_output_per_capita_table_1(
        industrial_output_per_capita() / gdp_pc_unit()
    )


@component.add(
    name="indicated services output per capita table 1",
    units="$/(Person*year)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_indicated_services_output_per_capita_table_1"
    },
)
def indicated_services_output_per_capita_table_1(x, final_subs=None):
    """
    Table relating industrial output per capita to the indicated service output per capita before policy year (ISOPC1T#61.1).
    """
    return _hardcodedlookup_indicated_services_output_per_capita_table_1(x, final_subs)


_hardcodedlookup_indicated_services_output_per_capita_table_1 = HardcodedLookups(
    [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600],
    [40, 300, 640, 1000, 1220, 1450, 1650, 1800, 2000],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_indicated_services_output_per_capita_table_1",
)


@component.add(
    name="indicated services output per capita 2",
    units="$/(Person*year)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "industrial_output_per_capita": 1,
        "gdp_pc_unit": 1,
        "indicated_services_output_per_capita_table_2": 1,
    },
)
def indicated_services_output_per_capita_2():
    """
    Indicated service output per capita after policy year (ISOPC2#621).
    """
    return indicated_services_output_per_capita_table_2(
        industrial_output_per_capita() / gdp_pc_unit()
    )


@component.add(
    name="indicated services output per capita table 2",
    units="$/(Person*year)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_indicated_services_output_per_capita_table_2"
    },
)
def indicated_services_output_per_capita_table_2(x, final_subs=None):
    """
    Table relating industrial output per capita to the indicated service output per capita afte policy year (ISOPC1T#62.1).
    """
    return _hardcodedlookup_indicated_services_output_per_capita_table_2(x, final_subs)


_hardcodedlookup_indicated_services_output_per_capita_table_2 = HardcodedLookups(
    [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600],
    [40, 300, 640, 1000, 1220, 1450, 1650, 1800, 2000],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_indicated_services_output_per_capita_table_2",
)


@component.add(
    name="service capital depreciation",
    units="$/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"service_capital": 1, "average_life_of_service_capital": 1},
)
def service_capital_depreciation():
    """
    SERVICE CAPITAL DEPRECIATION RATE (SCDR#68).
    """
    return service_capital() / average_life_of_service_capital()


@component.add(
    name="service capital investment",
    units="$/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "industrial_output": 1,
        "fraction_of_industrial_output_allocated_to_services": 1,
    },
)
def service_capital_investment():
    """
    SERVICE CAPITAL INVESTMENT RATE (SCIR#66).
    """
    return industrial_output() * fraction_of_industrial_output_allocated_to_services()


@component.add(
    name="service output per capita",
    units="$/(Person*year)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"service_output": 1, "population": 1},
)
def service_output_per_capita():
    """
    SERVICE OUTPUT PER CAPITA (SOPC#71).
    """
    return service_output() / population()


@component.add(
    name="Service Capital",
    units="$",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_service_capital": 1},
    other_deps={
        "_integ_service_capital": {
            "initial": {"initial_service_capital": 1},
            "step": {
                "service_capital_investment": 1,
                "service_capital_depreciation": 1,
            },
        }
    },
)
def service_capital():
    """
    Service capital (SC#67).
    """
    return _integ_service_capital()


_integ_service_capital = Integ(
    lambda: service_capital_investment() - service_capital_depreciation(),
    lambda: initial_service_capital(),
    "_integ_service_capital",
)


@component.add(
    name="initial service capital",
    units="$",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_service_capital():
    """
    The initial level of service capital (SCI#67.2)
    """
    return 144000000000.0


@component.add(
    name="service output",
    units="$/year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "service_capital": 1,
        "capacity_utilization_fraction": 1,
        "service_capital_output_ratio": 1,
    },
)
def service_output():
    """
    Service output (SO#70).
    """
    return (
        service_capital()
        * capacity_utilization_fraction()
        / service_capital_output_ratio()
    )
