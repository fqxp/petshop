# pyright: reportUnknownVariableType=false,reportUnknownMemberType=false,reportUnknownArgumentType=false
import datetime
from datetime import datetime

from sqlalchemy.orm import column_property, declared_attr
from sqlmodel import ARRAY, Column, Field, Relationship, SQLModel, String, func


class Base(SQLModel): ...


class ClassifierPackageLink(Base, table=True):
    classifier_id: int | None = Field(
        default=None, foreign_key="classifier.id", primary_key=True
    )
    package_id: int | None = Field(
        default=None, foreign_key="package.id", primary_key=True
    )


class Classifier(Base, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    packages: list["Package"] = Relationship(
        back_populates="classifiers", link_model=ClassifierPackageLink
    )


class Package(Base, table=True):
    id: int | None = Field(default=None, primary_key=True)
    metadata_version: str | None
    name: str = Field(index=True)
    version: str
    summary: str | None
    description: str | None
    description_content_type: str | None
    author: str | None
    author_email: str | None
    maintainer: str | None
    maintainer_email: str | None
    license: str | None
    keywords: str | None
    classifiers_array: list[str] | None = Field(sa_column=Column(ARRAY(String)))
    platform: list[str] | None = Field(sa_column=Column(ARRAY(String)))
    home_page: str | None
    download_url: str | None
    requires_python: str | None
    requires: list[str] | None = Field(sa_column=Column(ARRAY(String)))
    provides: list[str] | None = Field(sa_column=Column(ARRAY(String)))
    obsoletes: list[str] | None = Field(sa_column=Column(ARRAY(String)))
    requires_dist: list[str] | None = Field(sa_column=Column(ARRAY(String)))
    provides_dist: list[str] | None = Field(sa_column=Column(ARRAY(String)))
    obsoletes_dist: list[str] | None = Field(sa_column=Column(ARRAY(String)))
    requires_external: list[str] | None = Field(sa_column=Column(ARRAY(String)))
    project_urls: list[str] | None = Field(sa_column=Column(ARRAY(String)))
    uploaded_via: str | None
    upload_time: datetime.datetime
    filename: str | None
    size: int | None
    path: str | None
    python_version: str | None
    packagetype: str | None
    comment_text: str | None
    has_signature: bool | None
    md5_digest: str
    sha256_digest: str | None
    blake2_256_digest: str | None
    license_expression: str | None
    license_files: list[str] | None = Field(sa_column=Column(ARRAY(String)))

    classifiers: list["Classifier"] = Relationship(
        back_populates="packages", link_model=ClassifierPackageLink
    )
class Download(Base, table=True):
    id: int | None = Field(default=None, primary_key=True)
    imported_at: datetime
    package_id: int = Field(foreign_key="package.id")
    package: Package = Relationship(back_populates="downloads")
    month: datetime
    downloads: int
