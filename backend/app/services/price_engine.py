"""
CoinGecko Price Engine Service
Provides historical price lookups for crypto tokens with caching.
"""

import logging
import httpx
import asyncio
from datetime import datetime
from functools import lru_cache
from typing import Optional, Dict, Tuple
from decimal import Decimal

from app.config import settings
from app.utils.cache import async_lru_cache

logger = logging.getLogger(__name__)

# CoinGecko token ID mapping (uppercase symbols)
COINGECKO_IDS = {
    "ETH": "ethereum",
    "BNB": "binancecoin",
    "MATIC": "matic-network",
    "SOL": "solana",
    "BTC": "bitcoin",
    "USDT": "tether",
    "USDC": "usd-coin",
    "DAI": "dai",
    "LINK": "chainlink",
    "UNI": "uniswap",
    "AAVE": "aave",
    "MKR": "maker",
    "COMP": "compound-governance-token",
    "SNX": "havven",
    "YFI": "yearn-finance",
    "CRV": "curve-dao-token",
    "SUSHI": "sushi",
    "ARB": "arbitrum",
    "OP": "optimism",
    "1INCH": "1inch",
    "BAL": "balancer",
    "REN": "republic-protocol",
    "KNC": "kyber-network-crystal",
    "BAT": "basic-attention-token",
    "ZRX": "0x",
    "OMG": "omisego",
    "ENJ": "enjincoin",
    "MANA": "decentraland",
    "SAND": "the-sandbox",
    "AXS": "axie-infinity",
    "CHZ": "chiliz",
    "FTT": "ftx-token",
    "HT": "huobi-token",
    "OKB": "okb",
    "LEO": "leo-token",
    "CRO": "crypto-com-chain",
    "NEXO": "nexo",
    "CEL": "celsius-degree-token",
    "NEO": "neo",
    "ETC": "ethereum-classic",
    "XRP": "ripple",
    "XLM": "stellar",
    "ADA": "cardano",
    "DOT": "polkadot",
    "AVAX": "avalanche-2",
    "ATOM": "cosmos",
    "ALGO": "algorand",
    "FIL": "filecoin",
    "ICP": "internet-computer",
    "XTZ": "tezos",
    "EOS": "eos",
    "TRX": "tron",
    "VET": "vechain",
    "THETA": "theta-token",
    "DOGE": "dogecoin",
    "SHIB": "shiba-inu",
    "LTC": "litecoin",
    "BCH": "bitcoin-cash",
    "BSV": "bitcoin-sv",
    "XMR": "monero",
    "ZEC": "zcash",
    "DASH": "dash",
}

# Additional common stablecoins
STABLECOINS = {"USDT", "USDC", "DAI", "BUSD", "TUSD", "USDP", "USDD", "FRAX", "LUSD"}


class PriceEngineError(Exception):
    """Custom exception for price engine errors."""

    pass


