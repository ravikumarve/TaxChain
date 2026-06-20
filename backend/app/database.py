import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

logger = logging.getLogger(__name__)

# Create declarative base for SQLAlchemy models
Base = declarative_base()

# Handle SQLite vs PostgreSQL connection args
connect_args = {}
if "sqlite" in settings.DATABASE_URL:
    connect_args = {"check_same_thread": False}
    pool_config = {}
else:
    # PostgreSQL production pool settings
    pool_config = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "pool_pre_ping": True,
        "pool_recycle": 1800,
    }

engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    future=True,
    **pool_config,
)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    """Yield an AsyncSession for FastAPI's Depends() injection.

    Connection retries are handled by the engine's pool_pre_ping setting.
    No manual retry loop — Python 3.12 async generators with try/except/yield
    trigger RuntimeError("generator didn't stop after athrow()") on cleanup.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
