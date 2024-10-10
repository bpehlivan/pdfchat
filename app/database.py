from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from settings import settings

async_engine = create_async_engine(
    url=f"postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@"
    f"{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}",
    echo=True,
    future=True,
)


async def get_db_session():
    async_session = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session


async def create_db_and_tables(engine=async_engine):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
