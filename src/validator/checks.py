"""Custom subclass for warnings and errors. 

The class SBLCheck is a subclass of the standard Pandera Check class
that requires the `name` kwarg to be supplied. Errors and warnings are
distinguised based on the value of the warning attribute. It defaults
to false but can be set to True during init to indicate the validation
should be handled as a warning rather than an error. 

Examples:

    warning_check = SBLCheck(
        lambda: True, 
        warning=True, 
        name="Just a Warning"
    )
    
    error_check_implied = SBLCheck(lambda: Truename="Error Check")
    
    error_check_explicit = SBLCheck(
        lambda: True,
        warning=False, 
        name="Also an Error"
    )
"""


from typing import Any, Callable, Type

from pandera import Check
from pandera.backends.base import BaseCheckBackend
from pandera.backends.pandas.checks import PandasCheckBackend


class SBLCheck(Check):
    """A custom Pandera.Check subclasss that requires a `name` and an `id` be
    specified. Additionally, an attribute named `warning` is added to
    the class to enable distinction between warnings and errors. The
    default value of warning is `False` which corresponds to an error.

    Don't use this class directly. Make use of the SBLErrorCheck and
    SBLWarningCheck subclasses below."""

    def __init__(
        self, check_fn: Callable, id: str = None, warning=False, *args, **kwargs
    ):
        """Custom init method that verifies the presence of `name` and `id` in
        kwargs creates a custom class attribute called `warning`. All
        other initializaiton is handled by the parent Check class.

        Args:
            check_fn (Callable): A function which evaluates the validity
                of the column(s) being tested.
            id (str, required): Each check mut have an id.
            warning (bool, optional): Boolean specifying whether to
                treat the check as a warning rather than an error.

        Raises:
            ValueError: Raised if `name` not supplied in kwargs and if id is not
            supplied or None.
        """

        self.id = id

        if "name" not in kwargs or id is None:
            raise ValueError("Each check must be assigned a `name` and an `id`.")

        # if warning==False treat check as an error check
        self.warning = warning

        super().__init__(check_fn=check_fn, *args, **kwargs)

    @classmethod
    def get_backend(cls, check_obj: Any) -> Type[BaseCheckBackend]:
        """Assume Pandas DataFrame and return PandasCheckBackend"""
        return PandasCheckBackend
