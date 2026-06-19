#!/usr/bin/env python3
"""
Script to create a test user for TaxChain
Run with: python create_test_user.py
"""

import asyncio
import bcrypt
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select

# Database connection - adjust as needed
DATABASE_URL = "postgresql://user:pass@localhost:5432/taxchain"

# Create async engine
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_password_hash(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


async def create_test_user():
    """Create a test user with email: test@taxchain.app, password: testpassword123"""

    # Check if user already exists
    async with AsyncSessionLocal() as session:
        # We need to check if users table exists and create if needed
        # For now, let's just print the connection info

        print("Testing database connection...")
        try:
            # Try a simple query to check connection
            result = await session.execute("SELECT 1")
            print("✓ Database connection successful")
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            print("\nPlease ensure:")
            print("1. PostgreSQL is running")
            print("2. Database 'taxchain' exists")
            print("3. Connection string is correct in backend/.env")
            return

        # Check if users table exists
        try:
            result = await session.execute(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
            )
            table_exists = result.scalar()

            if not table_exists:
                print("✗ Users table does not exist. Please run migrations first:")
                print("   cd backend && alembic upgrade head")
                return

            print("✓ Users table exists")

            # Check if test user already exists
            result = await session.execute(
                "SELECT email FROM users WHERE email = 'test@taxchain.app'"
            )
            existing_user = result.scalar()

            if existing_user:
                print("✓ Test user already exists: test@taxchain.app")
                print("Password: testpassword123")
                return

            # Create test user
            hashed_password = await get_password_hash("testpassword123")
            await session.execute(
                "INSERT INTO users (email, password_hash, country, financial_year_start) VALUES (:email, :password, :country, :fy_start)",
                {
                    "email": "test@taxchain.app",
                    "password": hashed_password,
                    "country": "IN",
                    "fy_start": "04-01",
                },
            )
            await session.commit()
            print("✓ Test user created successfully!")
            print("Email: test@taxchain.app")
            print("Password: testpassword123")

        except Exception as e:
            print(f"✗ Error: {e}")
            print("\nYou may need to:")
            print("1. Run database migrations: cd backend && alembic upgrade head")
            print("2. Start PostgreSQL service")
            print("3. Check your database connection string in backend/.env")


if __name__ == "__main__":
    print("Creating test user for TaxChain...\n")
    asyncio.run(create_test_user())
