"""
Chain Sync Service
Fetches transactions from blockchain explorers (Etherscan, BscScan,
PolygonScan, Solscan) with proper rate limiting and error handling.
"""

import httpx
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from decimal import Decimal
from app.config import settings


class ChainSyncError(Exception):
    """Custom exception for chain sync errors."""

    pass


# Chain configurations from AGENTS.md
CHAIN_CONFIGS = {
    "eth": {
        "base_url": "https://api.etherscan.io/api",
        "api_key": settings.ETHERSCAN_API_KEY,
        "rate_limit_delay": 0.2,  # 200ms delay for Etherscan (5 req/sec)
    },
    "bnb": {
        "base_url": "https://api.bscscan.com/api",
        "api_key": settings.BSCSCAN_API_KEY,
        "rate_limit_delay": 0.2,
    },
    "polygon": {
        "base_url": "https://api.polygonscan.com/api",
        "api_key": settings.POLYGONSCAN_API_KEY,
        "rate_limit_delay": 0.2,
    },
    "sol": {
        "base_url": "https://public-api.solscan.io/",
        "api_key": settings.SOLSCAN_API_KEY,
        "rate_limit_delay": 2.0,  # 2s delay for Solscan (more restrictive)
    },
}


async def fetch_transactions(address: str, chain: str) -> List[Dict[str, Any]]:
    """
    Fetch transactions for a wallet address from the specified blockchain.

    Args:
        address: Wallet address
        chain: Blockchain identifier ('eth', 'bnb', 'polygon', 'sol')

    Returns:
        List of transaction dictionaries

    Raises:
        ChainSyncError: If chain not supported or API call fails
    """
    if chain not in CHAIN_CONFIGS:
        raise ChainSyncError(f"Unsupported chain: {chain}")

    config = CHAIN_CONFIGS[chain]

    try:
        if chain == "sol":
            # Solscan has different API structure
            transactions = await _fetch_solana_transactions(address, config)
        else:
            # EVM chains (Etherscan-compatible APIs)
            transactions = await _fetch_evm_transactions(address, config)

        return transactions

    except httpx.RequestError as e:
        raise ChainSyncError(f"Network error fetching transactions: {e}")
    except Exception as e:
        raise ChainSyncError(f"Unexpected error: {e}")


