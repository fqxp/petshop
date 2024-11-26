# pyright: reportUnknownVariableType=false,reportUnknownMemberType=false,reportUnknownArgumentType=false
import datetime
import logging
import os
from collections.abc import Iterator

from dotenv import load_dotenv
from google.cloud.bigquery import Client, QueryJobConfig, ScalarQueryParameter
from sqlmodel import Session, create_engine, select

from petshop.models import Package

# roughly 5 years before project start - do not change light-handedly!
PACKAGE_UPLOAD_TIME_AFTER = datetime.datetime(2020, 1, 1, 0, 0, 0)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_packages(
    client: Client, upload_time_after: datetime.datetime
) -> Iterator[Package]:
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
        MAX_BY(classifiers, upload_time) AS classifiers,
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

    for row in rows:
        package = Package(**{key: value for key, value in row.items()})
        # package = Package(
        # metadata_version=row.metadata_version,
        # name=row.name,
        # version=row.version,
        # summary=row.summary,
        # description=row.description,
        # description_content_type=row.description_content_type,
        # author=row.author,
        # author_email=row.author_email,
        # maintainer=row.maintainer,
        # maintainer_email=row.maintainer_email,
        # license=row.license,
        # keywords=row.keywords or [],
        # classifiers=row.classifiers or [],
        # platform=row.platform or [],
        # home_page=row.home_page,
        # download_url=row.download_url,
        # requires_python=row.requires_python,
        # requires=row.requires or [],
        # provides=row.provides or [],
        # obsoletes=row.obsoletes or [],
        # requires_dist=row.requires_dist or [],
        # provides_dist=row.provides_dist or [],
        # obsoletes_dist=row.obsoletes_dist or [],
        # requires_external=row.requires_external or [],
        # project_urls=row.project_urls or [],
        # uploaded_via=row.uploaded_via,
        # upload_time=row.upload_time,
        # filename=row.filename,
        # size=row.size,
        # path=row.path,
        # python_version=row.python_version,
        # packagetype=row.packagetype,
        # comment_text=row.comment_text,
        # has_signature=row.has_signature,
        # md5_digest=row.md5_digest,
        # sha256_digest=row.sha256_digest,
        # blake2_256_digest=row.blake2_256_digest,
        # license_expression=row.license_expression,
        # license_files=row.license_files or [],
        # )
        yield package


def get_latest_update_time(
    session: Session, default: datetime.datetime
) -> datetime.datetime:
    statement = select(Package.upload_time).order_by(Package.upload_time.desc())  # pyright: ignore[reportAttributeAccessIssue]
    upload_time = session.exec(statement).first()

    if upload_time is None:
        return default

    return upload_time


def main():
    load_dotenv()  # pyright: ignore[reportUnusedCallResult]
    sqlmodel_engine = create_engine(os.environ["DATABASE_URL"])

    google_project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    bigquery_client = Client(project=google_project)

    with Session(sqlmodel_engine) as session:
        upload_time_after = get_latest_update_time(session, PACKAGE_UPLOAD_TIME_AFTER)
        logger.info(
            f"Importing PyPI packages from Google BigQuery (google project: {google_project}, starting: {upload_time_after.isoformat()})"
        )

        packages_iterator = get_packages(bigquery_client, upload_time_after)
        count = 0
        commit_every_rows = 5000
        for package in packages_iterator:
            print(f"{package.name} {package.version}: {package.upload_time}")

            session.add(package)

            if count >= commit_every_rows:
                print(f"committing {commit_every_rows} rows")
                session.commit()
                count = 0
            else:
                count = count + 1

        session.commit()
