#!/usr/bin/env python3
"""
Check if PostgreSQL is available and ready for integration tests.
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

database_url = os.getenv("DATABASE_URL")

if not database_url:
    print("✗ DATABASE_URL environment variable not set")
    print("Please create a .env file with DATABASE_URL=")
    exit(1)


async def check_postgres_connection():
    """Check if PostgreSQL is available."""
    try:
        conn = await asyncpg.connect(database_url)
        version = await conn.fetchval("SELECT version()")
        await conn.close()
        print(f"✓ PostgreSQL connected: {version}")
        return True
    except Exception as e:
        print(f"✗ PostgreSQL connection failed: {e}")
        return False


async def check_database_exists():
    """Check if the database exists."""
    try:
        # Extract database name from URL
        db_name = database_url.split("/")[-1]
        temp_conn = await asyncpg.connect(database_url.rsplit("/", 1)[0] + "/postgres")
        exists = await temp_conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", db_name
        )
        await temp_conn.close()

        if exists:
            print(f"✓ Database '{db_name}' exists")
            return True
        else:
            print(f"✗ Database '{db_name}' does not exist")
            return False
    except Exception as e:
        print(f"✗ Database check failed: {e}")
        return False


async def main():
    """Run all checks."""
    print("Checking PostgreSQL availability...")

    connection_ok = await check_postgres_connection()
    database_ok = await check_database_exists()

    if connection_ok and database_ok:
        print("\n✅ PostgreSQL is ready for integration tests!")
        print("Run: python tests/test_database_integration.py")
        return True
    else:
        print("\n❌ PostgreSQL is not ready for integration tests")
        print("Please ensure:")
        print("1. PostgreSQL is running")
        print("2. Database 'taxchain_test' exists")
        print("3. DATABASE_URL in .env points to correct database")
        return False


if __name__ == "__main__":
    asyncio.run(main())
