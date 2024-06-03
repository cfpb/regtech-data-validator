import pandas as pd

from dataclasses import dataclass
from enum import StrEnum


class ValidationPhase(StrEnum):
    SYNTACTICAL = "Syntactical"
    LOGICAL = "Logical"


@dataclass(frozen=True)
class ValidationResults(object):
    single_field_count: int
    multi_field_count: int
    register_count: int
    is_valid: bool
    findings: pd.DataFrame
    phase: ValidationPhase
