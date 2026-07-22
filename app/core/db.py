from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, declared_attr, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    id = Column(Integer, primary_key=True)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


engine = create_async_engine(settings.database_url)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session
