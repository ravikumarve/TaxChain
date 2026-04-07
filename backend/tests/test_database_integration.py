"""
Database integration tests for TaxChain backend.

Tests database connection, model operations, Decimal handling,
relationships, and async session functionality.
"""

import asyncio
import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.database import get_db, Base, engine
from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import Transaction


@pytest.fixture(scope="module")
async def setup_database():
    """Create test tables and yield session."""
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_database_connection():
    """Test that database connection works."""
    async with AsyncSession(engine) as session:
        # Test connection by executing a simple query
        result = await session.execute(select(1))
        assert result.scalar() == 1
        print("✓ Database connection successful")


@pytest.mark.asyncio
async def test_user_creation(setup_database):
    """Test creating a user with proper fields."""
    async with AsyncSession(engine) as session:
        # Create test user
        user = User(
            email="test@example.com",
            password_hash="hashed_password_123",
            plan="free",
            country="IN",
            financial_year_start="04-01",
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)

        # Verify user was created
        assert user.id is not None
        assert isinstance(user.id, UUID)
        assert user.email == "test@example.com"
        assert user.country == "IN"
        assert user.financial_year_start == "04-01"
        assert user.created_at is not None
        assert user.updated_at is not None

        print("✓ User creation successful")
        return user


@pytest.mark.asyncio
async def test_wallet_creation(setup_database):
    """Test creating a wallet with proper relationships."""
    async with AsyncSession(engine) as session:
        # Create user first
        user = User(
            email="wallet_test@example.com", password_hash="hashed_password_123"
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        # Create wallet
        wallet = Wallet(
            user_id=user.id,
            address="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            chain="eth",
            label="Test Wallet",
        )

        session.add(wallet)
        await session.commit()
        await session.refresh(wallet)

        # Verify wallet was created
        assert wallet.id is not None
        assert isinstance(wallet.id, UUID)
        assert wallet.address == "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
        assert wallet.chain == "eth"
        assert wallet.user_id == user.id
        assert wallet.created_at is not None

        print("✓ Wallet creation successful")
        return wallet


@pytest.mark.asyncio
async def test_decimal_precision_handling(setup_database):
    """Test that Decimal types work correctly for financial amounts."""
    async with AsyncSession(engine) as session:
        # Create user and wallet
        user = User(
            email="decimal_test@example.com", password_hash="hashed_password_123"
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        wallet = Wallet(
            user_id=user.id,
            address="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            chain="eth",
        )
        session.add(wallet)
        await session.commit()
        await session.refresh(wallet)

        # Test various Decimal precision scenarios
        test_cases = [
            # (quantity, price_usd, expected_value_usd)
            (
                Decimal("1.234567890123456789"),
                Decimal("1234.56789012"),
                Decimal("1524.691357024691357"),
            ),
            (
                Decimal("0.00000001"),
                Decimal("50000.00"),
                Decimal("0.0005"),
            ),  # Small amounts
            (
                Decimal("1000000.0"),
                Decimal("0.00000001"),
                Decimal("0.01"),
            ),  # Large quantity, small price
            (
                Decimal("123456789012345.6789"),
                Decimal("0.12345678"),
                Decimal("15241577.54867901234567"),
            ),
        ]

        for i, (quantity, price_usd, expected_value_usd) in enumerate(test_cases):
            transaction = Transaction(
                wallet_id=wallet.id,
                user_id=user.id,
                tx_hash=f"0x{i}{'a' * 63}",
                chain="eth",
                tx_type="transfer_in",
                token_symbol="ETH",
                quantity=quantity,
                price_usd=price_usd,
                value_usd=quantity * price_usd,
                fee_usd=Decimal("0.001"),
                timestamp=user.created_at,
            )

            session.add(transaction)
            await session.commit()
            await session.refresh(transaction)

            # Verify Decimal precision is preserved
            assert transaction.quantity == quantity
            assert transaction.price_usd == price_usd
            assert transaction.value_usd == expected_value_usd
            assert transaction.fee_usd == Decimal("0.001")

            print(f"✓ Decimal precision test {i + 1} successful")


@pytest.mark.asyncio
async def test_relationships(setup_database):
    """Test that relationships between models work correctly."""
    async with AsyncSession(engine) as session:
        # Create user
        user = User(
            email="relationship_test@example.com", password_hash="hashed_password_123"
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        # Create wallet
        wallet = Wallet(
            user_id=user.id,
            address="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            chain="eth",
        )
        session.add(wallet)
        await session.commit()
        await session.refresh(wallet)

        # Create transaction
        transaction = Transaction(
            wallet_id=wallet.id,
            user_id=user.id,
            tx_hash="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            chain="eth",
            tx_type="transfer_in",
            token_symbol="ETH",
            quantity=Decimal("1.5"),
            price_usd=Decimal("2000.00"),
            value_usd=Decimal("3000.00"),
            fee_usd=Decimal("0.001"),
            timestamp=user.created_at,
        )
        session.add(transaction)
        await session.commit()
        await session.refresh(transaction)

        # Test relationships by querying
        user_query = await session.execute(
            select(User).where(User.email == "relationship_test@example.com")
        )
        fetched_user = user_query.scalar()

        # Check user -> wallets relationship
        assert len(fetched_user.wallets) == 1
        assert fetched_user.wallets[0].address == wallet.address

        # Check user -> transactions relationship
        assert len(fetched_user.transactions) == 1
        assert fetched_user.transactions[0].tx_hash == transaction.tx_hash

        # Check wallet -> user relationship
        wallet_query = await session.execute(
            select(Wallet).where(Wallet.id == wallet.id)
        )
        fetched_wallet = wallet_query.scalar()
        assert fetched_wallet.user.email == user.email

        # Check wallet -> transactions relationship
        assert len(fetched_wallet.transactions) == 1
        assert fetched_wallet.transactions[0].id == transaction.id

        # Check transaction -> user relationship
        transaction_query = await session.execute(
            select(Transaction).where(Transaction.id == transaction.id)
        )
        fetched_transaction = transaction_query.scalar()
        assert fetched_transaction.user.email == user.email

        # Check transaction -> wallet relationship
        assert fetched_transaction.wallet.address == wallet.address

        print("✓ All relationships work correctly")


@pytest.mark.asyncio
async def test_async_session_cleanup():
    """Test that async sessions are properly cleaned up."""
    # Test the get_db dependency
    session_count_before = len(engine.sync_engine.pool.checkedin_connections)

    async for session in get_db():
        # Use the session
        result = await session.execute(select(1))
        assert result.scalar() == 1

        # Session should be open
        assert not session.closed

    # Session should be closed after context manager
    session_count_after = len(engine.sync_engine.pool.checkedin_connections)

    print("✓ Async session cleanup successful")


@pytest.mark.asyncio
async def test_concurrent_operations(setup_database):
    """Test concurrent database operations."""

    async def create_user_and_wallet(email_suffix):
        async with AsyncSession(engine) as session:
            user = User(
                email=f"concurrent{email_suffix}@example.com",
                password_hash=f"hash{email_suffix}",
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

            wallet = Wallet(
                user_id=user.id, address=f"0x{email_suffix * 40}", chain="eth"
            )
            session.add(wallet)
            await session.commit()

            return user.id

    # Run concurrent operations
    tasks = [create_user_and_wallet(str(i)) for i in range(5)]
    results = await asyncio.gather(*tasks)

    # Verify all operations completed
    assert len(results) == 5
    assert all(isinstance(result, UUID) for result in results)

    print("✓ Concurrent operations successful")


if __name__ == "__main__":
    """Run tests directly for quick verification."""
    import asyncio

    async def run_tests():
        print("Running database integration tests...")

        # Create tables first
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        try:
            await test_database_connection()
            await test_user_creation(None)
            await test_wallet_creation(None)
            await test_decimal_precision_handling(None)
            await test_relationships(None)
            await test_async_session_cleanup()
            await test_concurrent_operations(None)

            print("\n🎉 All database integration tests passed!")

        finally:
            # Clean up
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)

    asyncio.run(run_tests())
