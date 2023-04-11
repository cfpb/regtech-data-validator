"""A sublcass of Pandera.Check that outputs errors in a more meaninful
manner."""

from typing import Optional, Union

import pandas as pd
from pandera import Check
from pandera.api.base.checks import CheckResult
from pandera.backends.pandas.checks import PandasCheckBackend


class VerboseCheck(Check):
    def __init__(self, *args, **kwargs):
        if "name" not in kwargs:
            raise ValueError("Each check must be assigned a `name`.")
        super().__init__(*args, **kwargs)

    def __call__(
        self,
        check_obj: Union[pd.DataFrame, pd.Series],
        column: Optional[str] = None,
    ) -> CheckResult:
        # pylint: disable=too-many-branches
        """Validate pandas DataFrame or Series.

        This method is overrides the default Check.__call__ method. This
        implementation captures the output of the validation and prints
        it to the terminal. Eventually we'll do something with it. Just
        a POC at this phase.

        :param check_obj: pandas DataFrame of Series to validate.
        :param column: for dataframe checks, apply the check function to this
            column.
        :returns: CheckResult tuple containing:

            ``check_output``: boolean scalar, ``Series`` or ``DataFrame``
            indicating which elements passed the check.

            ``check_passed``: boolean scalar that indicating whether the check
            passed overall.

            ``checked_object``: the checked object itself. Depending on the
            options provided to the ``Check``, this will be a pandas Series,
            DataFrame, or if the ``groupby`` option is specified, a
            ``Dict[str, Series]`` or ``Dict[str, DataFrame]`` where the keys
            are distinct groups.

            ``failure_cases``: subset of the check_object that failed.
        """
        print("______________________________________________")
        print(f"Running check `{self.name}` on column `{column}`. Output:")
        backend = self.get_backend(check_obj)(self)
        check_result_output = backend(check_obj, column)
        print(f"{check_result_output.check_output}")
        print("")
        return check_result_output

    @classmethod
    def get_backend(cls, check_obj: pd.DataFrame) -> PandasCheckBackend:
        """Assume Pandas DataFrame and return PandasCheckBackend"""
        return PandasCheckBackend
