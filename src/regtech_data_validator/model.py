from enum import Enum
from datetime import datetime
from typing import Any
from sqlalchemy import Enum as SAEnum
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.types import JSON


class Base(AsyncAttrs, DeclarativeBase):
    pass


class SubmissionState(str, Enum):
    SUBMISSION_ACCEPTED = "SUBMISSION_ACCEPTED"
    SUBMISSION_STARTED = "SUBMISSION_STARTED"
    SUBMISSION_UPLOAD_MALFORMED = "SUBMISSION_UPLOAD_MALFORMED"
    SUBMISSION_UPLOADED = "SUBMISSION_UPLOADED"
    UPLOAD_FAILED = "UPLOAD_FAILED"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    VALIDATION_EXPIRED = "VALIDATION_EXPIRED"
    VALIDATION_IN_PROGRESS = "VALIDATION_IN_PROGRESS"
    VALIDATION_SUCCESSFUL = "VALIDATION_SUCCESSFUL"
    VALIDATION_WITH_ERRORS = "VALIDATION_WITH_ERRORS"
    VALIDATION_WITH_WARNINGS = "VALIDATION_WITH_WARNINGS"


class SubmissionDAO(Base):
    __tablename__ = "submission"
    id: Mapped[int] = mapped_column(index=True, primary_key=True, autoincrement=True)
    filing: Mapped[int]
    submitter_id: Mapped[int]
    accepter_id: Mapped[int]
    state: Mapped[SubmissionState] = mapped_column(SAEnum(SubmissionState))
    validation_ruleset_version: Mapped[str] = mapped_column(nullable=True)
    validation_results: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)
    submission_time: Mapped[datetime] = mapped_column(server_default=func.now())
    filename: Mapped[str]
    total_records: Mapped[int] = mapped_column(nullable=True)

    def __str__(self):
        return f"Submission ID: {self.id}, State: {self.state}, Ruleset: {self.validation_ruleset_version}, Filing Period: {self.filing}, Submission: {self.submission_time}"


class FindingDAO(Base):
    __tablename__ = "findings"
    validation_type: Mapped[str],
    validation_id: Mapped[str],
    validation_name: Mapped[str],
    row: Mapped[int], 
    unique_identifier: Mapped[str],
    fig_link: Mapped[str],
    validation_description: Mapped[str],
    scope: Mapped[str],
    phase: Mapped[str],
    submission_id: Mapped[int],
    field_1: Mapped[str],
    field_2: Mapped[str],
    field_3: Mapped[str],
    field_4: Mapped[str],
    field_5: Mapped[str],
    field_6: Mapped[str],
    field_7: Mapped[str],
    field_8: Mapped[str],
    field_9: Mapped[str],
    field_10: Mapped[str],
    field_11: Mapped[str],
    field_12: Mapped[str],
    field_13: Mapped[str],
    value_1: Mapped[str],
    value_2: Mapped[str],
    value_3: Mapped[str],
    value_4: Mapped[str],
    value_5: Mapped[str],
    value_6: Mapped[str],
    value_7: Mapped[str],
    value_8: Mapped[str],
    value_9: Mapped[str],
    value_10: Mapped[str],
    value_11: Mapped[str],
    value_12: Mapped[str],
    value_13: Mapped[str]

