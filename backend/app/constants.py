"""
Centralized blockchain constants for TaxChain.
Single source of truth for chain configs, address validation, and pricing IDs.
"""

from typing import Dict, Set

# ── Supported Chains ──────────────────────────────────────────────────────
# EVM L1s
CHAIN_ETH = "eth"
CHAIN_BNB = "bnb"
CHAIN_POLYGON = "polygon"
# EVM L2s
CHAIN_ARBITRUM = "arbitrum"
CHAIN_OPTIMISM = "optimism"
CHAIN_BASE = "base"
# Non-EVM
CHAIN_SOLANA = "sol"
CHAIN_BITCOIN = "btc"

ALL_CHAINS: Set[str] = {
    CHAIN_ETH, CHAIN_BNB, CHAIN_POLYGON,
    CHAIN_ARBITRUM, CHAIN_OPTIMISM, CHAIN_BASE,
    CHAIN_SOLANA, CHAIN_BITCOIN,
}

# EVM-compatible chains (share Etherscan-like API pattern)
EVM_CHAINS: Set[str] = {
    CHAIN_ETH, CHAIN_BNB, CHAIN_POLYGON,
    CHAIN_ARBITRUM, CHAIN_OPTIMISM, CHAIN_BASE,
}

# ── Chain Display Names ───────────────────────────────────────────────────
CHAIN_DISPLAY_NAMES = {
    CHAIN_ETH: "Ethereum",
    CHAIN_BNB: "BNB Chain",
    CHAIN_POLYGON: "Polygon",
    CHAIN_ARBITRUM: "Arbitrum",
    CHAIN_OPTIMISM: "Optimism",
    CHAIN_BASE: "Base",
    CHAIN_SOLANA: "Solana",
    CHAIN_BITCOIN: "Bitcoin",
}

# ── Address Validation Regex ──────────────────────────────────────────────
CHAIN_ADDRESS_PATTERNS = {
    CHAIN_ETH: r"^0x[a-fA-F0-9]{40}$",
    CHAIN_BNB: r"^0x[a-fA-F0-9]{40}$",
    CHAIN_POLYGON: r"^0x[a-fA-F0-9]{40}$",
    CHAIN_ARBITRUM: r"^0x[a-fA-F0-9]{40}$",
    CHAIN_OPTIMISM: r"^0x[a-fA-F0-9]{40}$",
    CHAIN_BASE: r"^0x[a-fA-F0-9]{40}$",
    CHAIN_SOLANA: r"^[1-9A-HJ-NP-Za-km-z]{32,44}$",
    # Bitcoin: legacy P2PKH, P2SH, and bech32
    CHAIN_BITCOIN: r"^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,62}$",
}

# ── Plan Chain Access ─────────────────────────────────────────────────────
# Which chains each plan tier can access
PLAN_CHAINS = {
    "free": {CHAIN_ETH},
    "starter": {CHAIN_ETH, CHAIN_BNB, CHAIN_POLYGON, CHAIN_ARBITRUM},
    "pro": {
        CHAIN_ETH, CHAIN_BNB, CHAIN_POLYGON,
        CHAIN_ARBITRUM, CHAIN_OPTIMISM, CHAIN_BASE,
        CHAIN_SOLANA, CHAIN_BITCOIN,
    },
}

# ── CoinGecko IDs for Native Tokens ──────────────────────────────────────
CHAIN_NATIVE_COINGECKO = {
    CHAIN_ETH: "ethereum",
    CHAIN_BNB: "binancecoin",
    CHAIN_POLYGON: "matic-network",
    CHAIN_ARBITRUM: "ethereum",       # ARB uses ETH for gas
    CHAIN_OPTIMISM: "ethereum",       # OP uses ETH for gas
    CHAIN_BASE: "ethereum",           # Base uses ETH for gas
    CHAIN_SOLANA: "solana",
    CHAIN_BITCOIN: "bitcoin",
}

# ── BTC Explorer (UTXO model — different from EVM) ───────────────────────
BTC_EXPLORER_URL = "https://blockstream.info/api"
