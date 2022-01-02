"""Splitting methods are function that can accept the list of
all the models and return the list of values that should be assigned.

Note import variables of time t are computed using the export variables
of time t-1.
Other variables computed at time t will use import variables computed in time t.
TODO: make sure it should work this way, maybe other variables want to use t-1
"""
from __future__ import annotations

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from pysimgame.types import ImportExportMethod, ModelType


def equally_distibuted(
    export_variable: str, import_variable: str, models: List[ModelType]
) -> List[float]:
    """Distribute the sum of the exports to all regions equally."""
    total_export = sum([getattr(model, export_variable)() for model in models])
    return [total_export / len(models)] * len(models)


def weighted_average(weighted_attribute: str) -> ImportExportMethod:
    """Will perform a weighted average on the given attribute value.

    This method needs to be called and will return the desired import
    export method.
    """

    def import_export_method(
        export_variable: str, import_variable: str, models: List[ModelType]
    ) -> List[float]:
        """The actual method that is used."""
        total_export = sum(
            [getattr(model, export_variable)() for model in models]
        )
        weights = [getattr(model, weighted_attribute)() for model in models]
        total_weight = sum(weights)
        return [total_export * w / total_weight for w in weights]

    return import_export_method


def fulfil_imports(
    preference: str, reverse: bool = False
) -> ImportExportMethod:
    """Try to fulfil the import values.

    Will try to fulfil first the imports using the highest value given
    by calling the attribute in preference.
    Reverse can be used for changing the order of preference.

    If the sum of all exported values is < 0, then all the imports will
    be 0.
    If the exported values is greater than than the sum of all imports
    then the overflow is thrown away.

    TODO: make sure this method has preseraved order depending on what
    the model imputs can be. (Ensure with the 1rst step inputs.)
    """
    # Flag for the first step
    is_first_step: bool = True
    original_import_methods: List = []

    def import_export_method(
        export_variable: str, import_variable: str, models: List[ModelType]
    ) -> List[float]:
        nonlocal is_first_step
        if is_first_step:
            # Store the original methods
            original_import_methods.extend(
                getattr(model, import_variable) for model in models
            )
            print(f"First step: {original_import_methods = }")
            is_first_step = False
        total_export = sum(
            [getattr(model, export_variable)() for model in models]
        )
        preference_values = [getattr(model, preference)() for model in models]
        argsorted_values = sorted(
            range(len(models)),
            key=preference_values.__getitem__,
            reverse=not reverse,  # Sort from most needing by default
        )
        print(f"Steps {total_export = }")
        imports = [0.0 for _ in models]
        while argsorted_values and total_export > 0:
            index = argsorted_values.pop(0)
            required = original_import_methods[index]()
            print(f"{index = }, {required = }")
            imports[index] = min(required, total_export)
            # updates the exports left
            total_export -= required
        print(f"Steps {imports = }")
        return imports

    return import_export_method
