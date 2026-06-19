"""
Comprehensive test suite for FIFO tax calculator.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from app.services.tax_engine import FIFOTaxCalculator, calculate_fifo
from app.models.transaction import Transaction
from app.models.tax_event import TaxEvent
import uuid


def create_test_transaction(
    tx_type: str,
    quantity: Decimal,
    price_usd: Decimal = None,
    timestamp: datetime = None,
    token_symbol: str = "ETH",
) -> Transaction:
    """Create a test transaction with default values."""
    if timestamp is None:
        timestamp = datetime.now()
    if price_usd is None:
        price_usd = Decimal("1000")

    return Transaction(
        id=uuid.uuid4(),
        wallet_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        tx_hash=f"0x{uuid.uuid4().hex[:40]}",
        chain="eth",
        tx_type=tx_type,
        token_symbol=token_symbol,
        quantity=quantity,
        price_usd=price_usd,
        value_usd=quantity * price_usd,
        timestamp=timestamp,
    )


def test_fifo_calculator_simple_buy_sell():
    """Test simple buy and sell scenario."""
    calculator = FIFOTaxCalculator("test_user")

    # Buy 1 ETH at $1000
    buy_time = datetime(2023, 1, 1)
    calculator.add_lot(Decimal("1"), Decimal("1000"), buy_time)

    # Sell 1 ETH at $2000
    sell_time = datetime(2023, 6, 1)
    result = calculator.consume_lots(Decimal("1"), Decimal("2000"), sell_time)

    assert result["quantity"] == Decimal("1")
    assert result["proceeds_usd"] == Decimal("2000")
    assert result["cost_basis_usd"] == Decimal("1000")
    assert result["gain_loss_usd"] == Decimal("1000")
    assert result["is_short_term"] == True  # Held < 365 days


def test_fifo_calculator_multiple_lots_partial_consumption():
    """Test multiple lots with partial consumption."""
    calculator = FIFOTaxCalculator("test_user")

    # Buy 2 ETH at $1000
    calculator.add_lot(Decimal("2"), Decimal("1000"), datetime(2023, 1, 1))

    # Buy 1 ETH at $1500
    calculator.add_lot(Decimal("1"), Decimal("1500"), datetime(2023, 2, 1))

    # Sell 2.5 ETH at $2000
    result = calculator.consume_lots(
        Decimal("2.5"), Decimal("2000"), datetime(2023, 3, 1)
    )

    # Should consume first 2 ETH @ $1000 = $2000 cost basis
    # Then 0.5 ETH @ $1500 = $750 cost basis
    expected_cost_basis = Decimal("2000") + Decimal("750")  # $2750
    expected_proceeds = Decimal("2.5") * Decimal("2000")  # $5000

    assert result["quantity"] == Decimal("2.5")
    assert result["cost_basis_usd"] == expected_cost_basis
    assert result["proceeds_usd"] == expected_proceeds
    assert result["gain_loss_usd"] == expected_proceeds - expected_cost_basis


def test_fifo_calculator_long_term_holding():
    """Test long-term vs short-term classification."""
    calculator = FIFOTaxCalculator("test_user")

    # Buy ETH
    buy_time = datetime(2022, 1, 1)
    calculator.add_lot(Decimal("1"), Decimal("1000"), buy_time)

    # Sell after 400 days (long-term)
    sell_time = buy_time + timedelta(days=400)
    result = calculator.consume_lots(Decimal("1"), Decimal("2000"), sell_time)

    assert result["is_short_term"] == False


def test_fifo_calculator_insufficient_lots():
    """Test error when trying to sell more than available."""
    calculator = FIFOTaxCalculator("test_user")
    calculator.add_lot(Decimal("1"), Decimal("1000"), datetime.now())

    with pytest.raises(ValueError, match="Insufficient lots"):
        calculator.consume_lots(Decimal("2"), Decimal("2000"), datetime.now())


def test_fifo_calculator_zero_quantity():
    """Test error handling for zero quantities."""
    calculator = FIFOTaxCalculator("test_user")

    with pytest.raises(ValueError, match="must be positive"):
        calculator.add_lot(Decimal("0"), Decimal("1000"), datetime.now())

    calculator.add_lot(Decimal("1"), Decimal("1000"), datetime.now())

    with pytest.raises(ValueError, match="must be positive"):
        calculator.consume_lots(Decimal("0"), Decimal("2000"), datetime.now())


def test_fifo_calculator_negative_price():
    """Test error handling for negative prices."""
    calculator = FIFOTaxCalculator("test_user")

    with pytest.raises(ValueError, match="cannot be negative"):
        calculator.add_lot(Decimal("1"), Decimal("-1000"), datetime.now())

    calculator.add_lot(Decimal("1"), Decimal("1000"), datetime.now())

    with pytest.raises(ValueError, match="cannot be negative"):
        calculator.consume_lots(Decimal("1"), Decimal("-2000"), datetime.now())


def test_calculate_fifo_simple_flow():
    """Test the main calculate_fifo function with simple flow."""
    user_id = "test_user"
    token_symbol = "ETH"

    transactions = [
        create_test_transaction(
            "transfer_in", Decimal("1"), Decimal("1000"), datetime(2023, 1, 1)
        ),
        create_test_transaction(
            "trade", Decimal("1"), Decimal("2000"), datetime(2023, 6, 1)
        ),
    ]

    tax_events = calculate_fifo(user_id, token_symbol, transactions)

    assert len(tax_events) == 1
    event = tax_events[0]
    assert event.token_symbol == "ETH"
    assert event.quantity == Decimal("1")
    assert event.proceeds_usd == Decimal("2000")
    assert event.cost_basis_usd == Decimal("1000")
    assert event.gain_loss_usd == Decimal("1000")
    assert event.is_short_term == True


def test_calculate_fifo_airdrop_and_staking():
    """Test that airdrops and staking rewards are treated as buys."""
    user_id = "test_user"
    token_symbol = "ETH"

    transactions = [
        create_test_transaction(
            "airdrop", Decimal("0.5"), Decimal("0"), datetime(2023, 1, 1)
        ),
        create_test_transaction(
            "staking", Decimal("0.1"), Decimal("0"), datetime(2023, 2, 1)
        ),
        create_test_transaction(
            "trade", Decimal("0.6"), Decimal("2000"), datetime(2023, 3, 1)
        ),
    ]

    tax_events = calculate_fifo(user_id, token_symbol, transactions)

    assert len(tax_events) == 1
    # Airdrop and staking should be treated as buys with $0 cost basis
    # Total cost basis should be $0
    assert tax_events[0].cost_basis_usd == Decimal("0")
    assert tax_events[0].proceeds_usd == Decimal("1200")  # 0.6 * 2000
    assert tax_events[0].gain_loss_usd == Decimal("1200")


def test_calculate_fifo_multiple_tokens():
    """Test handling of different tokens."""
    user_id = "test_user"

    # ETH transactions
    eth_transactions = [
        create_test_transaction(
            "transfer_in", Decimal("1"), Decimal("1000"), datetime(2023, 1, 1), "ETH"
        ),
        create_test_transaction(
            "trade", Decimal("1"), Decimal("2000"), datetime(2023, 6, 1), "ETH"
        ),
    ]

    # BTC transactions
    btc_transactions = [
        create_test_transaction(
            "transfer_in", Decimal("0.1"), Decimal("20000"), datetime(2023, 1, 1), "BTC"
        ),
        create_test_transaction(
            "trade", Decimal("0.1"), Decimal("40000"), datetime(2023, 6, 1), "BTC"
        ),
    ]

    eth_events = calculate_fifo(user_id, "ETH", eth_transactions)
    btc_events = calculate_fifo(user_id, "BTC", btc_transactions)

    assert len(eth_events) == 1
    assert len(btc_events) == 1

    assert eth_events[0].token_symbol == "ETH"
    assert btc_events[0].token_symbol == "BTC"
    assert eth_events[0].gain_loss_usd == Decimal("1000")
    assert btc_events[0].gain_loss_usd == Decimal("2000")  # 0.1 * (40000 - 20000)


def test_calculate_fifo_edge_case_zero_price():
    """Test handling of zero prices."""
    user_id = "test_user"
    token_symbol = "ETH"

    transactions = [
        create_test_transaction(
            "transfer_in", Decimal("1"), Decimal("0"), datetime(2023, 1, 1)
        ),
        create_test_transaction(
            "trade", Decimal("1"), Decimal("2000"), datetime(2023, 6, 1)
        ),
    ]

    tax_events = calculate_fifo(user_id, token_symbol, transactions)

    assert len(tax_events) == 1
    assert tax_events[0].cost_basis_usd == Decimal("0")
    assert tax_events[0].proceeds_usd == Decimal("2000")
    assert tax_events[0].gain_loss_usd == Decimal("2000")


def test_calculate_fifo_invalid_transaction_skipped():
    """Test that invalid transactions are skipped gracefully."""
    user_id = "test_user"
    token_symbol = "ETH"

    # Create a transaction with negative quantity
    invalid_tx = create_test_transaction("transfer_in", Decimal("-1"), Decimal("1000"))
    valid_tx = create_test_transaction("trade", Decimal("1"), Decimal("2000"))

    # The invalid transaction should be skipped
    tax_events = calculate_fifo(user_id, token_symbol, [invalid_tx, valid_tx])

    # Should only process the valid transaction
    assert len(tax_events) == 0  # No tax events because no valid buy to match the sell


def test_calculate_fifo_precision_handling():
    """Test precision handling with small amounts."""
    user_id = "test_user"
    token_symbol = "ETH"

    transactions = [
        create_test_transaction(
            "transfer_in", Decimal("0.00000001"), Decimal("1000"), datetime(2023, 1, 1)
        ),
        create_test_transaction(
            "trade", Decimal("0.00000001"), Decimal("2000"), datetime(2023, 6, 1)
        ),
    ]

    tax_events = calculate_fifo(user_id, token_symbol, transactions)

    assert len(tax_events) == 1
    # Very small amounts should still calculate correctly
    expected_cost_basis = Decimal("0.00000001") * Decimal("1000")  # $0.00001
    expected_proceeds = Decimal("0.00000001") * Decimal("2000")  # $0.00002

    assert tax_events[0].cost_basis_usd == expected_cost_basis
    assert tax_events[0].proceeds_usd == expected_proceeds
    assert tax_events[0].gain_loss_usd == expected_proceeds - expected_cost_basis
