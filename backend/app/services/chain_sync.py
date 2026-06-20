"""
Chain Sync Service
Fetches transactions from blockchain explorers for all supported chains.
EVM chains (Etherscan-compatible APIs): eth, bnb, polygon, arbitrum, optimism, base
Non-EVM: solana (Solscan), bitcoin (Blockstream)
"""

import httpx
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from decimal import Decimal
from app.config import settings
from app.constants import (
    EVM_CHAINS, CHAIN_SOLANA, CHAIN_BITCOIN,
    BTC_EXPLORER_URL, CHAIN_NATIVE_COINGECKO,
)
from app.services.defi_categoriser import DeFiCategorizer


class ChainSyncError(Exception):
    """Custom exception for chain sync errors."""
    pass


# ── EVM Chain Configs (Etherscan-compatible) ──────────────────────────────

EVM_CHAIN_CONFIGS = {
    "eth": {
        "base_url": "https://api.etherscan.io/api",
        "api_key": settings.ETHERSCAN_API_KEY,
        "rate_limit_delay": 0.2,
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
    "arbitrum": {
        "base_url": "https://api.arbiscan.io/api",
        "api_key": settings.ARBISCAN_API_KEY,
        "rate_limit_delay": 0.2,
    },
    "optimism": {
        "base_url": "https://api-optimistic.etherscan.io/api",
        "api_key": settings.OPTIMISM_API_KEY,
        "rate_limit_delay": 0.2,
    },
    "base": {
        "base_url": "https://api.basescan.org/api",
        "api_key": settings.BASESCAN_API_KEY,
        "rate_limit_delay": 0.2,
    },
}

# Non-EVM configs
SOLANA_CONFIG = {
    "base_url": "https://public-api.solscan.io/",
    "api_key": settings.SOLSCAN_API_KEY,
    "rate_limit_delay": 2.0,
}


# ── Main Fetch Entrypoint ─────────────────────────────────────────────────

async def fetch_transactions(address: str, chain: str) -> List[Dict[str, Any]]:
    """
    Fetch transactions for a wallet address from the specified blockchain.
    Routes to the correct fetcher based on chain type.
    """
    if chain in EVM_CHAIN_CONFIGS:
        return await _fetch_evm_transactions(address, EVM_CHAIN_CONFIGS[chain])

    if chain == CHAIN_SOLANA:
        return await _fetch_solana_transactions(address, SOLANA_CONFIG)

    if chain == CHAIN_BITCOIN:
        return await _fetch_bitcoin_transactions(address)

    raise ChainSyncError(f"Unsupported chain: {chain}")


# ── EVM Chain Fetcher ─────────────────────────────────────────────────────

async def _fetch_evm_transactions(
    address: str, config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Fetch transactions from Etherscan-compatible APIs."""
    async with httpx.AsyncClient() as client:
        normal_txs = await _fetch_evm_type(client, address, config, "txlist")
        token_txs = await _fetch_evm_type(client, address, config, "tokentx")
        internal_txs = await _fetch_evm_type(client, address, config, "txlistinternal")
        await asyncio.sleep(config["rate_limit_delay"])
        return normal_txs + token_txs + internal_txs


async def _fetch_evm_type(
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
        return data.get("result", [])
    except httpx.RequestError as e:
        raise ChainSyncError(f"Network error: {e}")
    except ValueError as e:
        raise ChainSyncError(f"Invalid JSON response: {e}")


# ── Solana Fetcher ────────────────────────────────────────────────────────

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
        resp = await client.get(
            f"{config['base_url']}account/transactions",
            params={"account": address, "limit": 10000},
            headers=headers,
        )
        if resp.status_code != 200:
            raise ChainSyncError(f"Solscan API error: {resp.status_code}")
        await asyncio.sleep(config["rate_limit_delay"])
        return resp.json()


# ── Bitcoin Fetcher (UTXO model) ──────────────────────────────────────────

async def _fetch_bitcoin_transactions(address: str) -> List[Dict[str, Any]]:
    """Fetch transactions for a Bitcoin address via Blockstream API."""
    async with httpx.AsyncClient() as client:
        # Get TX history for address
        resp = await client.get(
            f"{BTC_EXPLORER_URL}/address/{address}/txs",
            params={"limit": 50},  # paginate if needed
        )
        if resp.status_code != 200:
            raise ChainSyncError(
                f"Blockstream API error: {resp.status_code}"
            )
        txs = resp.json()

        # Enrich each TX with address-specific details
        enriched = []
        for tx in txs:
            txid = tx.get("txid", "")
            # Get detailed TX info
            detail_resp = await client.get(
                f"{BTC_EXPLORER_URL}/tx/{txid}"
            )
            if detail_resp.status_code == 200:
                detail = detail_resp.json()
                enriched.append({
                    "tx_hash": txid,
                    "address": address,
                    "detail": detail,
                })
            await asyncio.sleep(0.1)  # rate limit

        return enriched


# ── Transaction Transformers ──────────────────────────────────────────────

def transform_transaction(tx: Dict[str, Any], chain: str) -> Dict[str, Any]:
    """Transform raw API transaction to standardized format."""
    if chain == CHAIN_SOLANA:
        return _transform_solana_tx(tx)
    if chain == CHAIN_BITCOIN:
        return _transform_bitcoin_tx(tx)
    return _transform_evm_tx(tx, chain)


def _transform_evm_tx(tx: Dict[str, Any], chain: str) -> Dict[str, Any]:
    """Transform EVM transaction to standardized format."""
    native_symbol = {
        "eth": "ETH", "bnb": "BNB", "polygon": "MATIC",
        "arbitrum": "ETH", "optimism": "ETH", "base": "ETH",
    }.get(chain, "ETH")

    return {
        "tx_hash": tx.get("hash", ""),
        "chain": chain,
        "from_address": tx.get("from", ""),
        "to_address": tx.get("to", ""),
        "value": Decimal(tx.get("value", 0)) / Decimal("1e18"),
        "gas_used": int(tx.get("gasUsed", 0)),
        "gas_price": int(tx.get("gasPrice", 0)),
        "block_number": int(tx.get("blockNumber", 0)),
        "timestamp": datetime.fromtimestamp(int(tx.get("timeStamp", 0))),
        "is_error": tx.get("isError") == "1",
        "tx_type": _determine_evm_tx_type(tx),
        "token_symbol": tx.get("tokenSymbol", native_symbol),
        "token_name": tx.get("tokenName", native_symbol),
        "token_decimal": int(tx.get("tokenDecimal", 18)) if tx.get("tokenDecimal") else 18,
        "contract_address": tx.get("contractAddress", ""),
        "raw_data": tx,
    }


def _transform_solana_tx(tx: Dict[str, Any]) -> Dict[str, Any]:
    """Transform Solana transaction to standardized format."""
    return {
        "tx_hash": tx.get("signature", ""),
        "chain": "sol",
        "from_address": tx.get("source", ""),
        "to_address": tx.get("destination", ""),
        "value": Decimal(tx.get("amount", 0)) / Decimal("1e9"),
        "fee": Decimal(tx.get("fee", 0)) / Decimal("1e9"),
        "block_time": datetime.fromtimestamp(tx.get("blockTime", 0)),
        "slot": tx.get("slot", 0),
        "tx_type": _determine_solana_tx_type(tx),
        "raw_data": tx,
    }


def _transform_bitcoin_tx(tx: Dict[str, Any]) -> Dict[str, Any]:
    """Transform Bitcoin transaction to standardized format."""
    detail = tx.get("detail", {})
    address = tx.get("address", "")

    # Calculate net value for this address
    vin_sum = sum(
        Decimal(inp.get("prevout", {}).get("value", 0))
        for inp in detail.get("vin", [])
        if inp.get("prevout", {}).get("scriptpubkey_address") == address
    )
    vout_sum = sum(
        Decimal(out.get("value", 0))
        for out in detail.get("vout", [])
        if out.get("scriptpubkey_address") == address
    )

    # Determine direction
    if vout_sum > vin_sum:
        value = vout_sum - vin_sum  # receiving
        tx_type = "transfer_in"
    else:
        value = vin_sum - vout_sum  # sending (change stays)
        tx_type = "transfer_out"

    return {
        "tx_hash": tx.get("tx_hash", ""),
        "chain": "btc",
        "from_address": address,
        "to_address": address,
        "value": Decimal(value),
        "fee": Decimal(detail.get("fee", 0)),
        "block_time": datetime.fromtimestamp(detail.get("status", {}).get("block_time", 0)),
        "block_number": detail.get("status", {}).get("block_height", 0),
        "tx_type": tx_type,
        "token_symbol": "BTC",
        "token_name": "Bitcoin",
        "raw_data": tx,
    }


# ── Type Determination ─────────────────────────────────────────────────────

def _determine_evm_tx_type(tx: Dict[str, Any]) -> str:
    # Check DeFi categorizer first
    defi_type = DeFiCategorizer.classify(tx, tx.get("chain", "eth"))
    if defi_type:
        return defi_type

    if tx.get("contractAddress"):
        return "token_transfer" if tx.get("value") == "0" else "token_swap"
    elif tx.get("isError") == "1":
        return "failed"
    elif tx.get("to") == "":
        return "contract_creation"
    return "transfer"


def _determine_solana_tx_type(tx: Dict[str, Any]) -> str:
    instructions = tx.get("instructions", [])
    if any(inst.get("program") == "tokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA" for inst in instructions):
        return "token_transfer"
    if any(inst.get("program") == "11111111111111111111111111111111" for inst in instructions):
        return "transfer"
    if any(inst.get("program") == "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTAnL8hJb1B" for inst in instructions):
        return "token_account_creation"
    return "program_interaction"


# ── Retry Wrapper ─────────────────────────────────────────────────────────

async def fetch_transactions_with_retry(
    address: str, chain: str, max_retries: int = 3, retry_delay: float = 1.0
) -> List[Dict[str, Any]]:
    """Fetch transactions with retry logic for reliability."""
    for attempt in range(max_retries):
        try:
            raw_txs = await fetch_transactions(address, chain)
            return [transform_transaction(tx, chain) for tx in raw_txs]
        except ChainSyncError:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(retry_delay * (attempt + 1))
    return []


# ── Address Validation ────────────────────────────────────────────────────

def validate_address(address: str, chain: str) -> bool:
    """Validate wallet address format for the given chain."""
    import re
    from app.constants import CHAIN_ADDRESS_PATTERNS

    pattern = CHAIN_ADDRESS_PATTERNS.get(chain)
    if not pattern:
        return False
    return bool(re.match(pattern, address))