@async_lru_cache(maxsize=10000)
async def get_historical_price(
    token_symbol: str, date: datetime, coingecko_api_key: Optional[str] = None
) -> Decimal:
    """
    Get historical price for a token on a specific date.

    Args:
        token_symbol: Token symbol (e.g., 'ETH', 'BTC')
        date: Date for historical price lookup
        coingecko_api_key: Optional API key for CoinGecko Pro

    Returns:
        Decimal: Price in USD at the given date

    Raises:
        PriceEngineError: If token not found or API error
    """
    token_symbol_upper = token_symbol.upper()

    # Handle stablecoins - return $1.00
    if token_symbol_upper in STABLECOINS:
        return Decimal("1.00")

    coin_id = COINGECKO_IDS.get(token_symbol_upper)
    if not coin_id:
        logger.warning(
            "Unknown token symbol: %s — returning $0.00. "
            "Flag for user manual price input.",
            token_symbol,
        )
        return Decimal("0")

    date_str = date.strftime("%d-%m-%Y")  # CoinGecko format

    # Use free API by default, Pro API if key provided
    if coingecko_api_key:
        base_url = "https://pro-api.coingecko.com/api/v3"
        headers = {"X-CG-Pro-API-Key": coingecko_api_key}
    else:
        base_url = "https://api.coingecko.com/api/v3"
        headers = {}

    url = f"{base_url}/coins/{coin_id}/history"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url,
                params={"date": date_str, "localization": "false"},
                headers=headers,
                timeout=30.0,
            )

            if resp.status_code != 200:
                raise PriceEngineError(
                    f"CoinGecko API error: {resp.status_code} - {resp.text}"
                )

            data = resp.json()

            # Check if market data is available
            market_data = data.get("market_data", {})
            current_price = market_data.get("current_price", {})
            price_usd = current_price.get("usd")

            if price_usd is None:
                logger.warning(
                    "No price data for %s on %s", token_symbol, date_str
                )
                return Decimal("0")

            # Add small delay to respect rate limits
            await asyncio.sleep(0.2)  # 5 requests per second for free tier

            return Decimal(str(price_usd))

    except httpx.RequestError as e:
        raise PriceEngineError(f"Network error fetching price: {e}")
    except ValueError as e:
        raise PriceEngineError(f"Invalid JSON response: {e}")
    except Exception as e:
        raise PriceEngineError(f"Unexpected error: {e}")


async def get_current_price(
    token_symbol: str, coingecko_api_key: Optional[str] = None
) -> Decimal:
    """
    Get current price for a token.

    Args:
        token_symbol: Token symbol (e.g., 'ETH', 'BTC')
        coingecko_api_key: Optional API key for CoinGecko Pro

    Returns:
        Decimal: Current price in USD
    """
    token_symbol_upper = token_symbol.upper()

    # Handle stablecoins - return $1.00
    if token_symbol_upper in STABLECOINS:
        return Decimal("1.00")

    coin_id = COINGECKO_IDS.get(token_symbol_upper)
    if not coin_id:
        logger.warning(
            "Unknown token symbol (current price): %s — returning $0.00",
            token_symbol,
        )
        return Decimal("0")

    # Use free API by default, Pro API if key provided
    if coingecko_api_key:
        base_url = "https://pro-api.coingecko.com/api/v3"
        headers = {"X-CG-Pro-API-Key": coingecko_api_key}
    else:
        base_url = "https://api.coingecko.com/api/v3"
        headers = {}

    url = f"{base_url}/simple/price"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url,
                params={"ids": coin_id, "vs_currencies": "usd"},
                headers=headers,
                timeout=30.0,
            )

            if resp.status_code != 200:
                raise PriceEngineError(
                    f"CoinGecko API error: {resp.status_code} - {resp.text}"
                )

            data = resp.json()
            price_data = data.get(coin_id, {})
            price_usd = price_data.get("usd")

            if price_usd is None:
                logger.warning(
                    "No current price for %s", token_symbol
                )
                return Decimal("0")

            # Add small delay to respect rate limits
            await asyncio.sleep(0.2)

            return Decimal(str(price_usd))

    except httpx.RequestError as e:
        raise PriceEngineError(f"Network error fetching current price: {e}")
    except ValueError as e:
        raise PriceEngineError(f"Invalid JSON response: {e}")
    except Exception as e:
        raise PriceEngineError(f"Unexpected error: {e}")


def get_coingecko_id(token_symbol: str) -> Optional[str]:
    """
    Get CoinGecko ID for a token symbol.

    Args:
        token_symbol: Token symbol (e.g., 'ETH', 'BTC')

    Returns:
        Optional[str]: CoinGecko ID if found, None otherwise
    """
    return COINGECKO_IDS.get(token_symbol.upper())


def is_token_supported(token_symbol: str) -> bool:
    """
    Check if a token is supported by the price engine.

    Args:
        token_symbol: Token symbol to check

    Returns:
        bool: True if token is supported
    """
    return token_symbol.upper() in COINGECKO_IDS or token_symbol.upper() in STABLECOINS


def clear_price_cache():
    """Clear the cache for price lookups."""
    from app.utils.cache import price_cache

    price_cache.clear()
