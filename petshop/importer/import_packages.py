# pyright: reportUnknownVariableType=false,reportUnknownMemberType=false,reportUnknownArgumentType=false
import datetime
import logging
import os
from typing import cast

from google.cloud.bigquery import Client, QueryJobConfig, ScalarQueryParameter
from google.cloud.bigquery.table import RowIterator
from sqlalchemy import Engine
from sqlmodel import Session, select

from petshop.db import engine
from petshop.models import Classifier, Package

# roughly 5 years before project start - do not change light-handedly!
PACKAGE_UPLOAD_TIME_AFTER = datetime.datetime(2020, 1, 1, 0, 0, 0)

logger = logging.getLogger(__name__)


def get_packages(client: Client, upload_time_after: datetime.datetime) -> RowIterator:
    query = """
    SELECT
        name,
        MAX(upload_time) AS upload_time,
        MAX_BY(metadata_version, upload_time) AS metadata_version,
        MAX_BY(version, upload_time) AS version,
        MAX_BY(summary, upload_time) AS summary,
        MAX_BY(description, upload_time) AS description,
        MAX_BY(description_content_type, upload_time) AS description_content_type,
        MAX_BY(author, upload_time) AS author,
        MAX_BY(author_email, upload_time) AS author_email,
        MAX_BY(maintainer, upload_time) AS maintainer,
        MAX_BY(maintainer_email, upload_time) AS maintainer_email,
        MAX_BY(license, upload_time) AS license,
        MAX_BY(keywords, upload_time) AS keywords,
        MAX_BY(classifiers, upload_time) AS classifiers_array,
        MAX_BY(platform, upload_time) AS platform,
        MAX_BY(home_page, upload_time) AS home_page,
        MAX_BY(download_url, upload_time) AS download_url,
        MAX_BY(requires_python, upload_time) AS requires_python,
        MAX_BY(requires, upload_time) AS requires,
        MAX_BY(provides, upload_time) AS provides,
        MAX_BY(obsoletes, upload_time) AS obsoletes,
        MAX_BY(requires_dist, upload_time) AS requires_dist,
        MAX_BY(provides_dist, upload_time) AS provides_dist,
        MAX_BY(obsoletes_dist, upload_time) AS obsoletes_dist,
        MAX_BY(requires_external, upload_time) AS requires_external,
        MAX_BY(project_urls, upload_time) AS project_urls,
        MAX_BY(uploaded_via, upload_time) AS uploaded_via,
        MAX_BY(filename, upload_time) AS filename,
        MAX_BY(size, upload_time) AS size,
        MAX_BY(path, upload_time) AS path,
        MAX_BY(python_version, upload_time) AS python_version,
        MAX_BY(packagetype, upload_time) AS packagetype,
        MAX_BY(comment_text, upload_time) AS comment_text,
        MAX_BY(has_signature, upload_time) AS has_signature,
        MAX_BY(md5_digest, upload_time) AS md5_digest,
        MAX_BY(sha256_digest, upload_time) AS sha256_digest,
        MAX_BY(blake2_256_digest, upload_time) AS blake2_256_digest,
        MAX_BY(license_expression, upload_time) AS license_expression,
        MAX_BY(license_files, upload_time) AS license_files
    FROM `bigquery-public-data.pypi.distribution_metadata`
    WHERE upload_time >= @upload_time_after
    GROUP BY name
    ORDER BY upload_time ASC
    """
    job_config = QueryJobConfig(
        query_parameters=[
            ScalarQueryParameter("upload_time_after", "TIMESTAMP", upload_time_after),
        ]
    )
    query_job = client.query(query, job_config=job_config)
    rows = query_job.result()

    logger.info(f"Google BigQuery query resultset contains {rows.total_rows} rows")

    return rows


def get_latest_update_time(sqlmodel_engine: Engine) -> datetime.datetime | None:
    with Session(sqlmodel_engine) as session:
        statement = select(Package.upload_time).order_by(Package.upload_time.desc())  # pyright: ignore[reportAttributeAccessIssue]
        upload_time = session.exec(statement).first()

        return upload_time


def update_packages(
    sqlmodel_engine: Engine, package_rows: RowIterator, commit_every_nth_row: int = 5000
):
    with Session(sqlmodel_engine) as session:
        classifiers_by_name = {
            classifier.name: classifier
            for classifier in session.exec(select(Classifier))
        }

        keys = [cast(str, field.name) for field in package_rows.schema]

        for index, row in enumerate(package_rows):
            logger.debug(f"Processing {row.name} {row.version} ({row.upload_time})")

            statement = select(Package).where(Package.name == row.name)
            package = session.exec(statement).first()

            if package:
                for key in keys:
                    setattr(package, key, getattr(row, key))
            else:
                package = Package(**{key: value for key, value in row.items()})

            package.classifiers = [
                classifiers_by_name[classifier_name]
                for classifier_name in row.classifiers_array
            ]

            session.add(package)

            if index > 0 and index % commit_every_nth_row == 0:
                logger.info(f"🟢 committing {commit_every_nth_row} rows")
                session.commit()

        logger.info("🟢 committing leftover rows")
        session.commit()


def import_packages():
    sqlmodel_engine = engine()

    google_project = os.environ["GOOGLE_CLOUD_PROJECT"]
    bigquery_client = Client(project=google_project)

    upload_time_after = (
        get_latest_update_time(sqlmodel_engine) or PACKAGE_UPLOAD_TIME_AFTER
    )
    logger.info(
        f"Importing PyPI packages from Google BigQuery (project: {google_project}, starting: {upload_time_after.isoformat()})"
    )

    package_rows = get_packages(bigquery_client, upload_time_after)
    update_packages(sqlmodel_engine, package_rows)
