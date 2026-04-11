"""
Test suite for CoinGecko Price Engine Service.
"""

import pytest
import asyncio
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, patch, MagicMock, Mock
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


@pytest.fixture(autouse=True)
def clear_cache_between_tests():
    """Clear price cache between tests."""
    clear_price_cache()
    yield
    clear_price_cache()


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


@pytest.mark.asyncio
async def test_get_coingecko_id():
    """Test CoinGecko ID lookup."""
    assert get_coingecko_id("ETH") == "ethereum"
    assert get_coingecko_id("BTC") == "bitcoin"
    assert get_coingecko_id("UNKNOWN") is None


def test_is_token_supported():
    """Test token support check."""
    assert is_token_supported("ETH") == True
    assert is_token_supported("BTC") == True
    assert is_token_supported("USDT") == True
    assert is_token_supported("UNKNOWN") == False


@pytest.mark.asyncio
async def test_get_historical_price_caching():
    """Test that price lookups are cached."""
    date = datetime(2023, 1, 1)

    # Mock the HTTP request to return a specific price
    mock_response = {"market_data": {"current_price": {"usd": 1500.0}}}

    # Mock the HTTP request to return a specific price
    mock_response = {"market_data": {"current_price": {"usd": 1500.0}}}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json = Mock(return_value=mock_response)

        # First call should make HTTP request
        price1 = await get_historical_price("ETH", date)
        assert price1 == Decimal("1500.0")
        assert mock_get.call_count == 1

        # Second call should use cache
        price2 = await get_historical_price("ETH", date)
        assert price2 == Decimal("1500.0")
        assert mock_get.call_count == 1  # Still 1 call due to caching


@pytest.mark.asyncio
async def test_get_historical_price_api_error():
    """Test error handling for API failures."""
    date = datetime(2023, 1, 1)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 429  # Rate limit
        mock_get.return_value.text = "Rate limit exceeded"

        with pytest.raises(PriceEngineError, match="CoinGecko API error"):
            await get_historical_price("ETH", date)


@pytest.mark.asyncio
async def test_get_historical_price_network_error():
    """Test error handling for network failures."""
    date = datetime(2023, 1, 1)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.RequestError("Network error")

        with pytest.raises(PriceEngineError, match="Network error"):
            await get_historical_price("ETH", date)


@pytest.mark.asyncio
async def test_get_historical_price_no_market_data():
    """Test handling of missing market data."""
    date = datetime(2023, 1, 1)
    mock_response = {"market_data": {}}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json = Mock(return_value=mock_response)

        price = await get_historical_price("ETH", date)
        assert price == Decimal("0")


@pytest.mark.asyncio
async def test_concurrent_requests():
    """Test that concurrent requests work correctly."""
    date = datetime(2023, 1, 1)
    mock_response = {"market_data": {"current_price": {"usd": 1500.0}}}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json = Mock(return_value=mock_response)

        # Make multiple concurrent requests
        results = await asyncio.gather(
            get_historical_price("ETH", date),
            get_historical_price("BTC", date),
            get_historical_price("MATIC", date),
        )

        # All should return the mock price
        assert all(price == Decimal("1500.0") for price in results)
        # Should be 3 separate API calls
        assert mock_get.call_count == 3


def test_clear_cache():
    """Test that cache clearing works."""
    # Mock a function call to populate cache
    original_cache_info = get_historical_price.cache_info()

    # Clear cache
    clear_price_cache()

    # Cache should be empty
    new_cache_info = get_historical_price.cache_info()
    assert new_cache_info.hits == 0
    assert new_cache_info.misses == 0
    assert new_cache_info.currsize == 0


@pytest.mark.asyncio
async def test_decimal_precision():
    """Test that prices are returned as Decimals with proper precision."""
    date = datetime(2023, 1, 1)
    mock_response = {"market_data": {"current_price": {"usd": 1234.56789}}}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json = Mock(return_value=mock_response)

        price = await get_historical_price("ETH", date)

        # Should be Decimal with exact precision
        assert price == Decimal("1234.56789")
        assert isinstance(price, Decimal)


@pytest.mark.asyncio
async def test_case_insensitive_token_lookup():
    """Test that token symbols are case-insensitive."""
    date = datetime(2023, 1, 1)
    mock_response = {"market_data": {"current_price": {"usd": 1500.0}}}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json = Mock(return_value=mock_response)

        # Test different cases
        price1 = await get_historical_price("eth", date)
        price2 = await get_historical_price("ETH", date)
        price3 = await get_historical_price("Eth", date)

        assert price1 == price2 == price3 == Decimal("1500.0")
