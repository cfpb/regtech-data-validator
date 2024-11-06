"""
Subclasses of Pandera's `Check` class
"""

from enum import StrEnum
from typing import Any, Callable, Type

from pandera import Check
from pandera.backends.base import BaseCheckBackend
from pandera.backends.polars.checks import PolarsCheckBackend


class Severity(StrEnum):
    ERROR = 'Error'
    WARNING = 'Warning'


class SBLCheck(Check):
    """
    A Pandera.Check subclasss that requires a `name` and an `id` be
    specified. Additionally, an attribute named `warning` is added to
    the class to enable distinction between warnings and errors. The
    default value of warning is `False` which corresponds to an error.
    Don't use this class directly. Make use of the SBLErrorCheck and
    SBLWarningCheck subclasses below.
    """

    def __init__(
        self,
        check_fn: Callable,
        id: str,
        name: str,
        description: str,
        severity: Severity,
        fig_link: str,
        scope: str,
        **check_kwargs
    ):
        """
        Subclass of Pandera's `Check`, with special handling for severity level
        Args:
            check_fn (Callable): A function which evaluates the validity of the column(s) being tested.
            id (str, required): Unique identifier for a check
            name (str, required): Unique name for a check
            description (str, required): Long-form description of a check
            severity (Severity, required): The severity of a check (error or warning)
            check_kwargs (Any, optional): Parameters passed to `check_fn` function
        """

        self.severity = severity
        self.fig_link = fig_link
        self.scope = scope

        super().__init__(check_fn, title=id, name=name, description=description, **check_kwargs)

    @classmethod
    def get_backend(cls, check_obj: Any) -> Type[BaseCheckBackend]:
        """Assume Pandas DataFrame and return PandasCheckBackend"""
        return PolarsCheckBackend
