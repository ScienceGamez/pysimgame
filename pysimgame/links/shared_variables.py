from __future__ import annotations

from typing import TYPE_CHECKING, List

from .manager import BaseLink

if TYPE_CHECKING:
    from .manager import LinksManager

_SHARED_VARIABLES: SharedVariables


class SharedVariables(BaseLink):
    """Singleton class used to register all the shared variables.

    TODO: Think about creating a "shared region"
    """

    variables: List[str]

    def __init__(self) -> None:
        super().__init__()
        global _SHARED_VARIABLES
        _SHARED_VARIABLES = self
        self.variables = []

    def register_variable(self, variable: str):
        """Actual registering of the variable in the model."""

        model_manager = self.LINKS_MANAGER.MODEL_MANAGER
        if not hasattr(model_manager.model, variable):
            self.LINKS_MANAGER.logger.error(
                f"Model has not attribute {variable}."
            )
        self.variables.append(variable)


def shared_variable(*variables: str):
    """Register shared variables.

    A shared variable has its value same accross all regions.
    """
    for var in variables:
        _SHARED_VARIABLES.register_variable(var)
