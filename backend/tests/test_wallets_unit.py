"""Unit tests for wallet functions (pure, no HTTP client)."""
import pytest
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

from app.routers.wallets import validate_wallet_address
from app.constants import ALL_CHAINS as VALID_CHAINS


def test_address_validation():
    """Test address validation for different chains"""
    assert validate_wallet_address("0x1234567890123456789012345678901234567890", "eth")
    assert validate_wallet_address("0x1234567890123456789012345678901234567890", "bnb")
    assert validate_wallet_address("0x1234567890123456789012345678901234567890", "polygon")
    assert validate_wallet_address("5Q544fKrFoe6fsEb5W6fG7yRyD4TjAg6Z7L3LmBQ7Q", "sol")
    assert not validate_wallet_address("invalid", "eth")
    assert not validate_wallet_address("0x123", "eth")
    assert not validate_wallet_address("0x1234567890123456789012345678901234567890", "invalid_chain")


def test_chain_validation():
    """Test chain validation"""
    assert "eth" in VALID_CHAINS
    assert "bnb" in VALID_CHAINS
    assert "polygon" in VALID_CHAINS
    assert "sol" in VALID_CHAINS
    assert "btc" in VALID_CHAINS
    assert "invalid" not in VALID_CHAINS
