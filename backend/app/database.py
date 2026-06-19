import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from sqlalchemy.exc import OperationalError, TimeoutError
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


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((OperationalError, TimeoutError)),
    before_sleep=lambda retry_state: logger.warning(
        f"DB connection attempt {retry_state.attempt_number} failed, retrying..."
    ),
)
async def get_db():
    async with async_session() as session:
        try:
            # Verify connection is alive
            await session.execute(text("SELECT 1"))
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