async def _fetch_evm_transactions(
    address: str, config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Fetch transactions from Etherscan-compatible APIs."""
    async with httpx.AsyncClient() as client:
        # Normal transactions
        normal_txs = await _fetch_evm_transaction_type(
            client, address, config, "txlist"
        )

        # ERC-20 token transfers
        token_txs = await _fetch_evm_transaction_type(
            client, address, config, "tokentx"
        )

        # Internal transactions (optional)
        internal_txs = await _fetch_evm_transaction_type(
            client, address, config, "txlistinternal"
        )

        # Apply rate limiting
        await asyncio.sleep(config["rate_limit_delay"])

        return normal_txs + token_txs + internal_txs


async def _fetch_evm_transaction_type(
    client: httpx.AsyncClient, address: str, config: Dict[str, Any], action: str
) -> List[Dict[str, Any]]:
    """Fetch specific transaction type from EVM chain."""
    try:
        resp = await client.get(
            config["base_url"],
            params={
                "module": "account",
                "action": action,
                "address": address,
                "startblock": 0,
                "endblock": 99999999,
                "sort": "asc",
                "apikey": config["api_key"],
            },
        )

        if resp.status_code != 200:
            raise ChainSyncError(f"API error: {resp.status_code} - {resp.text}")

        data = resp.json()
        if data.get("status") != "1" or data.get("message") != "OK":
            raise ChainSyncError(f"API response error: {data}")

        return data.get("result", [])

    except httpx.RequestError as e:
        raise ChainSyncError(f"Network error: {e}")
    except ValueError as e:
        raise ChainSyncError(f"Invalid JSON response: {e}")


async def _fetch_solana_transactions(
    address: str, config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Fetch transactions from Solscan API."""
    async with httpx.AsyncClient() as client:
        headers = (
            {"Authorization": f"Bearer {config['api_key']}"}
            if config["api_key"]
            else {}
        )

        # Solscan transactions endpoint
        resp = await client.get(
            f"{config['base_url']}account/transactions",
            params={"account": address, "limit": 10000},
            headers=headers,
        )

        if resp.status_code != 200:
            raise ChainSyncError(f"Solscan API error: {resp.status_code} - {resp.text}")

        data = resp.json()

        # Apply rate limiting
        await asyncio.sleep(config["rate_limit_delay"])

        return data


def transform_transaction(tx: Dict[str, Any], chain: str) -> Dict[str, Any]:
    """
    Transform raw API transaction to standardized format.

    Args:
        tx: Raw transaction from blockchain API
        chain: Blockchain identifier

    Returns:
        Standardized transaction dictionary
    """
    if chain == "sol":
        return _transform_solana_transaction(tx)
    else:
        return _transform_evm_transaction(tx, chain)


def _transform_evm_transaction(tx: Dict[str, Any], chain: str) -> Dict[str, Any]:
    """Transform EVM transaction to standardized format."""
    return {
        "tx_hash": tx.get("hash", ""),
        "chain": chain,
        "from_address": tx.get("from", ""),
        "to_address": tx.get("to", ""),
        "value": Decimal(tx.get("value", 0)) / Decimal("1e18"),  # Convert from wei
        "gas_used": int(tx.get("gasUsed", 0)),
        "gas_price": int(tx.get("gasPrice", 0)),
        "block_number": int(tx.get("blockNumber", 0)),
        "timestamp": datetime.fromtimestamp(int(tx.get("timeStamp", 0))),
        "is_error": tx.get("isError") == "1",
        "tx_type": _determine_evm_tx_type(tx),
        "token_symbol": tx.get("tokenSymbol", ""),
        "token_name": tx.get("tokenName", ""),
        "token_decimal": int(tx.get("tokenDecimal", 0)),
        "contract_address": tx.get("contractAddress", ""),
        "raw_data": tx,  # Keep original data for audit
    }


def _transform_solana_transaction(tx: Dict[str, Any]) -> Dict[str, Any]:
    """Transform Solana transaction to standardized format."""
    return {
        "tx_hash": tx.get("signature", ""),
        "chain": "sol",
        "from_address": tx.get("source", ""),
        "to_address": tx.get("destination", ""),
        "value": Decimal(tx.get("amount", 0)) / Decimal("1e9"),  # Convert from lamports
        "fee": Decimal(tx.get("fee", 0)) / Decimal("1e9"),
        "block_time": datetime.fromtimestamp(tx.get("blockTime", 0)),
        "slot": tx.get("slot", 0),
        "tx_type": _determine_solana_tx_type(tx),
        "raw_data": tx,
    }


def _determine_evm_tx_type(tx: Dict[str, Any]) -> str:
    """Determine transaction type for EVM chains."""
    if tx.get("contractAddress"):
        # Token transfer
        if tx.get("value") == "0":
            return "token_transfer"
        else:
            return "token_swap"
    elif tx.get("isError") == "1":
        return "failed"
    elif tx.get("to") == "":  # Contract creation
        return "contract_creation"
    else:
        return "transfer"


def _determine_solana_tx_type(tx: Dict[str, Any]) -> str:
    """Determine transaction type for Solana."""
    instructions = tx.get("instructions", [])

    if any(
        inst.get("program") == "tokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
        for inst in instructions
    ):
        return "token_transfer"
    elif any(
        inst.get("program") == "11111111111111111111111111111111"
        for inst in instructions
    ):
        return "transfer"
    elif any(
        inst.get("program") == "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTAnL8hJb1B"
        for inst in instructions
    ):
        return "token_account_creation"
    else:
        return "program_interaction"


async def fetch_transactions_with_retry(
    address: str, chain: str, max_retries: int = 3, retry_delay: float = 1.0
) -> List[Dict[str, Any]]:
    """
    Fetch transactions with retry logic for reliability.

    Args:
        address: Wallet address
        chain: Blockchain identifier
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        List of standardized transactions
    """
    for attempt in range(max_retries):
        try:
            raw_txs = await fetch_transactions(address, chain)
            transformed_txs = [transform_transaction(tx, chain) for tx in raw_txs]
            return transformed_txs

        except ChainSyncError:
            if attempt == max_retries - 1:
                raise

            await asyncio.sleep(retry_delay * (attempt + 1))

    return []  # Should never reach here


# Test utility function
def validate_address(address: str, chain: str) -> bool:
    """
    Validate wallet address format for the given chain.

    Args:
        address: Wallet address to validate
        chain: Blockchain identifier

    Returns:
        True if address format is valid for the chain
    """
    import re

    patterns = {
        "eth": r"^0x[a-fA-F0-9]{40}$",
        "bnb": r"^0x[a-fA-F0-9]{40}$",
        "polygon": r"^0x[a-fA-F0-9]{40}$",
        "sol": r"^[1-9A-HJ-NP-Za-km-z]{32,44}$",
    }

    if chain not in patterns:
        return False

    return bool(re.match(patterns[chain], address))
