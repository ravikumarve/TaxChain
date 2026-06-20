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


async def get_db():
    """Yield an AsyncSession with retry logic for connection failures.

    Note: Must NOT use @retry decorator — tenacity breaks async generator
    detection (inspect.isasyncgenfunction returns False), which prevents
    FastAPI's Depends() from properly resolving the yield.
    """
    import asyncio

    last_error = None
    for attempt in range(1, 4):  # 3 attempts
        session = None
        try:
            async with async_session() as session:
                await session.execute(text("SELECT 1"))
                yield session
                await session.commit()
            return  # success, exit generator
        except (OperationalError, TimeoutError) as e:
            last_error = e
            logger.warning(f"DB connection attempt {attempt}/3 failed: {e}")
            if attempt < 3:
                await asyncio.sleep(min(2**attempt, 10))
        except Exception:
            if session is not None:
                await session.rollback()
            raise

    raise last_error or OperationalError("All database connection attempts failed")
