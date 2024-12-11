import os

from sqlalchemy import Engine
from sqlmodel import create_engine

_engine = None


def engine() -> Engine:
    global _engine

    if not _engine:
        _engine = create_engine(os.environ["DATABASE_URL"], echo=True)

    return _engine
