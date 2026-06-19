"""
Exchange Rate Service
Provides USD → local currency conversion for multi-currency P&L display.
Uses free exchangerate.host API with hardcoded fallback rates.
"""

import logging
from decimal import Decimal
from typing import Dict, Optional
from datetime import datetime, date

import httpx

logger = logging.getLogger(__name__)

# Supported currencies
SUPPORTED_CURRENCIES = {"USD", "INR", "EUR", "GBP", "AUD", "SGD", "CAD", "JPY"}

# Fallback rates (used when API is unavailable)
# Updated: 2026-06 — these are approximate and should be replaced with live data
FALLBACK_RATES: Dict[str, Decimal] = {
    "USD": Decimal("1.0000"),
    "INR": Decimal("83.50"),
    "EUR": Decimal("0.92"),
    "GBP": Decimal("0.79"),
    "AUD": Decimal("1.52"),
    "SGD": Decimal("1.34"),
    "CAD": Decimal("1.37"),
    "JPY": Decimal("156.00"),
}

# Free exchange rate API (no key required for basic usage)
EXCHANGE_API_URL = "https://open.er-api.com/v6/latest/USD"


async def get_usd_rate(target_currency: str) -> Decimal:
    """
    Get USD → target_currency exchange rate.
    
    Args:
        target_currency: ISO 4217 currency code (e.g., 'EUR', 'GBP', 'INR')
        
    Returns:
        Decimal exchange rate (how many target units per 1 USD)
    """
    target = target_currency.upper()
    if target == "USD":
        return Decimal("1.0000")

    if target not in SUPPORTED_CURRENCIES:
        logger.warning("Unsupported currency: %s, falling back to USD", target)
        return Decimal("1.0000")

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(EXCHANGE_API_URL, timeout=10.0)
            if resp.status_code == 200:
                data = resp.json()
                rate = data.get("rates", {}).get(target)
                if rate:
                    return Decimal(str(rate))
                logger.warning("Currency %s not found in API response", target)
            else:
                logger.warning(
                    "Exchange rate API returned %s, using fallback", resp.status_code
                )
    except Exception as e:
        logger.warning("Exchange rate API error: %s, using fallback", e)

    # Fallback
    rate = FALLBACK_RATES.get(target, Decimal("1.0000"))
    logger.info("Using fallback rate for %s: %s", target, rate)
    return rate


def format_currency(amount: Decimal, currency: str = "USD") -> str:
    """Format a decimal amount as a human-readable currency string."""
    symbols = {
        "USD": "$", "INR": "₹", "EUR": "€", "GBP": "£",
        "AUD": "A$", "SGD": "S$", "CAD": "C$", "JPY": "¥",
    }
    symbol = symbols.get(currency.upper(), "$")

    # JPY has no decimal places
    if currency.upper() == "JPY":
        return f"{symbol}{amount:,.0f}"

    return f"{symbol}{amount:,.2f}"
