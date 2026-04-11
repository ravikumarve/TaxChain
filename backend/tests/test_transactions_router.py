import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4
from datetime import datetime, date

from app.routers.transactions import router
from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import Transaction

# Create a test app with just the transactions router
from fastapi import FastAPI

test_app = FastAPI()
test_app.include_router(router, prefix="/api/transactions")
client = TestClient(test_app)


@pytest.fixture
def mock_user():
    """Create a mock user for testing"""
    return User(id=uuid4(), email="test@example.com", plan="pro")


@pytest.fixture
def mock_wallet():
    """Create a mock wallet"""
    return Wallet(
        id=uuid4(),
        address="0x1234567890123456789012345678901234567890",
        chain="eth",
        user_id=uuid4(),
    )


@pytest.fixture
def mock_transaction():
    """Create a mock transaction"""
    return Transaction(
        id=uuid4(),
        tx_hash="0xabc123def456ghi789jkl012mno345pqr678stu901vwx234yz5678901234",
        chain="eth",
        tx_type="transfer_in",
        token_symbol="ETH",
        token_address="0x0000000000000000000000000000000000000000",
        quantity=1.5,
        price_usd=2000.0,
        value_usd=3000.0,
        fee_usd=10.0,
        timestamp=datetime(2024, 1, 1, 12, 0, 0),
        wallet_id=uuid4(),
        user_id=uuid4(),
    )


