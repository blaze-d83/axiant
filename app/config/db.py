from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker 
from .settings import settings

engine = create_async_engine(settings.sqlite_database_url, echo=settings.debug, connect_args={"check_same_thread": False})

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncEngine, expire_on_commit=False)

# Initial table creation
async def create_db_tables() -> None:
    """Create SQLMOdel tables"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# DB dependency to pass
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency: One db session per request"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
