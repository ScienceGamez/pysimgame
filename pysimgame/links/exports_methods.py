"""Splitting methods are function that can accept the list of
all the models and return the list of values that should be assigned.

Note import variables of time t are computed using the export variables
of time t-1.
Other variables computed at time t will use import variables computed in time t.
TODO: make sure it should work this way, maybe other variables want to use t-1
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Dict, List, Tuple

from pysimgame.utils.logging import register_logger

logger = logging.getLogger(__name__)
register_logger(logger)

if TYPE_CHECKING:
    from pysimgame.types import ExportImportMethod, ModelType, RegionName


def export_all_equally_distibuted() -> ExportImportMethod:
    """Distribute the sum of the exports to all regions equally.

    .. note:: this ignores the equation set for the imports
    """

    def _export_all_equally_distibuted(
        export_variable: str,
        import_variable: str,
        models: Dict[RegionName, ModelType],
    ) -> Tuple[Dict[RegionName, float], Dict[RegionName, float]]:

        exports = {
            region: getattr(model, export_variable)()
            for region, model in models.items()
        }
        total_export = sum(exports.items())
        import_value = total_export / len(models)
        imports = {region: import_value for region in models.keys()}
        return exports, imports

    return _export_all_equally_distibuted


def weighted_average(weighted_attribute: str) -> ExportImportMethod:
    """Will perform a weighted average on the given attribute value.

    This method needs to be called and will return the desired import
    export method.
    .. note:: this ignores the equation set for the imports

    """

    def _weighted_average(
        export_variable: str,
        import_variable: str,
        models: Dict[RegionName, ModelType],
    ) -> Tuple[Dict[RegionName, float], Dict[RegionName, float]]:

        exports = {
            region: getattr(model, export_variable)()
            for region, model in models.items()
        }
        total_export = sum(exports.values())
        weights = {
            region: getattr(model, weighted_attribute)()
            for region, model in models.items()
        }
        total_weight = sum(weights)
        imports = {
            region: total_export * w / total_weight
            for region, w in weights.items()
        }
        return exports, imports

    return _weighted_average


def fulfil_imports(
    preference: str, reverse: bool = False
) -> ExportImportMethod:
    """Try to fulfil the import values.

    Will try to fulfil first the imports using the highest value given
    by calling the attribute in preference.
    Reverse can be used for changing the order of preference.

    If the sum of all exported values is < 0, then all the imports will
    be 0.
    If the exported values is greater than than the sum of all imports
    then the overflow is thrown away.

    """

    def _fulfil_imports(
        export_variable: str,
        import_variable: str,
        models: Dict[str, ModelType],
    ) -> Tuple[Dict[RegionName, float], Dict[RegionName, float]]:
        exports = {
            region: getattr(model, export_variable)()
            for region, model in models.items()
        }
        total_export = sum(exports.values())
        preference_values = {
            region: getattr(model, preference)()
            for region, model in models.items()
        }
        keys = sorted(
            list(preference_values.keys()),
            key=preference_values.values().__getitem__,
            reverse=not reverse,  # Sort from most needing by default
        )
        logger.debug(f"Steps {total_export = }")
        imports = {region: 0.0 for region in models.keys()}
        while keys and total_export > 0:
            region = keys.pop(0)
            required = getattr(models[region], import_variable)()
            logger.debug(f"{region = }, {required = }")
            imports[region] = min(required, total_export)
            # updates the exports left
            total_export -= required
        logger.debug(f"Steps {imports = }")

        # TODO: decide if we throw away the exports or if we change their
        # value
        return exports, imports

    return _fulfil_imports
