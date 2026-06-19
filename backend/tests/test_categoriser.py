"""
Tests for Transaction Categorization Service
"""

import pytest
from decimal import Decimal
from app.services.categoriser import TransactionCategorizer


class TestTransactionCategorizer:
    """Test suite for transaction categorization."""

    def test_ethereum_fee_transaction(self):
        """Test Ethereum gas fee categorization."""
        tx_data = {
            "gas_price": "20000000000",
            "gas_used": "21000",
            "value": "0",
            "to": "0x742d35cc6634c0532925a3b844bc454e4438f44e",
            "input": "0x",
        }

        result = TransactionCategorizer.categorize_ethereum_transaction(tx_data)
        assert result == "fee"

    def test_ethereum_dex_trade(self):
        """Test Ethereum DEX trade categorization."""
        tx_data = {
            "to": "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",  # Uniswap V2
            "value": "1000000000000000000",  # 1 ETH
            "input": "0x...swap...",
        }

        result = TransactionCategorizer.categorize_ethereum_transaction(tx_data)
        assert result == "trade"

    def test_ethereum_staking(self):
        """Test Ethereum staking categorization."""
        tx_data = {
            "to": "0xae7ab96520de3a18e5e111b5eaab095312d7fe84",  # Lido
            "value": "1000000000000000000",  # 1 ETH
            "input": "0x...stake...",
        }

        result = TransactionCategorizer.categorize_ethereum_transaction(tx_data)
        assert result == "staking"

    def test_ethereum_transfer_out(self):
        """Test Ethereum transfer out categorization."""
        tx_data = {
            "from": "0x1234567890123456789012345678901234567890",
            "to": "0x9876543210987654321098765432109876543210",
            "value": "1000000000000000000",  # 1 ETH
        }

        result = TransactionCategorizer.categorize_ethereum_transaction(tx_data)
        assert result == "transfer_out"

    def test_ethereum_transfer_in(self):
        """Test Ethereum transfer in categorization."""
        tx_data = {
            "to": "0x1234567890123456789012345678901234567890",
            "value": "1000000000000000000",  # 1 ETH
        }

        result = TransactionCategorizer.categorize_ethereum_transaction(tx_data)
        assert result == "transfer_in"

    def test_bsc_fee_transaction(self):
        """Test BSC gas fee categorization."""
        tx_data = {"gas_price": "5000000000", "gas_used": "21000", "value": "0"}

        result = TransactionCategorizer.categorize_bsc_transaction(tx_data)
        assert result == "fee"

    def test_bsc_dex_trade(self):
        """Test BSC DEX trade categorization."""
        tx_data = {
            "to": "0x10ed43c718714eb63d5aa57b78b54704e256024e",  # PancakeSwap V2
            "value": "1000000000000000000",  # 1 BNB
            "input": "0x...swap...",
        }

        result = TransactionCategorizer.categorize_bsc_transaction(tx_data)
        assert result == "trade"

    def test_polygon_fee_transaction(self):
        """Test Polygon gas fee categorization."""
        tx_data = {"gas_price": "30000000000", "gas_used": "21000", "value": "0"}

        result = TransactionCategorizer.categorize_polygon_transaction(tx_data)
        assert result == "fee"

    def test_polygon_dex_trade(self):
        """Test Polygon DEX trade categorization."""
        tx_data = {
            "to": "0xa5e0829caced8ffdd4de3c43696c57f7d7a678ff",  # QuickSwap
            "value": "1000000000000000000",  # 1 MATIC
            "input": "0x...swap...",
        }

        result = TransactionCategorizer.categorize_polygon_transaction(tx_data)
        assert result == "trade"

    def test_solana_fee_transaction(self):
        """Test Solana fee categorization."""
        tx_data = {
            "fee": 5000,  # 0.000005 SOL
            "type": "transfer",
        }

        result = TransactionCategorizer.categorize_solana_transaction(tx_data)
        assert result == "fee"

    def test_solana_transfer(self):
        """Test Solana transfer categorization."""
        tx_data = {
            "type": "transfer",
            "source": "Wallet123",
            "destination": "Wallet456",
            "amount": 1000000000,  # 1 SOL
        }

        result = TransactionCategorizer.categorize_solana_transaction(tx_data)
        assert result == "transfer_out"

    def test_solana_swap(self):
        """Test Solana swap categorization."""
        tx_data = {
            "type": "swap",
            "input_token": "SOL",
            "output_token": "USDC",
            "amount": 1000000000,  # 1 SOL
        }

        result = TransactionCategorizer.categorize_solana_transaction(tx_data)
        assert result == "trade"

    def test_main_categorizer_eth(self):
        """Test main categorizer with Ethereum data."""
        tx_data = {
            "to": "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",  # Uniswap V2
            "value": "1000000000000000000",
        }

        result = TransactionCategorizer.categorize_transaction("eth", tx_data)
        assert result == "trade"

    def test_main_categorizer_bnb(self):
        """Test main categorizer with BSC data."""
        tx_data = {
            "to": "0x10ed43c718714eb63d5aa57b78b54704e256024e",  # PancakeSwap V2
            "value": "1000000000000000000",
        }

        result = TransactionCategorizer.categorize_transaction("bnb", tx_data)
        assert result == "trade"

    def test_main_categorizer_polygon(self):
        """Test main categorizer with Polygon data."""
        tx_data = {
            "to": "0xa5e0829caced8ffdd4de3c43696c57f7d7a678ff",  # QuickSwap
            "value": "1000000000000000000",
        }

        result = TransactionCategorizer.categorize_transaction("polygon", tx_data)
        assert result == "trade"

    def test_main_categorizer_sol(self):
        """Test main categorizer with Solana data."""
        tx_data = {"type": "swap", "input_token": "SOL", "output_token": "USDC"}

        result = TransactionCategorizer.categorize_transaction("sol", tx_data)
        assert result == "trade"

    def test_main_categorizer_unknown_chain(self):
        """Test main categorizer with unknown chain."""
        tx_data = {"value": "1000000000000000000"}

        result = TransactionCategorizer.categorize_transaction("unknown", tx_data)
        assert result == "transfer_in"  # Default fallback

    def test_main_categorizer_empty_data(self):
        """Test main categorizer with empty data."""
        result = TransactionCategorizer.categorize_transaction("eth", {})
        assert result == "transfer_in"  # Default fallback

    def test_is_known_dex(self):
        """Test known DEX address detection."""
        # Test Ethereum
        assert TransactionCategorizer.is_known_dex(
            "eth", "0x7a250d5630b4cf539739df2c5dacb4c659f2488d"
        )
        assert not TransactionCategorizer.is_known_dex(
            "eth", "0x1234567890123456789012345678901234567890"
        )

        # Test BSC
        assert TransactionCategorizer.is_known_dex(
            "bnb", "0x10ed43c718714eb63d5aa57b78b54704e256024e"
        )

        # Test unknown chain
        assert not TransactionCategorizer.is_known_dex(
            "unknown", "0x1234567890123456789012345678901234567890"
        )

    def test_is_known_staking(self):
        """Test known staking contract detection."""
        # Test Ethereum
        assert TransactionCategorizer.is_known_staking(
            "eth", "0xae7ab96520de3a18e5e111b5eaab095312d7fe84"
        )
        assert not TransactionCategorizer.is_known_staking(
            "eth", "0x1234567890123456789012345678901234567890"
        )

    def test_is_known_airdrop(self):
        """Test known airdrop contract detection."""
        # Test Ethereum
        assert TransactionCategorizer.is_known_airdrop(
            "eth", "0x090d4613473dee047c3f2706764f49e0821d256e"
        )
        assert not TransactionCategorizer.is_known_airdrop(
            "eth", "0x1234567890123456789012345678901234567890"
        )

    def test_error_handling(self):
        """Test that categorizer handles errors gracefully."""
        # Invalid data that should cause errors
        tx_data = {"value": "invalid"}

        # Should not raise exception
        result = TransactionCategorizer.categorize_transaction("eth", tx_data)
        assert result == "transfer_in"  # Default fallback

    def test_edge_case_zero_value(self):
        """Test transactions with zero value."""
        tx_data = {"value": "0", "to": "0x1234567890123456789012345678901234567890"}

        result = TransactionCategorizer.categorize_ethereum_transaction(tx_data)
        assert result == "transfer_in"  # Default for zero value

    def test_edge_case_missing_fields(self):
        """Test transactions with missing fields."""
        tx_data = {}  # Empty data

        result = TransactionCategorizer.categorize_ethereum_transaction(tx_data)
        assert result == "transfer_in"  # Default fallback
