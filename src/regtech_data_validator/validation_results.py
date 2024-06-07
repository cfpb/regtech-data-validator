import pandas as pd

from dataclasses import dataclass
from enum import StrEnum


class ValidationPhase(StrEnum):
    SYNTACTICAL = "Syntactical"
    LOGICAL = "Logical"


@dataclass(frozen=True)
class Counts(object):
    single_field_count: int = 0
    multi_field_count: int = 0
    register_count: int = 0
    total_count: int = 0


@dataclass(frozen=True)
class ValidationResults(object):
    error_counts: Counts
    warning_counts: Counts
    is_valid: bool
    findings: pd.DataFrame
    phase: ValidationPhase
