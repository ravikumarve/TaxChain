import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4


# Test address validation function directly
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


def test_chain_validation():
    """Test chain validation"""
    from app.routers.wallets import VALID_CHAINS

    assert "eth" in VALID_CHAINS
    assert "bnb" in VALID_CHAINS
    assert "polygon" in VALID_CHAINS
    assert "sol" in VALID_CHAINS
    assert "invalid" not in VALID_CHAINS
