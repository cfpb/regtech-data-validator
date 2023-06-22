"""Custom check class"""

from typing import Callable

from pandera import Check
from pandera.backends.pandas.checks import PandasCheckBackend


class SBLCheck(Check):
    """A custom Pandera.Check subclasss that requires a `name` be
    specified. Additionally, an attribute named `warning` is added to
    the class to enable distinction between warnings and errors. The
    default value of warning is `False` which corresponds to an error.

    Don't use this class directly. Make use of the SBLErrorCheck and
    SBLWarningCheck subclasses below."""

    def __init__(self, check_fn: Callable, warning=False, *args, **kwargs):
        """Custom init method that verifies the presence of `name` in
        kwargs creates a custom class attribute called `warning`. All
        other initializaiton is handled by the parent Check class.

        Args:
            check_fn (Callable): A function which evaluates the validity
                of the column(s) being tested.
            warning (bool, optional): Boolean specifying whether to
                treat the check as a warning rather than an error.

        Raises:
            ValueError: Raised if `name` not supplied in kwargs.
        """

        if "name" not in kwargs:
            raise ValueError("Each check must be assigned a `name`.")

        # if warning==False treat check as an error check
        self.warning = warning

        super().__init__(check_fn=check_fn, *args, **kwargs)

    @classmethod
    def get_backend(cls, *args) -> PandasCheckBackend:
        """Assume Pandas DataFrame and return PandasCheckBackend"""
        return PandasCheckBackend
