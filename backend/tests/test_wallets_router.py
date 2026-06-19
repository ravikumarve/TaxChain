import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4

from app.routers.wallets import router
from app.models.user import User
from app.models.wallet import Wallet

# Create a test app with just the wallet router
from fastapi import FastAPI

test_app = FastAPI()
test_app.include_router(router, prefix="/api/wallets")
client = TestClient(test_app)


@pytest.fixture
def mock_user():
    """Create a mock user for testing"""
    return User(id=uuid4(), email="test@example.com", plan="pro")


@pytest.fixture
def mock_free_user():
    """Create a mock free tier user"""
    return User(id=uuid4(), email="free@example.com", plan="free")


@pytest.fixture
def mock_wallet():
    """Create a mock wallet"""
    return Wallet(
        id=uuid4(),
        address="0x1234567890123456789012345678901234567890",
        chain="eth",
        user_id=uuid4(),
    )


@pytest.mark.asyncio
async def test_list_wallets_success(mock_user):
    """Test successful wallet listing"""
    with (
        patch("app.routers.wallets.get_db") as mock_get_db,
        patch("app.routers.wallets.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock wallet query
        mock_wallets = [
            Wallet(id=uuid4(), address="0x123...", chain="eth", user_id=mock_user.id),
            Wallet(id=uuid4(), address="0x456...", chain="bnb", user_id=mock_user.id),
        ]
        mock_db.execute.return_value.scalars.return_value.all.return_value = (
            mock_wallets
        )

        response = client.get("/api/wallets/")

        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0]["chain"] == "eth"


@pytest.mark.asyncio
async def test_add_wallet_success(mock_user):
    """Test successful wallet addition"""
    with (
        patch("app.routers.wallets.get_db") as mock_get_db,
        patch("app.routers.wallets.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock no existing wallet
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        # Mock wallet count (pro user)
        mock_db.execute.return_value.scalar.return_value = 0

        response = client.post(
            "/api/wallets/",
            params={
                "address": "0x1234567890123456789012345678901234567890",
                "chain": "eth",
                "label": "My ETH Wallet",
            },
        )

        assert response.status_code == 201
        assert "Wallet added successfully" in response.json()["message"]


@pytest.mark.asyncio
async def test_add_wallet_invalid_chain(mock_user):
    """Test wallet addition with invalid chain"""
    with patch("app.routers.wallets.get_current_user") as mock_get_user:
        mock_get_user.return_value = mock_user

        response = client.post(
            "/api/wallets/",
            params={
                "address": "0x1234567890123456789012345678901234567890",
                "chain": "invalid_chain",
            },
        )

        assert response.status_code == 400
        assert "Invalid chain" in response.json()["detail"]


@pytest.mark.asyncio
async def test_add_wallet_invalid_address_format(mock_user):
    """Test wallet addition with invalid address format"""
    with patch("app.routers.wallets.get_current_user") as mock_get_user:
        mock_get_user.return_value = mock_user

        response = client.post(
            "/api/wallets/", params={"address": "invalid_address", "chain": "eth"}
        )

        assert response.status_code == 400
        assert "Invalid eth address format" in response.json()["detail"]


@pytest.mark.asyncio
async def test_add_wallet_already_exists(mock_user, mock_wallet):
    """Test wallet addition when wallet already exists"""
    with (
        patch("app.routers.wallets.get_db") as mock_get_db,
        patch("app.routers.wallets.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock existing wallet
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_wallet

        response = client.post(
            "/api/wallets/",
            params={
                "address": "0x1234567890123456789012345678901234567890",
                "chain": "eth",
            },
        )

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_add_wallet_free_tier_limit(mock_free_user):
    """Test free tier wallet limit enforcement"""
    with (
        patch("app.routers.wallets.get_db") as mock_get_db,
        patch("app.routers.wallets.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_free_user

        # Mock no existing wallet with same address
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        # Mock wallet count (already has 1 wallet)
        mock_db.execute.return_value.scalar.return_value = 1

        response = client.post(
            "/api/wallets/",
            params={
                "address": "0x1234567890123456789012345678901234567890",
                "chain": "eth",
            },
        )

        assert response.status_code == 403
        assert "Free tier limited to 1 wallet" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_wallet_success(mock_user, mock_wallet):
    """Test successful wallet deletion"""
    with (
        patch("app.routers.wallets.get_db") as mock_get_db,
        patch("app.routers.wallets.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock wallet exists and belongs to user
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_wallet

        response = client.delete(f"/api/wallets/{mock_wallet.id}")

        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]


@pytest.mark.asyncio
async def test_delete_wallet_not_found(mock_user):
    """Test wallet deletion when wallet not found"""
    with (
        patch("app.routers.wallets.get_db") as mock_get_db,
        patch("app.routers.wallets.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock wallet not found
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        response = client.delete(f"/api/wallets/{uuid4()}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_sync_wallet_success(mock_user, mock_wallet):
    """Test successful wallet sync"""
    with (
        patch("app.routers.wallets.get_db") as mock_get_db,
        patch("app.routers.wallets.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock wallet exists and belongs to user
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_wallet

        response = client.post(f"/api/wallets/{mock_wallet.id}/sync")

        assert response.status_code == 200
        assert "Sync triggered" in response.json()["message"]


@pytest.mark.asyncio
async def test_get_wallet_status_success(mock_user, mock_wallet):
    """Test successful wallet status retrieval"""
    with (
        patch("app.routers.wallets.get_db") as mock_get_db,
        patch("app.routers.wallets.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock wallet exists and belongs to user
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_wallet
        # Mock transaction count
        mock_db.execute.return_value.scalar.return_value = 5

        response = client.get(f"/api/wallets/{mock_wallet.id}/status")

        assert response.status_code == 200
        assert response.json()["address"] == mock_wallet.address
        assert response.json()["transaction_count"] == 5
        assert "status" in response.json()


@pytest.mark.asyncio
async def test_get_wallet_status_not_found(mock_user):
    """Test wallet status when wallet not found"""
    with (
        patch("app.routers.wallets.get_db") as mock_get_db,
        patch("app.routers.wallets.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock wallet not found
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        response = client.get(f"/api/wallets/{uuid4()}/status")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


def test_address_validation():
    """Test address validation for different chains"""
    from app.routers.wallets import validate_wallet_address

    # Valid addresses
    assert validate_wallet_address("0x1234567890123456789012345678901234567890", "eth")
    assert validate_wallet_address("0x1234567890123456789012345678901234567890", "bnb")
    assert validate_wallet_address(
        "0x1234567890123456789012345678901234567890", "polygon"
    )
    assert validate_wallet_address("5Q544fKrFoe6fsEb5W6fG7yRyD4TjAg6Z7L3LmBQ7Q", "sol")

    # Invalid addresses
    assert not validate_wallet_address("invalid", "eth")
    assert not validate_wallet_address("0x123", "eth")
    assert not validate_wallet_address(
        "0x1234567890123456789012345678901234567890", "invalid_chain"
    )
    assert not validate_wallet_address("invalid_sol_address", "sol")


@pytest.mark.asyncio
async def test_sync_wallet_with_mock_blockchain_data(mock_user, mock_wallet):
    """Test wallet sync with mock blockchain data"""
    with (
        patch("app.routers.wallets.get_db") as mock_get_db,
        patch("app.routers.wallets.get_current_user") as mock_get_user,
        patch("app.routers.wallets.fetch_transactions") as mock_fetch_txs,
        patch("app.routers.wallets.categorize_transaction") as mock_categorize,
        patch("app.routers.wallets.get_historical_price") as mock_get_price,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock wallet exists and belongs to user
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_wallet

        # Mock blockchain data
        mock_blockchain_txs = [
            {
                "hash": "0xabc123",
                "from": "0x1234567890123456789012345678901234567890",
                "to": "0xrecipient",
                "value": "1000000000000000000",  # 1 ETH
                "gasPrice": "20000000000",
                "gasUsed": "21000",
                "timeStamp": "1640995200",  # Jan 1, 2022
                "isError": "0",
            }
        ]
        mock_fetch_txs.return_value = mock_blockchain_txs
        mock_categorize.return_value = "transfer_in"
        mock_get_price.return_value = Decimal("3000.0")

        response = client.post(f"/api/wallets/{mock_wallet.id}/sync")

        assert response.status_code == 200
        assert "Sync completed" in response.json()["message"]
        assert response.json()["transactions_processed"] == 1


@pytest.mark.asyncio
async def test_sync_wallet_rate_limiting(mock_user, mock_wallet):
    """Test wallet sync rate limiting"""
    with (
        patch("app.routers.wallets.get_db") as mock_get_db,
        patch("app.routers.wallets.get_current_user") as mock_get_user,
        patch("app.routers.wallets.fetch_transactions") as mock_fetch_txs,
        patch("app.routers.wallets.rate_limiter") as mock_rate_limiter,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_wallet

        # Mock rate limiting hit
        mock_rate_limiter.limit.return_value = True
        mock_fetch_txs.side_effect = HTTPException(
            status_code=429, detail="Rate limit exceeded"
        )

        response = client.post(f"/api/wallets/{mock_wallet.id}/sync")

        assert response.status_code == 429
        assert "Rate limit" in response.json()["detail"]


@pytest.mark.asyncio
async def test_sync_wallet_concurrent_operations(mock_user, mock_wallet):
    """Test concurrent wallet sync operations"""
    with (
        patch("app.routers.wallets.get_db") as mock_get_db,
        patch("app.routers.wallets.get_current_user") as mock_get_user,
        patch("app.routers.wallets.fetch_transactions") as mock_fetch_txs,
        patch("app.routers.wallets.asyncio.sleep") as mock_sleep,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_wallet

        # Mock concurrent operations by delaying response
        async def delayed_fetch(*args, **kwargs):
            await mock_sleep(0.1)
            return []

        mock_fetch_txs.side_effect = delayed_fetch

        response = client.post(f"/api/wallets/{mock_wallet.id}/sync")

        assert response.status_code == 200
        assert mock_sleep.called


@pytest.mark.asyncio
async def test_sync_wallet_empty_blockchain_response(mock_user, mock_wallet):
    """Test wallet sync with empty blockchain response"""
    with (
        patch("app.routers.wallets.get_db") as mock_get_db,
        patch("app.routers.wallets.get_current_user") as mock_get_user,
        patch("app.routers.wallets.fetch_transactions") as mock_fetch_txs,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_wallet
        mock_fetch_txs.return_value = []  # Empty response

        response = client.post(f"/api/wallets/{mock_wallet.id}/sync")

        assert response.status_code == 200
        assert "No new transactions" in response.json()["message"]


@pytest.mark.asyncio
async def test_sync_wallet_invalid_address_format(mock_user):
    """Test wallet sync with invalid address format"""
    with (
        patch("app.routers.wallets.get_db") as mock_get_db,
        patch("app.routers.wallets.get_current_user") as mock_get_user,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        # Mock wallet with invalid address
        invalid_wallet = Wallet(
            id=uuid4(),
            address="invalid_address",
            chain="eth",
            user_id=mock_user.id,
        )
        mock_db.execute.return_value.scalar_one_or_none.return_value = invalid_wallet

        response = client.post(f"/api/wallets/{invalid_wallet.id}/sync")

        assert response.status_code == 400
        assert "Invalid address format" in response.json()["detail"]


@pytest.mark.asyncio
async def test_sync_wallet_network_error(mock_user, mock_wallet):
    """Test wallet sync with network error"""
    with (
        patch("app.routers.wallets.get_db") as mock_get_db,
        patch("app.routers.wallets.get_current_user") as mock_get_user,
        patch("app.routers.wallets.fetch_transactions") as mock_fetch_txs,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_wallet
        mock_fetch_txs.side_effect = Exception("Network connection failed")

        response = client.post(f"/api/wallets/{mock_wallet.id}/sync")

        assert response.status_code == 500
        assert "Error syncing wallet" in response.json()["detail"]


@pytest.mark.asyncio
async def test_sync_wallet_large_transaction_volume(mock_user, mock_wallet):
    """Test wallet sync with large volume of transactions"""
    with (
        patch("app.routers.wallets.get_db") as mock_get_db,
        patch("app.routers.wallets.get_current_user") as mock_get_user,
        patch("app.routers.wallets.fetch_transactions") as mock_fetch_txs,
        patch("app.routers.wallets.categorize_transaction") as mock_categorize,
        patch("app.routers.wallets.get_historical_price") as mock_get_price,
    ):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user

        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_wallet

        # Mock 1000 transactions (large volume)
        large_tx_list = []
        for i in range(1000):
            large_tx_list.append(
                {
                    "hash": f"0x{i:064x}",
                    "from": "0x1234567890123456789012345678901234567890",
                    "to": f"0xrecipient{i}",
                    "value": "1000000000000000000",
                    "timeStamp": str(1640995200 + i),
                    "isError": "0",
                }
            )

        mock_fetch_txs.return_value = large_tx_list
        mock_categorize.return_value = "transfer_in"
        mock_get_price.return_value = Decimal("3000.0")

        response = client.post(f"/api/wallets/{mock_wallet.id}/sync")

        assert response.status_code == 200
        assert response.json()["transactions_processed"] == 1000
        assert "large volume" in response.json()["message"].lower()
