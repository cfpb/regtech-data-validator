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

#model for finding table
class FindingDAO(Base):
    __tablename__ = "findings"
    id: Mapped[int] = mapped_column(index=True, primary_key=True, autoincrement=True)
    validation_type: Mapped[str]
    validation_id: Mapped[str]
    row: Mapped[int]
    unique_identifier: Mapped[str]
    scope: Mapped[str]
    phase: Mapped[str]
    submission_id: Mapped[int]
    field_1: Mapped[str]
    field_2: Mapped[str] = mapped_column(nullable=True)
    field_3: Mapped[str] = mapped_column(nullable=True)
    field_4: Mapped[str] = mapped_column(nullable=True)
    field_5: Mapped[str] = mapped_column(nullable=True)
    field_6: Mapped[str] = mapped_column(nullable=True)
    field_7: Mapped[str] = mapped_column(nullable=True)
    field_8: Mapped[str] = mapped_column(nullable=True)
    field_9: Mapped[str] = mapped_column(nullable=True)
    field_10: Mapped[str] = mapped_column(nullable=True)
    field_11: Mapped[str] = mapped_column(nullable=True)
    field_12: Mapped[str] = mapped_column(nullable=True)
    field_13: Mapped[str] = mapped_column(nullable=True)
    value_1: Mapped[str]
    value_2: Mapped[str] = mapped_column(nullable=True)
    value_3: Mapped[str] = mapped_column(nullable=True)
    value_4: Mapped[str] = mapped_column(nullable=True)
    value_5: Mapped[str] = mapped_column(nullable=True)
    value_6: Mapped[str] = mapped_column(nullable=True)
    value_7: Mapped[str] = mapped_column(nullable=True)
    value_8: Mapped[str] = mapped_column(nullable=True)
    value_9: Mapped[str] = mapped_column(nullable=True)
    value_10: Mapped[str] = mapped_column(nullable=True)
    value_11: Mapped[str] = mapped_column(nullable=True)
    value_12: Mapped[str] = mapped_column(nullable=True)
    value_13: Mapped[str] = mapped_column(nullable=True)
