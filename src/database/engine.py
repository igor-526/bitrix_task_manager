from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (AsyncSession,
                                    async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import Session, sessionmaker

from .models import Base

async_engine = create_async_engine('sqlite+aiosqlite:///db.db', echo=True)
sync_engine = create_engine('sqlite:///db.db', echo=True)

async_session_maker = async_sessionmaker(bind=async_engine,
                                         class_=AsyncSession,
                                         expire_on_commit=False)

session_maker = sessionmaker(bind=sync_engine,
                             class_=Session,
                             expire_on_commit=False)


async def create_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
