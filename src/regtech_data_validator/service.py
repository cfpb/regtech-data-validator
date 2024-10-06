import os
import boto3
import json
import logging
import polars as pl

from botocore import ClientError
from fsspec import AbstractFileSystem, filesystem
from pydantic import PostgresDsn
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib import parse

from regtech_data_validator.validator import validate_batch_csv, ValidationSchemaError
from regtech_data_validator.data_formatters import df_to_download
from regtech_data_validator.model import SubmissionDAO, SubmissionState


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
    lei = file.split("/")[2]
    submission_id = file.split("/")[3].split(".csv")[0]

    filing_conn = None

    try:
        engine = get_filing_db_connection()
        filing_conn = sessionmaker(bind=engine)()
        submission = filing_conn.query(SubmissionDAO).filter_by(id=submission_id).first()
        submission.state = SubmissionState.VALIDATION_IN_PROGRESS
        filing_conn.commit()

        try:
            s3_path = f"{bucket}/{file}"

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
                filing_conn.commit()

                if all_findings:
                    final_df = pl.concat(all_findings, how="diagonal")
                    df_to_download(final_df, path=f"{bucket}/{submission_id}_report.csv")

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
