import pytest
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4

from app.routers.wallets import validate_wallet_address, VALID_CHAINS, CHAIN_VALIDATION
from app.models.user import User
from app.models.wallet import Wallet


def test_address_validation():
    """Test address validation for different chains"""
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


def test_chain_validation():
    """Test chain validation"""
    assert "eth" in VALID_CHAINS
    assert "bnb" in VALID_CHAINS
    assert "polygon" in VALID_CHAINS
    assert "sol" in VALID_CHAINS
    assert "invalid" not in VALID_CHAINS


@pytest.mark.asyncio
async def test_list_wallets_success():
    """Test successful wallet listing"""
    from app.routers.wallets import list_wallets

    mock_user = User(id=uuid4(), email="test@example.com", plan="pro")
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock wallet query
    mock_wallets = [
        Wallet(id=uuid4(), address="0x123...", chain="eth", user_id=mock_user.id),
        Wallet(id=uuid4(), address="0x456...", chain="bnb", user_id=mock_user.id),
    ]

    # Create proper async mock structure
    mock_scalars = AsyncMock()
    mock_scalars.all.return_value = mock_wallets
    mock_result = AsyncMock()
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result

    result = await list_wallets(mock_db, mock_user)

    assert len(result) == 2
    assert result[0]["chain"] == "eth"
    assert result[1]["chain"] == "bnb"


@pytest.mark.asyncio
async def test_add_wallet_success():
    """Test successful wallet addition"""
    from app.routers.wallets import add_wallet

    mock_user = User(id=uuid4(), email="test@example.com", plan="pro")
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock no existing wallet
    mock_scalar_result = AsyncMock()
    mock_scalar_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_scalar_result

    # Mock wallet count (pro user)
    mock_scalar_count = AsyncMock()
    mock_scalar_count.scalar.return_value = 0
    mock_db.execute.return_value = mock_scalar_count

    result = await add_wallet(
        "0x1234567890123456789012345678901234567890",
        "eth",
        "My ETH Wallet",
        mock_db,
        mock_user,
    )

    assert "Wallet added successfully" in result["message"]
    assert "wallet_id" in result


@pytest.mark.asyncio
async def test_add_wallet_invalid_chain():
    """Test wallet addition with invalid chain"""
    from app.routers.wallets import add_wallet

    mock_user = User(id=uuid4(), email="test@example.com", plan="pro")
    mock_db = AsyncMock(spec=AsyncSession)

    with pytest.raises(HTTPException) as exc_info:
        await add_wallet(
            "0x1234567890123456789012345678901234567890",
            "invalid_chain",
            None,
            mock_db,
            mock_user,
        )

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid chain" in exc_info.value.detail


@pytest.mark.asyncio
async def test_add_wallet_invalid_address_format():
    """Test wallet addition with invalid address format"""
    from app.routers.wallets import add_wallet

    mock_user = User(id=uuid4(), email="test@example.com", plan="pro")
    mock_db = AsyncMock(spec=AsyncSession)

    with pytest.raises(HTTPException) as exc_info:
        await add_wallet("invalid_address", "eth", None, mock_db, mock_user)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "ETH" in exc_info.value.detail


@pytest.mark.asyncio
async def test_add_wallet_free_tier_limit():
    """Test free tier wallet limit enforcement"""
    from app.routers.wallets import add_wallet

    mock_user = User(id=uuid4(), email="test@example.com", plan="free")
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock no existing wallet with same address
    mock_scalar_exists = AsyncMock()
    mock_scalar_exists.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_scalar_exists

    # Mock wallet count (already has 1 wallet)
    mock_scalar_count = AsyncMock()
    mock_scalar_count.scalar.return_value = 1
    mock_db.execute.return_value = mock_scalar_count

    with pytest.raises(HTTPException) as exc_info:
        await add_wallet(
            "0x1234567890123456789012345678901234567890",
            "eth",
            None,
            mock_db,
            mock_user,
        )

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Free tier limited to 1 wallet" in exc_info.value.detail
