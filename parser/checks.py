"""Custom subclasses for warnings and errors. 

The class SBLBaseCheck is a subclass of the standard Pandera Check class
that requires the `name` knwarg to be supplied. There are two additional
subclasses created from SBLBaseCheck called SBLErrorCheck and 
SBLWarningCheck. These contain no additional functionality and serve 
only to be explicit and facilitate calls to `isinstance` so we can 
handle errors and warnings appropriately."""


from pandera import Check
from pandera.backends.pandas.checks import PandasCheckBackend


class SBLBaseCheck(Check):
    """A custom Pandera.Check subclasss that requires a `name`.

    Don't use this class directly. Make use of the SBLErrorCheck and
    SBLWarningCheck subclasses below."""

    # TODO: ARE THERE OTHER FIELDS THAT WE WISH TO REQUIRE HERE?

    def __init__(self, *args, **kwargs):
        if "name" not in kwargs:
            raise ValueError("Each check must be assigned a `name`.")
        super().__init__(*args, **kwargs)

    @classmethod
    def get_backend(cls, *args) -> PandasCheckBackend:
        """Assume Pandas DataFrame and return PandasCheckBackend"""
        return PandasCheckBackend


#! FIGURE OUT: DO WE WANT TO HAVE TWO CHECK CLASSES OR A SINGLE CHECK
#!  CLASS WITH A `warning=True/False` FLAG?


class SBLErrorCheck(SBLBaseCheck):
    """For validations that should be interpreted as errors."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SBLErrorCheck(SBLBaseCheck):
    """For validations that should be interpreted as warnings."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
