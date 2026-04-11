"""
Test suite for chain sync service.
"""

import pytest
import asyncio
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from decimal import Decimal
from app.services.chain_sync import (
    fetch_transactions,
    transform_transaction,
    validate_address,
    ChainSyncError,
    CHAIN_CONFIGS,
)
from app.config import settings


class TestChainSync:
    """Test chain sync service functionality."""

    @pytest.mark.asyncio
    async def test_fetch_transactions_unsupported_chain(self):
        """Test error handling for unsupported chains."""
        with pytest.raises(ChainSyncError, match="Unsupported chain: invalid_chain"):
            await fetch_transactions(
                "0x1234567890abcdef1234567890abcdef12345678", "invalid_chain"
            )

    @pytest.mark.asyncio
    async def test_fetch_transactions_network_error(self):
        """Test network error handling."""
        with patch(
            "httpx.AsyncClient.get", side_effect=httpx.RequestError("Network error")
        ):
            with pytest.raises(ChainSyncError, match="Network error"):
                await fetch_transactions(
                    "0x1234567890abcdef1234567890abcdef12345678", "eth"
                )

    @pytest.mark.asyncio
    async def test_fetch_transactions_api_error(self):
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
    async def test_fetch_transactions_invalid_json(self):
        """Test invalid JSON response handling."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            with pytest.raises(ChainSyncError, match="Invalid JSON response"):
                await fetch_transactions(
                    "0x1234567890abcdef1234567890abcdef12345678", "eth"
                )

    def test_transform_evm_transaction(self):
        """Test EVM transaction transformation."""
        raw_tx = {
            "hash": "0x123",
            "from": "0xfrom",
            "to": "0xto",
            "value": "1000000000000000000",  # 1 ETH in wei
            "gasUsed": "21000",
            "gasPrice": "20000000000",
            "blockNumber": "123456",
            "timeStamp": "1614556800",
            "isError": "0",
            "contractAddress": "",
            "tokenSymbol": "",
            "tokenName": "",
            "tokenDecimal": "0",
        }

        result = transform_transaction(raw_tx, "eth")

        assert result["tx_hash"] == "0x123"
        assert result["chain"] == "eth"
        assert result["value"] == Decimal("1.0")
        assert result["gas_used"] == 21000
        assert result["gas_price"] == 20000000000
        assert result["block_number"] == 123456
        assert isinstance(result["timestamp"], datetime)
        assert result["is_error"] is False
        assert result["tx_type"] == "transfer"

    def test_transform_evm_token_transaction(self):
        """Test EVM token transaction transformation."""
        raw_tx = {
            "hash": "0x123",
            "from": "0xfrom",
            "to": "0xto",
            "value": "0",
            "gasUsed": "50000",
            "gasPrice": "20000000000",
            "blockNumber": "123456",
            "timeStamp": "1614556800",
            "isError": "0",
            "contractAddress": "0xcontract",
            "tokenSymbol": "USDC",
            "tokenName": "USD Coin",
            "tokenDecimal": "6",
        }

        result = transform_transaction(raw_tx, "eth")

        assert result["tx_hash"] == "0x123"
        assert result["chain"] == "eth"
        assert result["value"] == Decimal("0")
        assert result["token_symbol"] == "USDC"
        assert result["tx_type"] == "token_transfer"

    def test_transform_failed_transaction(self):
        """Test failed transaction transformation."""
        raw_tx = {
            "hash": "0x123",
            "from": "0xfrom",
            "to": "0xto",
            "value": "1000000000000000000",
            "gasUsed": "21000",
            "gasPrice": "20000000000",
            "blockNumber": "123456",
            "timeStamp": "1614556800",
            "isError": "1",
            "contractAddress": "",
            "tokenSymbol": "",
            "tokenName": "",
            "tokenDecimal": "0",
        }

        result = transform_transaction(raw_tx, "eth")

        assert result["is_error"] is True
        assert result["tx_type"] == "failed"

    def test_validate_address_eth_valid(self):
        """Test valid ETH address validation."""
        valid_address = "0x742d35Cc6634C893292Ce8bB6239C002Ad8e6b59"
        assert validate_address(valid_address, "eth") is True

    def test_validate_address_eth_invalid(self):
        """Test invalid ETH address validation."""
        invalid_address = "0xinvalid"
        assert validate_address(invalid_address, "eth") is False

    def test_validate_address_sol_valid(self):
        """Test valid Solana address validation."""
        valid_address = "5qGuzSNS4NQNQK8eUC8op6U1q8YYzP1y3J1y3J1y3J"
        assert validate_address(valid_address, "sol") is True

    def test_validate_address_sol_invalid(self):
        """Test invalid Solana address validation."""
        invalid_address = "invalid"
        assert validate_address(invalid_address, "sol") is False

    def test_validate_address_unsupported_chain(self):
        """Test validation for unsupported chain."""
        assert validate_address("0x123", "invalid_chain") is False

    @pytest.mark.asyncio
    async def test_fetch_transactions_with_retry_success(self):
        """Test successful retry scenario."""
        from app.services.chain_sync import fetch_transactions_with_retry

        mock_txs = [{"hash": "0x123", "value": "1000000000000000000"}]

        with patch("app.services.chain_sync.fetch_transactions", return_value=mock_txs):
            with patch(
                "app.services.chain_sync.transform_transaction"
            ) as mock_transform:
                mock_transform.return_value = {
                    "tx_hash": "0x123",
                    "value": Decimal("1.0"),
                }

                result = await fetch_transactions_with_retry("0x123", "eth")

                assert len(result) == 1
                assert result[0]["tx_hash"] == "0x123"

    @pytest.mark.asyncio
    async def test_fetch_transactions_with_retry_failure(self):
        """Test retry failure scenario."""
        from app.services.chain_sync import fetch_transactions_with_retry

        with patch(
            "app.services.chain_sync.fetch_transactions",
            side_effect=ChainSyncError("API error"),
        ):
            with pytest.raises(ChainSyncError):
                await fetch_transactions_with_retry("0x123", "eth", max_retries=2)

    def test_chain_configs_has_required_keys(self):
        """Test that chain configs have all required keys."""
        required_keys = {"base_url", "api_key", "rate_limit_delay"}

        for chain, config in CHAIN_CONFIGS.items():
            assert set(config.keys()) == required_keys, (
                f"Missing keys in {chain} config"
            )

    def test_rate_limit_delays_are_positive(self):
        """Test that rate limit delays are positive values."""
        for chain, config in CHAIN_CONFIGS.items():
            assert config["rate_limit_delay"] > 0, f"Invalid rate limit for {chain}"


class TestIntegration:
    """Integration tests (require API keys to be set)."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Etherscan API v1 deprecated - integration tests disabled")
    async def test_fetch_transactions_real_api(self):
        """Test actual API call (requires API keys)."""
        # This test will be skipped if API keys are not set
        if not settings.ETHERSCAN_API_KEY:
            pytest.skip("Etherscan API key not configured")

        # Test with a known address (Vitalik Buterin's address)
        test_address = "0x742d35Cc6634C893292Ce8bB6239C002Ad8e6b59"

        try:
            transactions = await fetch_transactions(test_address, "eth")

            # Should return some transactions
            assert isinstance(transactions, list)

            if transactions:  # If we got transactions, verify structure
                tx = transactions[0]
                assert "hash" in tx
                assert "from" in tx
                assert "to" in tx
                assert "value" in tx

        except ChainSyncError as e:
            # API might be rate limited, but shouldn't raise other errors
            if "rate limit" in str(e).lower() or "timeout" in str(e).lower():
                pytest.skip("API rate limited or timeout")
            else:
                raise


# Mock data for testing
def create_mock_evm_response():
    """Create mock EVM API response."""
    return {
        "status": "1",
        "message": "OK",
        "result": [
            {
                "hash": "0x123",
                "from": "0xfrom",
                "to": "0xto",
                "value": "1000000000000000000",
                "gasUsed": "21000",
                "gasPrice": "20000000000",
                "blockNumber": "123456",
                "timeStamp": "1614556800",
                "isError": "0",
                "contractAddress": "",
                "tokenSymbol": "",
                "tokenName": "",
                "tokenDecimal": "0",
            }
        ],
    }


def create_mock_solana_response():
    """Create mock Solana API response."""
    return [
        {
            "signature": "5xyz...",
            "source": "source_address",
            "destination": "dest_address",
            "amount": "1000000000",  # 1 SOL in lamports
            "fee": "5000",
            "blockTime": 1614556800,
            "slot": 123456,
            "instructions": [{"program": "11111111111111111111111111111111"}],
        }
    ]
