"""Custom subclass for warnings and errors. 

The class SBLCheck is a subclass of the standard Pandera Check class
that requires the `name` kwarg to be supplied. Errors and warnings are
distinguised based on the value of the warning attribute. It defaults
to false but can be set to True during init to indicate the validation
should be handled as a warning rather than an error. 

Examples:

    warning_check = SBLCheck(warning=True, name="Just a Warning")
    
    error_check_implied = SBLCheck(name="Error Check")
    error_check_explicit = SBLCheck(warning=False, name="Also an Error")
"""


from pandera import Check
from pandera.backends.pandas.checks import PandasCheckBackend


class SBLCheck(Check):
    """A custom Pandera.Check subclasss that requires a `name` be
    specificed. Additionally, an attribute named `warning` is added to
    the class to enable distinction between warnings and errors. The
    default value of warning is `False` which corresponds to an error.

    Don't use this class directly. Make use of the SBLErrorCheck and
    SBLWarningCheck subclasses below."""

    def __init__(self, warning=False, *args, **kwargs):
        """Custom init method that verifies the presence of `name` in
        kwargs creates a custom class attribute called `warning`. All
        other initializaiton is handled by the parent Check class.

        Args:
            warning (bool, optional): Boolean specifying whether to
                treat the check as a warning rather than an error.

        Raises:
            ValueError: Raised if `name` not supplied in kwargs.
        """

        if "name" not in kwargs:
            raise ValueError("Each check must be assigned a `name`.")

        # if warning==False treat check as an error check
        self.warning = warning

        super().__init__(*args, **kwargs)

    @classmethod
    def get_backend(cls, *args) -> PandasCheckBackend:
        """Assume Pandas DataFrame and return PandasCheckBackend"""
        return PandasCheckBackend
