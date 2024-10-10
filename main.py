from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Create the database and tables when the app starts
    """
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/hello")
async def hello_world():
    return {"hello": "world"}
