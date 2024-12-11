from collections.abc import Generator
from datetime import datetime
from typing import Callable

import pytest
from sqlmodel import Session

from petshop.db import engine
from petshop.importer.import_downloads import get_package_ids_by_name
from petshop.models import Classifier, Download, Package


@pytest.fixture
def session() -> Generator[Session, None, None]:
    with Session(engine()) as session:
        yield session


@pytest.fixture
def create_classifier(session: Session) -> Callable[[str], Classifier]:
    def create_classifier(name: str) -> Classifier:
        classifier = Classifier(name=name)
        session.add(classifier)
        session.commit()
        session.refresh(classifier)
        # Classifier(name="Development Status :: 5 - Production/Stable"),
        # Classifier(name="Operating System :: POSIX :: Linux"),

        return classifier

    return create_classifier


@pytest.fixture
def create_package(
    session: Session,
) -> Callable[[str, datetime, list[Classifier]], Package]:
    def create_package(
        name: str, upload_time: datetime, classifiers: list[Classifier] = []
    ) -> Package:
        package = Package(
            name=name,
            upload_time=upload_time,
            metadata_version="METADATA_VERSION",
            version="VERSION",
            summary="SUMMARY",
            description="DESCRIPTION",
            description_content_type="DESCRIPTION_CONTENT_TYPE",
            author="AUTHOR",
            author_email="AUTHOR_EMAIL",
            maintainer="MAINTAINER",
            maintainer_email="MAINTAINER_EMAIL",
            license="LICENSE",
            keywords="KEYWORDS",
            classifiers=classifiers,
            platform=["PLATFORM"],
            home_page="HOME_PAGE",
            download_url="DOWNLOAD_URL",
            requires_python="REQUIRES_PYTHON",
            requires=["REQUIRED A", "REQUIRED B"],
            provides=["PROVIDES A", "PROVIDES B"],
            obsoletes=["OBSOLETES A", "OBSOLETES B"],
            requires_dist=["REQUIRES_DIST A"],
            provides_dist=["PROVIDES_DIST A"],
            obsoletes_dist=["OBSOLETES_DIST A"],
            requires_external=["REQUIRES_EXTERNAL A"],
            project_urls=["PROJECT_URL 1"],
            uploaded_via="UPLOADED_VIA",
            filename="FILENAME",
            size=1000,
            path="PATH",
            python_version="PYTHON_VERSION",
            packagetype="PACKAGETYPE",
            comment_text="COMMENT_TEXT",
            has_signature=True,
            md5_digest="MD5_DIGEST",
            sha256_digest="SHA256_DIGEST",
            blake2_256_digest="BLAKE2_256_DIGEST",
            license_expression="LICENSE_EXPRESSION",
            license_files=["LICENSE_FILE"],
        )
        session.add(package)
        session.commit()
        session.refresh(package)
        return package

    return create_package


@pytest.fixture
def create_download(
    session: Session,
) -> Callable[[int, datetime, datetime, int], Download]:
    def create_download(
        package_id: int, month: datetime, imported_at: datetime, downloads: int = 1234
    ) -> Download:
        download = Download(
            package_id=package_id,
            month=month,
            imported_at=imported_at,
            downloads=downloads,
        )
        session.add(download)
        session.commit()
        session.refresh(download)
        return download

    return create_download


def test_get_package_ids_by_name(
    session: Session, create_package: Callable[[str, datetime], Package]
):
    package_a = create_package("PACKAGE A", datetime(2024, 12, 1))
    package_b = create_package("PACKAGE B", datetime(2024, 12, 2))
    package_c = create_package("PACKAGE C", datetime(2024, 12, 3))

    result = get_package_ids_by_name(session)

    assert result == {
        "PACKAGE A": package_a.id,
        "PACKAGE B": package_b.id,
        "PACKAGE C": package_c.id,
    }


# def test_get_incomplete_months(
#     create_download: Callable[[int, datetime, datetime, int], Package],
# ):
#     result = get_incomplete_months()
