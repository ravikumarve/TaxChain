"""
Transaction Categorization Service

Classifies blockchain transactions into types:
- trade: Token swaps on DEXs
- transfer_in: Receiving tokens
- transfer_out: Sending tokens
- staking: Staking rewards or deposits
- airdrop: Free token distributions
- nft_sale: NFT purchases/sales
- fee: Network gas fees
"""

from typing import Dict, Any
from decimal import Decimal


class TransactionCategorizer:
    """Categorizes blockchain transactions based on patterns and heuristics."""

    # Common DEX router addresses
    DEX_ROUTERS = {
        "eth": {
            "uniswap_v2": "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",
            "uniswap_v3": "0xe592427a0aece92de3edee1f18e0157c05861564",
            "sushiswap": "0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f",
        },
        "bnb": {
            "pancakeswap_v2": "0x10ed43c718714eb63d5aa57b78b54704e256024e",
            "pancakeswap_v3": "0x13f4ea83d0bd40e75c8222255bc855a974568dd4",
        },
        "polygon": {
            "quickswap": "0xa5e0829caced8ffdd4de3c43696c57f7d7a678ff",
            "sushiswap": "0x1b02da8cb0d097eb8d57a175b88c7d8b47997506",
        },
        "arbitrum": {
            "uniswap_v3": "0xe592427a0aece92de3edee1f18e0157c05861564",
            "camelot": "0xc873fEcbd354f5A56E00E710B90EF4201db2448d",
            "sushiswap": "0x1b02da8cb0d097eb8d57a175b88c7d8b47997506",
        },
        "optimism": {
            "uniswap_v3": "0xe592427a0aece92de3edee1f18e0157c05861564",
            "velodrome": "0x9c12939390052919aF3155f41Bf4160Fd3666A6f",
            "sushiswap": "0x1b02da8cb0d097eb8d57a175b88c7d8b47997506",
        },
        "base": {
            "uniswap_v3": "0xe592427a0aece92de3edee1f18e0157c05861564",
            "aerodrome": "0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43",
            "sushiswap": "0x1b02da8cb0d097eb8d57a175b88c7d8b47997506",
        },
    }

    # Staking contract patterns
    STAKING_CONTRACTS = {
        "eth": {
            "lido": "0xae7ab96520de3a18e5e111b5eaab095312d7fe84",
            "rocketpool": "0xdd3f50f8a6cafbe9b31a427582963f465e745af",
        },
        "bnb": {
            "pancake_staking": "0x73feaa1ee314f8c655e354234017be2193c9e24e",
        },
    }

    # Airdrop contract patterns
    AIRDROP_CONTRACTS = {
        "eth": {
            "uniswap": "0x090d4613473dee047c3f2706764f49e0821d256e",
            "ens": "0xc18360217d8f7ab5e7c516566761ea12ce7f9d72",
        }
    }

    @staticmethod
    def categorize_ethereum_transaction(tx_data: Dict[str, Any]) -> str:
        """Categorize Ethereum transaction based on patterns."""

        # Check for fee transactions (gas fees)
        if (
            tx_data.get("gas_price")
            and tx_data.get("gas_used")
            and tx_data.get("value") == "0"
        ):
            if tx_data.get("to") and tx_data.get("input") == "0x":
                return "fee"

        # Check for NFT sales
        if tx_data.get("input", "").startswith("0x23b872dd"):  # transferFrom for ERC721
            if "nft" in tx_data.get("contract_name", "").lower():
                return "nft_sale"

        # Check for DEX trades
        to_address = tx_data.get("to", "").lower()
        for dex_name, router_address in TransactionCategorizer.DEX_ROUTERS[
            "eth"
        ].items():
            if to_address == router_address:
                return "trade"

        # Check for staking
        for staking_name, staking_address in TransactionCategorizer.STAKING_CONTRACTS[
            "eth"
        ].items():
            if to_address == staking_address:
                return "staking"

        # Check for airdrops
        for airdrop_name, airdrop_address in TransactionCategorizer.AIRDROP_CONTRACTS[
            "eth"
        ].items():
            if to_address == airdrop_address:
                return "airdrop"

        # Default to transfer classification
        value = Decimal(tx_data.get("value", "0"))
        if value > 0:
            return "transfer_out" if tx_data.get("from") else "transfer_in"

        return "transfer_in"  # Default fallback

    @staticmethod
    def categorize_bsc_transaction(tx_data: Dict[str, Any]) -> str:
        """Categorize BSC transaction based on patterns."""

        # Check for fee transactions
        if (
            tx_data.get("gas_price")
            and tx_data.get("gas_used")
            and tx_data.get("value") == "0"
        ):
            return "fee"

        # Check for DEX trades
        to_address = tx_data.get("to", "").lower()
        for dex_name, router_address in TransactionCategorizer.DEX_ROUTERS[
            "bnb"
        ].items():
            if to_address == router_address:
                return "trade"

        # Check for staking
        for staking_name, staking_address in TransactionCategorizer.STAKING_CONTRACTS[
            "bnb"
        ].items():
            if to_address == staking_address:
                return "staking"

        # Default to transfer classification
        value = Decimal(tx_data.get("value", "0"))
        if value > 0:
            return "transfer_out" if tx_data.get("from") else "transfer_in"

        return "transfer_in"

    @staticmethod
    def categorize_polygon_transaction(tx_data: Dict[str, Any]) -> str:
        """Categorize Polygon transaction based on patterns."""

        # Check for fee transactions
        if (
            tx_data.get("gas_price")
            and tx_data.get("gas_used")
            and tx_data.get("value") == "0"
        ):
            return "fee"

        # Check for DEX trades
        to_address = tx_data.get("to", "").lower()
        for dex_name, router_address in TransactionCategorizer.DEX_ROUTERS[
            "polygon"
        ].items():
            if to_address == router_address:
                return "trade"

        # Default to transfer classification
        value = Decimal(tx_data.get("value", "0"))
        if value > 0:
            return "transfer_out" if tx_data.get("from") else "transfer_in"

        return "transfer_in"

    @staticmethod
    def categorize_solana_transaction(tx_data: Dict[str, Any]) -> str:
        """Categorize Solana transaction based on patterns."""

        # Solana transaction structure is different
        fee = tx_data.get("fee")
        if fee and fee > 0:
            return "fee"

        # Check for transfer patterns
        if tx_data.get("type") == "transfer":
            return "transfer_out" if tx_data.get("source") else "transfer_in"

        # Check for swap patterns
        if tx_data.get("type") == "swap":
            return "trade"

        # Check for stake patterns
        if tx_data.get("type") == "stake":
            return "staking"

        return "transfer_in"  # Default fallback

    @staticmethod
    def categorize_transaction(chain: str, tx_data: Dict[str, Any]) -> str:
        """
        Main categorization method that routes to chain-specific categorizers.

        Args:
            chain: Blockchain identifier (eth, bnb, polygon, sol)
            tx_data: Raw transaction data from blockchain explorer

        Returns:
            Transaction type string
        """

        if not tx_data:
            return "transfer_in"  # Default fallback

        try:
            # EVM L2s (arbitrum, optimism, base) share Ethereum's DEX routers
            evm_l2_chains = {"arbitrum", "optimism", "base"}
            if chain == "eth" or chain in evm_l2_chains:
                return TransactionCategorizer.categorize_ethereum_transaction(tx_data)
            elif chain == "bnb":
                return TransactionCategorizer.categorize_bsc_transaction(tx_data)
            elif chain == "polygon":
                return TransactionCategorizer.categorize_polygon_transaction(tx_data)
            elif chain == "sol":
                return TransactionCategorizer.categorize_solana_transaction(tx_data)
            else:
                return "transfer_in"  # Unknown chain fallback

        except Exception as e:
            # Log error but don't fail
            logger.warning("Categorization error for chain %s: %s", chain, e)
            return "transfer_in"  # Safe fallback

    @staticmethod
    def is_known_dex(chain: str, address: str) -> bool:
        """Check if address is a known DEX router."""
        address = address.lower()
        if chain in TransactionCategorizer.DEX_ROUTERS:
            return address in TransactionCategorizer.DEX_ROUTERS[chain].values()
        return False

    @staticmethod
    def is_known_staking(chain: str, address: str) -> bool:
        """Check if address is a known staking contract."""
        address = address.lower()
        if chain in TransactionCategorizer.STAKING_CONTRACTS:
            return address in TransactionCategorizer.STAKING_CONTRACTS[chain].values()
        return False

    @staticmethod
    def is_known_airdrop(chain: str, address: str) -> bool:
        """Check if address is a known airdrop contract."""
        address = address.lower()
        if chain in TransactionCategorizer.AIRDROP_CONTRACTS:
            return address in TransactionCategorizer.AIRDROP_CONTRACTS[chain].values()
        return False
