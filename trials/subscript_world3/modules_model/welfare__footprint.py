"""
Module welfare__footprint
Translated using PySD version 3.4.0
"""


@component.add(
    name='"Absorption Land (GHA)"',
    units="Ghectares",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "persistent_pollution_generation_rate": 1,
        "ha_per_unit_of_pollution": 1,
        "ha_per_gha": 1,
    },
)
def absorption_land_gha():
    return (
        persistent_pollution_generation_rate()
        * ha_per_unit_of_pollution()
        / ha_per_gha()
    )


@component.add(
    name='"Arable Land in Gigahectares (GHA)"',
    units="Ghectares",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"arable_land": 1, "ha_per_gha": 1},
)
def arable_land_in_gigahectares_gha():
    return arable_land() / ha_per_gha()


@component.add(
    name="Education Index",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"gdp_per_capita": 1, "gdp_pc_unit": 1, "education_index_lookup": 1},
)
def education_index():
    return education_index_lookup(gdp_per_capita() / gdp_pc_unit())


@component.add(
    name="Education Index LOOKUP",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_education_index_lookup"},
)
def education_index_lookup(x, final_subs=None):
    return _hardcodedlookup_education_index_lookup(x, final_subs)


_hardcodedlookup_education_index_lookup = HardcodedLookups(
    [0.0, 1000.0, 2000.0, 3000.0, 4000.0, 5000.0, 6000.0, 7000.0],
    [0.0, 0.81, 0.88, 0.92, 0.95, 0.98, 0.99, 1.0],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_education_index_lookup",
)


@component.add(
    name="GDP Index",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"gdp_per_capita": 1, "ref_lo_gdp": 2, "ref_hi_gdp": 1},
)
def gdp_index():
    return (np.log(gdp_per_capita() / ref_lo_gdp()) / np.log(10)) / (
        np.log(ref_hi_gdp() / ref_lo_gdp()) / np.log(10)
    )


@component.add(
    name="GDP per capita",
    units="$/(year*Person)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "industrial_output_per_capita": 1,
        "gdp_pc_unit": 1,
        "gdp_per_capita_lookup": 1,
    },
)
def gdp_per_capita():
    return gdp_per_capita_lookup(industrial_output_per_capita() / gdp_pc_unit())


@component.add(
    name="GDP per capita LOOKUP",
    units="$/(year*Person)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_gdp_per_capita_lookup"},
)
def gdp_per_capita_lookup(x, final_subs=None):
    return _hardcodedlookup_gdp_per_capita_lookup(x, final_subs)


_hardcodedlookup_gdp_per_capita_lookup = HardcodedLookups(
    [0, 200, 400, 600, 800, 1000],
    [120, 600, 1200, 1800, 2500, 3200],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_gdp_per_capita_lookup",
)


@component.add(
    name="ha per Gha",
    units="hectare/Ghectare",
    comp_type="Constant",
    comp_subtype="Normal",
)
def ha_per_gha():
    return 1000000000.0


@component.add(
    name="ha per unit of pollution",
    units="hectares/(Pollution units/year)",
    comp_type="Constant",
    comp_subtype="Normal",
)
def ha_per_unit_of_pollution():
    return 4


@component.add(
    name="Human Ecological Footprint",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "arable_land_in_gigahectares_gha": 1,
        "urban_land_gha": 1,
        "absorption_land_gha": 1,
        "total_land": 1,
    },
)
def human_ecological_footprint():
    """
    See Appendix 2 of Limits to Growth - the 30-Year Update for discussion of this index
    """
    return (
        arable_land_in_gigahectares_gha() + urban_land_gha() + absorption_land_gha()
    ) / total_land()


@component.add(
    name="Human Welfare Index",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"life_expectancy_index": 1, "education_index": 1, "gdp_index": 1},
)
def human_welfare_index():
    """
    See Appendix 2 of Limits to Growth - the 30-Year Update for discussion of this index
    """
    return (life_expectancy_index() + education_index() + gdp_index()) / 3


@component.add(
    name="Life Expectancy Index",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"life_expectancy": 1, "one_year": 1, "life_expectancy_index_lookup": 1},
)
def life_expectancy_index():
    return life_expectancy_index_lookup(life_expectancy() / one_year())


@component.add(
    name="Life Expectancy Index LOOKUP",
    units="Dmnl",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_life_expectancy_index_lookup"},
)
def life_expectancy_index_lookup(x, final_subs=None):
    return _hardcodedlookup_life_expectancy_index_lookup(x, final_subs)


_hardcodedlookup_life_expectancy_index_lookup = HardcodedLookups(
    [25.0, 35.0, 45.0, 55.0, 65.0, 75.0, 85.0],
    [0.0, 0.16, 0.33, 0.5, 0.67, 0.84, 1.0],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_life_expectancy_index_lookup",
)


@component.add(
    name="Ref Hi GDP",
    units="$/(year*Person)",
    comp_type="Constant",
    comp_subtype="Normal",
)
def ref_hi_gdp():
    return 9508


@component.add(
    name="Ref Lo GDP",
    units="$/(year*Person)",
    comp_type="Constant",
    comp_subtype="Normal",
)
def ref_lo_gdp():
    return 24


@component.add(
    name="Total Land", units="Ghectares", comp_type="Constant", comp_subtype="Normal"
)
def total_land():
    return 1.91


@component.add(
    name='"Urban Land (GHA)"',
    units="Ghectares",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"urban_and_industrial_land": 1, "ha_per_gha": 1},
)
def urban_land_gha():
    return urban_and_industrial_land() / ha_per_gha()
