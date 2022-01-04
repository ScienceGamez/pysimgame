from __future__ import annotations

from inspect import signature
from typing import TYPE_CHECKING

from pysimgame.utils.logging import logging, register_logger

if TYPE_CHECKING:
    from typing import Callable, List

    from pysimgame.types import ExportImportMethod, ModelsDict


def regions_sum(input_variable: str, output_variable: str) -> None:
    """Make a variable being the sum of another variable on all regions.

    The summed/output variable will automatically be shared by all models.
    TODO: also handle the registering of the output variable ?
    """
    from .manager import _LINKS_MANAGER

    _LINKS_MANAGER.MODEL_MANAGER.link_region_sum(
        input_variable, output_variable
    )


def regions_average(input_variable: str, output_variable: str) -> None:
    """Make a variable being the average of another variable on all regions.

    The average/output variable will automatically be shared by all models.
    """
    from .manager import _LINKS_MANAGER

    _LINKS_MANAGER.MODEL_MANAGER.link_region_average(
        input_variable, output_variable
    )


def export_import(
    export_variable: str,
    import_variable: str,
    method: ExportImportMethod,
) -> None:
    """Create an import export system between regions.

    At every step, this will sum up all the export varialbes in the
    regions and compute the import variable.
    Different methods exist for splitting.

    """
    from .manager import _LINKS_MANAGER

    # The method that will be send
    export_import_method: ExportImportMethod
    match len(signature(method).parameters):
        case 1:
            # only the models
            export_import_method = method
        case 3:
            # need to specifiy the export and imports
            def export_import_method(models: ModelsDict):
                return method(export_variable, import_variable, models)

        case _:
            logger = logging.getLogger(__name__)
            register_logger(logger)
            logger.error(
                f"Invalid signature for export_import_method {method}."
            )
            # Cannot register that function
            return

    _LINKS_MANAGER.MODEL_MANAGER.link_export_import(
        export_variable, import_variable, export_import_method
    )
