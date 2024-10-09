import os
import boto3
import json
import logging
import polars as pl

from botocore.exceptions import ClientError
from fsspec import AbstractFileSystem, filesystem
from pydantic import PostgresDsn
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker, Session
from urllib import parse

from regtech_data_validator.checks import Severity
from regtech_data_validator.validator import validate_batch_csv, ValidationSchemaError
from regtech_data_validator.data_formatters import df_to_download, df_to_dicts
from regtech_data_validator.model import SubmissionDAO, SubmissionState, FindingDAO
from regtech_data_validator.validation_results import ValidationPhase

logger = logging.getLogger()
logger.setLevel("INFO")


def get_secret(secret_name):
    region_name = "us-east-1"

    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']
    return json.loads(secret)


def service_validate(bucket, file):
    file_paths = file.split("/")
    lei = file_paths[2]
    submission_id = file_paths[3].split(".csv")[0]

    filing_conn = None

    try:
        engine = get_filing_db_connection()
        filing_conn = sessionmaker(bind=engine)()
        submission = filing_conn.query(SubmissionDAO).filter_by(id=submission_id).first()
        submission.state = SubmissionState.VALIDATION_IN_PROGRESS
        filing_conn.commit()

        try:
            s3_path = f"{bucket}/{file}"
            print(f"Path to file: {s3_path}")
            fs: AbstractFileSystem = filesystem("filecache", target_protocol='s3', cache_storage='/tmp/files/')
            with fs.open(s3_path, "r") as f:
                final_state = SubmissionState.VALIDATION_SUCCESSFUL
                all_findings = []
                for findings, phase in validate_batch_csv(f.name, {'lei': lei}, batch_size=50000, batch_count=1):
                    findings = findings.with_columns(phase=pl.lit(phase), submission_id=pl.lit(submission_id))
                    if final_state != SubmissionState.VALIDATION_WITH_ERRORS:
                        final_state = (
                            SubmissionState.VALIDATION_WITH_ERRORS
                            if findings.filter(pl.col('validation_type') == 'Error').height > 0
                            else SubmissionState.VALIDATION_WITH_WARNINGS
                        )
                    findings.write_database(table_name="findings", connection=engine, if_table_exists="append")
                    all_findings.append(findings)

                submission.state = final_state
                build_validation_results(submission, filing_conn)
                filing_conn.commit()

                if all_findings:
                    final_df = pl.concat(all_findings, how="diagonal")
                    df_to_download(final_df, path=f"s3://{bucket}/{file_paths[0]}/{file_paths[1]}/{file_paths[2]}/{submission_id}_report.csv")

        except ValidationSchemaError:
            logger.exception("The file is malformed.")
            submission = filing_conn.query(SubmissionDAO).filter_by(id=submission_id).first()
            submission.state = SubmissionState.SUBMISSION_UPLOAD_MALFORMED
            filing_conn.commit()

        except Exception:
            logger.exception("Error processing submission file.")
            if filing_conn:
                submission = filing_conn.query(SubmissionDAO).filter_by(id=submission_id).first()
                submission.state = SubmissionState.VALIDATION_ERROR
                filing_conn.commit()

    except Exception:
        logger.exception("Error processing submission file.")
        if filing_conn:
            submission = filing_conn.query(SubmissionDAO).filter_by(id=submission_id).first()
            submission.state = SubmissionState.VALIDATION_ERROR
            filing_conn.commit()


def get_filing_db_connection():
    secret = get_secret(os.getenv("DB_SECRET", None))
    postgres_dsn = PostgresDsn.build(
        scheme="postgresql+psycopg2",
        username=secret['username'],
        password=parse.quote(secret['password'], safe=""),
        host=secret['host'],
        path=secret['database'],
    )
    conn_str = str(postgres_dsn)
    return create_engine(conn_str)


def build_validation_results(submission: SubmissionDAO, session: Session):
    phase = get_validation_phase(session, submission.id)

    findings = get_findings(session, submission.id, 200)

    data = []
    for row in findings:
        finding_dict = row.__dict__.copy()
        finding_dict.pop("_sa_instance_state", None)
        data.append(finding_dict)

    val_json = df_to_dicts(pl.DataFrame(data), max_group_size=200)
    if phase == ValidationPhase.SYNTACTICAL:
        single_errors = (get_field_counts(session, submission.id, Severity.ERROR, "single-field"),)
        val_res = {
            "syntax_errors": {
                "single_field_count": single_errors,
                "multi_field_count": 0,  # this will always be zero for syntax errors
                "register_count": 0,  # this will always be zero for syntax errors
                "total_count": single_errors,
                "details": val_json,
            }
        }
    else:
        errors_list = [e for e in val_json if e["validation"]["severity"] == Severity.ERROR]
        warnings_list = [w for w in val_json if w["validation"]["severity"] == Severity.WARNING]
        val_res = {
            "syntax_errors": {
                "single_field_count": 0,
                "multi_field_count": 0,
                "register_count": 0,
                "total_count": 0,
                "details": [],
            },
            "logic_errors": {
                "single_field_count": get_field_counts(session, submission.id, Severity.ERROR, "single-field"),
                "multi_field_count": get_field_counts(session, submission.id, Severity.ERROR, "multi-field"),
                "register_count": get_field_counts(session, submission.id, Severity.ERROR, "register"),
                "total_count": get_field_counts(session, submission.id, Severity.ERROR),
                "details": errors_list,
            },
            "logic_warnings": {
                "single_field_count": get_field_counts(session, submission.id, Severity.WARNING, "single-field"),
                "multi_field_count": get_field_counts(session, submission.id, Severity.WARNING, "multi-field"),
                "register_count": 0,
                "total_count": get_field_counts(session, submission.id, Severity.WARNING),
                "details": warnings_list,
            },
        }

    submission.validation_results = val_res


def get_validation_phase(session: Session, submission_id: int):
    phase = session.execute(select(FindingDAO.phase).filter(FindingDAO.submission_id == submission_id))
    return phase.scalar()


def get_field_counts(session: Session, submission_id: int, severity: Severity, scope: str = None):
    query = session.query(func.count(FindingDAO.id)).filter(
        FindingDAO.submission_id == submission_id,
        FindingDAO.validation_type == severity,
    )
    if scope:
        query.filter(FindingDAO.scope == scope)

    return session.scalar(query)


def get_findings(session, submission_id, max_group_size):
    row_number = func.row_number().over(partition_by=FindingDAO.validation_id, order_by=FindingDAO.id).label('row_num')

    subquery = (session.query(FindingDAO.id).add_columns(row_number).filter(FindingDAO.submission_id == submission_id).subquery())
    filtered_subquery = (session.query(subquery.c.id).filter(subquery.c.row_num <= max_group_size))
    query = session.query(FindingDAO).filter(FindingDAO.id.in_(filtered_subquery))
    findings = session.scalars(query).all()
    return findings
