import logging
from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, col, desc, func, select

from petshop.db import engine
from petshop.models import Download, Package, PackagePublic

FRONTEND_ROOT = Path(__file__).parent.parent.parent.resolve().joinpath("frontend/dist")
RESULTS_PER_PAGE = 25

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    load_dotenv()  # pyright: ignore[reportUnusedCallResult]
    yield


def session() -> Generator[Session, None]:
    with Session(engine()) as session:
        yield session


app = FastAPI(lifespan=lifespan)
api = FastAPI()
app.mount("/api", api)
app.mount("/", StaticFiles(directory=FRONTEND_ROOT, html=True), name="frontend")
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_methods=["*"],
    allow_headers=["*"],
)


@api.get("/packages", response_model=list[PackagePublic])
def read_packages(
    session: Annotated[Session, Depends(session)],
    q: str = "",
    page: int = 0,
):
    statement = (
        select(Package, func.sum(col(Download.downloads)).label("downloads_total"))
        .join(Download)
        .group_by(col(Package.id))
        .order_by(desc("downloads_total"))
    )
    if q:
        logger.info(f"search term: %{q}")
        statement = statement.where(col(Package.name).like(f"{q}%"))
    statement = statement.limit(RESULTS_PER_PAGE).offset(page * RESULTS_PER_PAGE)
    result = session.exec(statement)

    return [
        {"downloads_total": downloads_total, **package.model_dump()}
        for package, downloads_total in result
    ]
