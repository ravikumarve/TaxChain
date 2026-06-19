"""
Pytest configuration for TaxChain backend tests.
"""

import pytest
import os
from dotenv import load_dotenv

# Load test environment variables
load_dotenv("../.env.test", override=True)

# Set test database URL if not already set
# Use SQLite by default (no PostgreSQL needed for unit tests)
if "TEST_DATABASE_URL" not in os.environ and "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_taxchain.db"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
