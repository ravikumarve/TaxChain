"""
Async test suite for chain sync service.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from app.services.chain_sync import fetch_transactions, ChainSyncError


@pytest.mark.asyncio
async def test_fetch_transactions_unsupported_chain():
    """Test error handling for unsupported chains."""
    with pytest.raises(ChainSyncError, match="Unsupported chain: invalid_chain"):
        await fetch_transactions(
            "0x1234567890abcdef1234567890abcdef12345678", "invalid_chain"
        )


@pytest.mark.asyncio
async def test_fetch_transactions_network_error():
    """Test network error handling."""
    with patch("httpx.AsyncClient.get", side_effect=httpx.RequestError("Network error")):
        with pytest.raises(ChainSyncError, match="Network error"):
            await fetch_transactions(
                "0x1234567890abcdef1234567890abcdef12345678", "eth"
            )


@pytest.mark.asyncio
async def test_fetch_transactions_api_error():
    """Test API error handling."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        with pytest.raises(ChainSyncError, match="API error"):
            await fetch_transactions(
                "0x1234567890abcdef1234567890abcdef12345678", "eth"
            )


@pytest.mark.asyncio
async def test_fetch_transactions_invalid_json():
    """Test invalid JSON response handling."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        with pytest.raises(ChainSyncError, match="Invalid JSON response"):
            await fetch_transactions(
                "0x1234567890abcdef1234567890abcdef12345678", "eth"
            )


@pytest.mark.asyncio
async def test_fetch_transactions_with_retry_success():
    """Test successful retry scenario."""
    from app.services.chain_sync import fetch_transactions_with_retry

    mock_txs = [{"hash": "0x123", "value": "1000000000000000000"}]

    with patch("app.services.chain_sync.fetch_transactions", return_value=mock_txs):
        with patch("app.services.chain_sync.transform_transaction") as mock_transform:
            mock_transform.return_value = {"tx_hash": "0x123", "value": 1.0}

            result = await fetch_transactions_with_retry("0x123", "eth")

            assert len(result) == 1
            assert result[0]["tx_hash"] == "0x123"


@pytest.mark.asyncio
async def test_fetch_transactions_with_retry_failure():
    """Test retry failure scenario."""
    from app.services.chain_sync import fetch_transactions_with_retry

    with patch(
        "app.services.chain_sync.fetch_transactions",
        side_effect=ChainSyncError("API error"),
    ):
        with pytest.raises(ChainSyncError):
            await fetch_transactions_with_retry("0x123", "eth", max_retries=2)
