from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from sqlmodel import Session, select

from petshop.db import engine
from petshop.models import Package


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    load_dotenv()  # pyright: ignore[reportUnusedCallResult]
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/packages/", response_model=list[Package])
def read_packages(limit: int, page: int = 0):
    with Session(engine()) as session:
        statement = select(Package).limit(limit).offset(page * limit)
        packages = session.exec(statement)
        return packages.all()
