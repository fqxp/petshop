# pyright: reportUnknownVariableType=false,reportUnknownMemberType=false,reportUnknownArgumentType=false
import logging
import os
import time
import uuid
from collections.abc import Generator
from datetime import datetime, timezone
from typing import cast

from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from google.cloud.bigquery import Client, QueryJobConfig, Row, ScalarQueryParameter
from google.cloud.bigquery.table import RowIterator
from sqlalchemy import Engine
from sqlmodel import TIMESTAMP, Integer, Session, String, column, select, text

from petshop.db import engine
from petshop.importer.utils import split_month
from petshop.models import Download, Package

MIN_DATE = datetime(2016, 1, 1, 0, 0, 0)

logger = logging.getLogger(__name__)


def get_package_ids_by_name(session: Session) -> dict[str, int]:
    statement = select(Package.name, Package.id)
    packages = session.exec(statement).all()

    return {package[0]: cast(int, package[1]) for package in packages}


def get_downloads_by_package_id(
    session: Session, month: datetime
) -> dict[int, Download]:
    downloads = session.exec(select(Download).where(Download.month == month))

    return {download.package_id: download for download in downloads}


def get_downloads_paged(client: Client, year: int, month: int) -> Generator[Row, None]:
    # pypi.file_downloads is partitioned by day on field timestamp
    # therefore it’s cheaper to split by month than by other means.
    month_splits = split_month(year, month, number_of_splits=5)

    for start_time, end_time in month_splits:
        rows = get_downloads(client, start_time, end_time)

        for row in rows:
            yield row


def get_downloads(
    client: Client,
    start_time: datetime,
    end_time: datetime,
) -> RowIterator:
    query = """
        SELECT
          project as package_name,
          COUNT(project) AS downloads
        FROM `bigquery-public-data.pypi.file_downloads`
        WHERE timestamp >= @timestamp_start
          AND timestamp < @timestamp_end
        GROUP BY project
    """
    job_id = f"import-downloads-{uuid.uuid4()}"
    logger.info(
        f"bigquery job {job_id}: requesting downloads from {start_time} to {end_time}"
    )

    job_config = QueryJobConfig(
        maximum_bytes_billed=1024 * 1024 * 1024 * 1024 - 1,  # < 1 TB
        query_parameters=[
            ScalarQueryParameter(
                "timestamp_start", "TIMESTAMP", start_time.isoformat()
            ),
            ScalarQueryParameter("timestamp_end", "TIMESTAMP", end_time.isoformat()),
        ],
    )
    query_job = client.query(query, job_config=job_config, job_id=job_id)
    rows = query_job.result()

    logger.info(
        f"bigquery job {rows.job_id}: resultset contains {rows.total_rows} rows"
    )

    return rows


def update_downloads(
    bigquery_client: Client,
    month: datetime,
    sqlmodel_engine: Engine,
):
    import_time = datetime.now(timezone.utc)

    logger.info("Importing PyPI downloads per package from Google BigQuery")
    download_rows = get_downloads_paged(bigquery_client, month.year, month.month)

    with Session(sqlmodel_engine) as session:
        logger.debug("loading package info")
        package_ids_by_name = get_package_ids_by_name(session)

        logger.debug("loading download info")
        downloads_by_package_id = get_downloads_by_package_id(session, month)
        # reset counts because we’re always updating the whole month
        for _, download in downloads_by_package_id.items():
            download.downloads = 0

        count_processed = 0
        count_created = 0
        count_updated = 0
        count_not_found = 0

        for count_processed, row in enumerate(download_rows):
            package_id = package_ids_by_name.get(row.package_name)
            if not package_id:
                logger.debug(f"package {row.package_name} does not exist, skipping")
                count_not_found += 1
                continue

            download = downloads_by_package_id.get(package_id)

            if download:
                if download.downloads == 0:
                    count_updated += 1
                download.imported_at = import_time
                download.downloads += row.downloads
            else:
                count_created += 1
                download = Download(
                    imported_at=import_time,
                    package_id=package_id,
                    month=month,
                    downloads=row.downloads,
                )
                downloads_by_package_id[package_id] = download

        session.add_all(downloads_by_package_id.values())
        session.commit()

        logger.info(
            f"🟢 processed {count_processed} downloads: {count_created} created, {count_updated} updated, {count_not_found} packages not found"
        )


def import_downloads(month: datetime):
    load_dotenv()  # pyright: ignore[reportUnusedCallResult]

    logger.info(f"Importing downloads for {month.isoformat()}")

    google_project = os.environ["GOOGLE_CLOUD_PROJECT"]
    bigquery_client = Client(project=google_project)

    start_time = time.perf_counter()
    update_downloads(bigquery_client, month, engine())
    end_time = time.perf_counter()

    logging.info(f"importing took {end_time-start_time} seconds")


def get_incomplete_months() -> list[datetime]:
    statement = text(
        """
            SELECT
              month
            FROM download
            WHERE imported_at < month + '1 month'
            GROUP BY month
        """
    ).columns(
        column("project", String),
        column("month", TIMESTAMP),
        column("downloads", Integer),
    )

    with Session(engine()) as session:
        rows = session.exec(statement).all()  # pyright: ignore[reportArgumentType,reportCallIssue]

        return [row for row in rows]
