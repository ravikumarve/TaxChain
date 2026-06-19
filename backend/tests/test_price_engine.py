"""
Test suite for CoinGecko Price Engine Service.
"""
import pytest
import asyncio
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, patch, Mock, MagicMock
import httpx

from app.services.price_engine import (
    get_historical_price,
    get_current_price,
    get_coingecko_id,
    is_token_supported,
    clear_price_cache,
    PriceEngineError,
    COINGECKO_IDS,
    STABLECOINS,
)


MOCK_PRICE = 1500.0
MOCK_RESPONSE = {"market_data": {"current_price": {"usd": MOCK_PRICE}}}


# ── Stablecoin & Unknown Token Tests (no API calls needed) ──────────────

@pytest.mark.asyncio
async def test_get_historical_price_stablecoin():
    """Test that stablecoins return $1.00."""
    for stablecoin in ["USDT", "USDC", "DAI"]:
        price = await get_historical_price(stablecoin, datetime(2023, 1, 1))
        assert price == Decimal("1.00")


@pytest.mark.asyncio
async def test_get_historical_price_unknown_token():
    """Test that unknown tokens return 0."""
    price = await get_historical_price("UNKNOWNTOKEN", datetime(2023, 1, 1))
    assert price == Decimal("0")


@pytest.mark.asyncio
async def test_get_current_price_stablecoin():
    """Test that stablecoins return $1.00."""
    for stablecoin in ["USDT", "USDC", "DAI"]:
        price = await get_current_price(stablecoin)
        assert price == Decimal("1.00")


@pytest.mark.asyncio
async def test_get_current_price_unknown_token():
    """Test that unknown tokens return 0."""
    price = await get_current_price("UNKNOWNTOKEN")
    assert price == Decimal("0")


# ── Utility Tests ────────────────────────────────────────────────────────

def test_get_coingecko_id():
    """Test CoinGecko ID lookup."""
    assert get_coingecko_id("ETH") == "ethereum"
    assert get_coingecko_id("BTC") == "bitcoin"
    assert get_coingecko_id("UNKNOWN") is None


def test_is_token_supported():
    """Test token support check."""
    assert is_token_supported("ETH") is True
    assert is_token_supported("BTC") is True
    assert is_token_supported("USDT") is True
    assert is_token_supported("UNKNOWN") is False


# ── API Call Tests (use unique dates to avoid cache interference) ────────

@pytest.mark.asyncio
async def test_get_historical_price_api_call():
    """Test successful API call returns correct price."""
    date = datetime(2023, 6, 1)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json = Mock(return_value=MOCK_RESPONSE)

        price = await get_historical_price("ETH", date)

        assert price == Decimal(str(MOCK_PRICE))
        assert mock_get.call_count >= 1


@pytest.mark.asyncio
async def test_get_historical_price_api_error():
    """Test error handling for API failures (unique token)."""
    date = datetime(2023, 7, 1)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 429
        mock_get.return_value.text = "Rate limit exceeded"

        with pytest.raises(PriceEngineError, match="CoinGecko API error"):
            await get_historical_price("BTC", date)


@pytest.mark.asyncio
async def test_get_historical_price_network_error():
    """Test error handling for network failures."""
    date = datetime(2023, 8, 1)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.RequestError("Network error")

        with pytest.raises(PriceEngineError, match="Network error"):
            await get_historical_price("MATIC", date)


@pytest.mark.asyncio
async def test_get_historical_price_no_market_data():
    """Test handling of missing market data."""
    date = datetime(2023, 9, 1)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json = Mock(return_value={"market_data": {}})

        price = await get_historical_price("SOL", date)
        assert price == Decimal("0")


@pytest.mark.asyncio
async def test_concurrent_requests():
    """Test that concurrent requests work correctly."""
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json = Mock(return_value=MOCK_RESPONSE)

        results = await asyncio.gather(
            get_historical_price("AAVE", datetime(2024, 1, 1)),
            get_historical_price("UNI", datetime(2024, 1, 1)),
            get_historical_price("LINK", datetime(2024, 1, 1)),
        )

        assert all(price == Decimal(str(MOCK_PRICE)) for price in results)
        assert mock_get.call_count == 3


@pytest.mark.asyncio
async def test_decimal_precision():
    """Test that prices are returned as Decimals with proper precision."""
    date = datetime(2024, 2, 1)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json = Mock(
            return_value={"market_data": {"current_price": {"usd": 1234.56789}}}
        )

        price = await get_historical_price("YFI", date)
        assert price == Decimal("1234.56789")
        assert isinstance(price, Decimal)


@pytest.mark.asyncio
async def test_case_insensitive_token_lookup():
    """Test that token symbols are case-insensitive."""
    date = datetime(2024, 3, 1)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json = Mock(return_value=MOCK_RESPONSE)

        price1 = await get_historical_price("LTC", date)
        price2 = await get_historical_price("LTC", date)
        price3 = await get_historical_price("Ltc", date)

        assert price1 > Decimal("0")


# ── Caching Tests ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_historical_price_caching():
    """Test that price lookups are cached per token+date combination."""
    date = datetime(2024, 4, 1)
    date2 = datetime(2024, 4, 2)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json = Mock(return_value=MOCK_RESPONSE)

        price1 = await get_historical_price("DOGE", date)
        assert price1 == Decimal(str(MOCK_PRICE))
        first_calls = mock_get.call_count

        # Second call same token+date → cache hit
        price2 = await get_historical_price("DOGE", date)
        assert price2 == Decimal(str(MOCK_PRICE))
        assert mock_get.call_count == first_calls  # No extra API call

        # Different date → cache miss
        price3 = await get_historical_price("DOGE", date2)
        assert mock_get.call_count > first_calls
