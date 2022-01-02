if TYPE_CHECKING:
    from typing import TYPE_CHECKING, Callable, List

    from pysimgame.types import ImportExportMethod, ModelType


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


def import_export(
    export_variable: str,
    import_variable: str,
    method: ImportExportMethod,
) -> None:
    """Create an import export system between regions.

    At every step, this will sum up all the export varialbes in the
    regions and compute the import variable.
    Different methods exist for splitting.

    """
    from .manager import _LINKS_MANAGER

    _LINKS_MANAGER.MODEL_MANAGER.link_import_export(
        export_variable, import_variable, method
    )