@pytest.mark.asyncio
async def test_list_transactions_success(mock_user, mock_transaction):
    """Test successful transaction listing"""
    with (
        patch("app.routers.transactions.get_db") as mock_get_db,
        patch("app.routers.transactions.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock transaction query
        mock_db.execute.return_value.scalars.return_value.all.return_value = [
            mock_transaction
        ]
        # Mock count query
        mock_db.execute.return_value.scalar.return_value = 1

        response = client.get("/api/transactions/")

        assert response.status_code == 200
        assert len(response.json()["transactions"]) == 1
        assert response.json()["transactions"][0]["chain"] == "eth"
        assert response.json()["pagination"]["total"] == 1


@pytest.mark.asyncio
async def test_list_transactions_with_filters(mock_user, mock_transaction):
    """Test transaction listing with filters"""
    with (
        patch("app.routers.transactions.get_db") as mock_get_db,
        patch("app.routers.transactions.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock transaction query
        mock_db.execute.return_value.scalars.return_value.all.return_value = [
            mock_transaction
        ]
        # Mock count query
        mock_db.execute.return_value.scalar.return_value = 1

        response = client.get(
            "/api/transactions/?chain=eth&tx_type=transfer_in&page=1&limit=50"
        )

        assert response.status_code == 200
        assert len(response.json()["transactions"]) == 1


@pytest.mark.asyncio
async def test_list_transactions_invalid_chain(mock_user):
    """Test transaction listing with invalid chain filter"""
    with patch("app.routers.transactions.get_current_user") as mock_get_user:
        mock_get_user.return_value = mock_user

        response = client.get("/api/transactions/?chain=invalid_chain")

        assert response.status_code == 400
        assert "Invalid chain" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_transactions_invalid_tx_type(mock_user):
    """Test transaction listing with invalid transaction type filter"""
    with patch("app.routers.transactions.get_current_user") as mock_get_user:
        mock_get_user.return_value = mock_user

        response = client.get("/api/transactions/?tx_type=invalid_type")

        assert response.status_code == 400
        assert "Invalid transaction type" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_transactions_pagination_limits(mock_user, mock_transaction):
    """Test transaction listing pagination limits"""
    with (
        patch("app.routers.transactions.get_db") as mock_get_db,
        patch("app.routers.transactions.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock transaction query
        mock_db.execute.return_value.scalars.return_value.all.return_value = [
            mock_transaction
        ]
        # Mock count query
        mock_db.execute.return_value.scalar.return_value = 1

        # Test limit too high
        response = client.get("/api/transactions/?limit=300")
        assert response.status_code == 422  # Validation error

        # Test limit valid
        response = client.get("/api/transactions/?limit=100")
        assert response.status_code == 200

        # Test page too low
        response = client.get("/api/transactions/?page=0")
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_transaction_summary_success(mock_user):
    """Test successful transaction summary"""
    with (
        patch("app.routers.transactions.get_db") as mock_get_db,
        patch("app.routers.transactions.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock summary query
        mock_summary = (
            10,  # total_transactions
            2,  # chains_count
            3,  # types_count
            15000.0,  # total_value_usd
            50.0,  # total_fee_usd
            datetime(2024, 1, 1),  # first_transaction
            datetime(2024, 12, 31),  # last_transaction
        )
        mock_db.execute.return_value.first.return_value = mock_summary

        response = client.get("/api/transactions/summary")

        assert response.status_code == 200
        assert response.json()["total_transactions"] == 10
        assert response.json()["chains_count"] == 2
        assert response.json()["total_value_usd"] == 15000.0


@pytest.mark.asyncio
async def test_get_transaction_summary_empty(mock_user):
    """Test transaction summary with no transactions"""
    with (
        patch("app.routers.transactions.get_db") as mock_get_db,
        patch("app.routers.transactions.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock empty summary
        mock_db.execute.return_value.first.return_value = None

        response = client.get("/api/transactions/summary")

        assert response.status_code == 200
        assert response.json()["total_transactions"] == 0
        assert response.json()["total_value_usd"] == 0.0


@pytest.mark.asyncio
async def test_get_transaction_summary_with_filters(mock_user):
    """Test transaction summary with filters"""
    with (
        patch("app.routers.transactions.get_db") as mock_get_db,
        patch("app.routers.transactions.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock summary query
        mock_summary = (
            5,  # total_transactions
            1,  # chains_count
            2,  # types_count
            5000.0,  # total_value_usd
            20.0,  # total_fee_usd
            datetime(2024, 6, 1),  # first_transaction
            datetime(2024, 6, 30),  # last_transaction
        )
        mock_db.execute.return_value.first.return_value = mock_summary

        response = client.get("/api/transactions/summary?chain=eth&tx_type=transfer_in")

        assert response.status_code == 200
        assert response.json()["total_transactions"] == 5


@pytest.mark.asyncio
async def test_get_transaction_summary_invalid_chain(mock_user):
    """Test transaction summary with invalid chain filter"""
    with patch("app.routers.transactions.get_current_user") as mock_get_user:
        mock_get_user.return_value = mock_user

        response = client.get("/api/transactions/summary?chain=invalid_chain")

        assert response.status_code == 400
        assert "Invalid chain" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_transaction_summary_invalid_tx_type(mock_user):
    """Test transaction summary with invalid transaction type filter"""
    with patch("app.routers.transactions.get_current_user") as mock_get_user:
        mock_get_user.return_value = mock_user

        response = client.get("/api/transactions/summary?tx_type=invalid_type")

        assert response.status_code == 400
        assert "Invalid transaction type" in response.json()["detail"]


def test_valid_tx_types_constants():
    """Test that VALID_TX_TYPES contains all expected values"""
    from app.routers.transactions import VALID_TX_TYPES

    expected_types = {
        "trade",
        "transfer_in",
        "transfer_out",
        "staking",
        "airdrop",
        "nft_sale",
        "fee",
    }
    assert VALID_TX_TYPES == expected_types


def test_valid_chains_constants():
    """Test that VALID_CHAINS contains all expected values"""
    from app.routers.transactions import VALID_CHAINS

    expected_chains = {"eth", "bnb", "polygon", "sol"}
    assert VALID_CHAINS == expected_chains


@pytest.mark.asyncio
async def test_list_transactions_date_filters(mock_user, mock_transaction):
    """Test transaction listing with date filters"""
    with (
        patch("app.routers.transactions.get_db") as mock_get_db,
        patch("app.routers.transactions.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        mock_db.execute.return_value.scalars.return_value.all.return_value = [
            mock_transaction
        ]
        mock_db.execute.return_value.scalar.return_value = 1

        # Test start date filter
        response = client.get(
            "/api/transactions/?start_date=2024-01-01&end_date=2024-12-31"
        )
        assert response.status_code == 200

        # Test invalid date format
        response = client.get("/api/transactions/?start_date=invalid-date")
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_transactions_pagination_edge_cases(mock_user, mock_transaction):
    """Test transaction pagination edge cases"""
    with (
        patch("app.routers.transactions.get_db") as mock_get_db,
        patch("app.routers.transactions.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock empty result for page 2
        mock_db.execute.return_value.scalars.return_value.all.return_value = []
        mock_db.execute.return_value.scalar.return_value = 1

        response = client.get("/api/transactions/?page=2&limit=50")
        assert response.status_code == 200
        assert len(response.json()["transactions"]) == 0


@pytest.mark.asyncio
async def test_get_transaction_summary_complex_scenarios(mock_user):
    """Test transaction summary with complex scenarios"""
    with (
        patch("app.routers.transactions.get_db") as mock_get_db,
        patch("app.routers.transactions.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock complex summary data
        mock_summary = (
            100,  # total_transactions
            3,  # chains_count
            5,  # types_count
            50000.0,  # total_value_usd
            200.0,  # total_fee_usd
            datetime(2023, 1, 1),  # first_transaction
            datetime(2024, 12, 31),  # last_transaction
        )
        mock_db.execute.return_value.first.return_value = mock_summary

        response = client.get("/api/transactions/summary")

        assert response.status_code == 200
        assert response.json()["total_transactions"] == 100
        assert response.json()["chains_count"] == 3
        assert response.json()["total_value_usd"] == 50000.0


@pytest.mark.asyncio
async def test_get_transaction_summary_multiple_filters(mock_user):
    """Test transaction summary with multiple filters"""
    with (
        patch("app.routers.transactions.get_db") as mock_get_db,
        patch("app.routers.transactions.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        mock_summary = (
            10,  # total_transactions
            1,  # chains_count
            2,  # types_count
            15000.0,  # total_value_usd
            50.0,  # total_fee_usd
            datetime(2024, 1, 1),  # first_transaction
            datetime(2024, 12, 31),  # last_transaction
        )
        mock_db.execute.return_value.first.return_value = mock_summary

        response = client.get(
            "/api/transactions/summary?chain=eth&tx_type=transfer_in&start_date=2024-01-01&end_date=2024-12-31"
        )

        assert response.status_code == 200
        assert response.json()["total_transactions"] == 10


@pytest.mark.asyncio
async def test_list_transactions_large_dataset(mock_user):
    """Test transaction listing with large dataset"""
    with (
        patch("app.routers.transactions.get_db") as mock_get_db,
        patch("app.routers.transactions.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock large dataset
        mock_db.execute.return_value.scalars.return_value.all.return_value = [
            mock_transaction
        ] * 1000
        mock_db.execute.return_value.scalar.return_value = 1000

        response = client.get("/api/transactions/?limit=200")

        assert response.status_code == 200
        assert response.json()["pagination"]["total"] == 1000
        assert response.json()["pagination"]["per_page"] == 200


@pytest.mark.asyncio
async def test_list_transactions_sorting(mock_user, mock_transaction):
    """Test transaction listing with sorting"""
    with (
        patch("app.routers.transactions.get_db") as mock_get_db,
        patch("app.routers.transactions.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        mock_db.execute.return_value.scalars.return_value.all.return_value = [
            mock_transaction
        ]
        mock_db.execute.return_value.scalar.return_value = 1

        # Test different sort orders
        response = client.get("/api/transactions/?sort=asc")
        assert response.status_code == 200

        response = client.get("/api/transactions/?sort=desc")
        assert response.status_code == 200

        response = client.get("/api/transactions/?sort=invalid")
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_transaction_summary_empty_filters(mock_user):
    """Test transaction summary with empty result after filtering"""
    with (
        patch("app.routers.transactions.get_db") as mock_get_db,
        patch("app.routers.transactions.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock empty summary
        mock_db.execute.return_value.first.return_value = None

        response = client.get("/api/transactions/summary?chain=sol&tx_type=nft_sale")

        assert response.status_code == 200
        assert response.json()["total_transactions"] == 0
        assert response.json()["total_value_usd"] == 0.0


@pytest.mark.asyncio
async def test_list_transactions_concurrent_access(mock_user, mock_transaction):
    """Test concurrent access to transactions endpoint"""
    with (
        patch("app.routers.transactions.get_db") as mock_get_db,
        patch("app.routers.transactions.get_current_user") as mock_get_user,
        patch("app.routers.transactions.asyncio.sleep") as mock_sleep,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock database delay to test concurrency
        async def delayed_execute(*args, **kwargs):
            await mock_sleep(0.05)
            return [mock_transaction]

        mock_db.execute.side_effect = delayed_execute
        mock_db.execute.return_value.scalar.return_value = 1

        response = client.get("/api/transactions/")

        assert response.status_code == 200
        assert mock_sleep.called


@pytest.mark.asyncio
async def test_list_transactions_error_handling(mock_user):
    """Test transaction listing error handling"""
    with (
        patch("app.routers.transactions.get_db") as mock_get_db,
        patch("app.routers.transactions.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock database error
        mock_db.execute.side_effect = Exception("Database connection failed")

        response = client.get("/api/transactions/")

        assert response.status_code == 500
        assert "Error fetching transactions" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_transaction_summary_error_handling(mock_user):
    """Test transaction summary error handling"""
    with (
        patch("app.routers.transactions.get_db") as mock_get_db,
        patch("app.routers.transactions.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock database error
        mock_db.execute.side_effect = Exception("Database query failed")

        response = client.get("/api/transactions/summary")

        assert response.status_code == 500
        assert "Error fetching transaction summary" in response.json()["detail"]


def test_transaction_model_validation():
    """Test transaction model validation"""
    from app.routers.transactions import VALID_TX_TYPES, VALID_CHAINS
    from app.models.transaction import Transaction

    # Test valid transaction types
    for tx_type in VALID_TX_TYPES:
        tx = Transaction(
            id=uuid4(),
            tx_hash="0x123",
            chain="eth",
            tx_type=tx_type,
            token_symbol="ETH",
            quantity=Decimal("1.0"),
            timestamp=datetime.now(),
            wallet_id=uuid4(),
            user_id=uuid4(),
        )
        assert tx.tx_type == tx_type

    # Test valid chains
    for chain in VALID_CHAINS:
        tx = Transaction(
            id=uuid4(),
            tx_hash="0x123",
            chain=chain,
            tx_type="transfer_in",
            token_symbol="ETH",
            quantity=Decimal("1.0"),
            timestamp=datetime.now(),
            wallet_id=uuid4(),
            user_id=uuid4(),
        )
        assert tx.chain == chain
