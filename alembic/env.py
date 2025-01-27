import json
import os
import re
from collections.abc import Generator, Iterable, Iterator
from logging.config import fileConfig
from typing import Any, cast

from alembic_utils.pg_materialized_view import PGMaterializedView
from alembic_utils.replaceable_entity import register_entities
from dotenv import load_dotenv
from sqlalchemy import Connection, Select, engine_from_config, pool, text
from sqlalchemy.schema import SchemaItem
from sqlmodel import Table

import petshop.models
from alembic import context, op

env_file = ".env-test" if os.environ.get("RUN_ENV") == "test" else ".env"
load_dotenv(env_file)  # pyright:ignore[reportUnusedCallResult]

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = petshop.models.Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def normalize_sql(sql: str) -> str:
    return re.sub(r"[ \n]+", " ", sql.strip())


def modified_materialized_views(connection: Connection) -> Iterator[Table]:
    views: list[Table] = [
        cast(Table, mapper.persist_selectable)
        for mapper in petshop.models.ViewBase._sa_registry.mappers  # pyright: ignore[reportPrivateUsage]
    ]

    if not views:
        return

    query = text(
        """
        SELECT matviewname, definition
        FROM pg_catalog.pg_matviews
        """
    )
    existent_views = {
        view_name: statement for view_name, statement in connection.execute(query).all()
    }

    print(json.dumps(existent_views))

    for view in petshop.models.ViewBase.__all_views__():
        view_table = cast(Table, cast(object, view.__table__))
        view_query = normalize_sql(str(view.__view_query__))

        print(f"query = `{view_query}`")
        if view_table.name not in existent_views:
            yield view_table
            continue

        existent_view_query = normalize_sql(str(existent_views[view_table.name]))
        print(f"exery = `{existent_view_query}`")
        if view_query != existent_view_query:
            yield view_table


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

        print(list(modified_materialized_views(connection)))


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
