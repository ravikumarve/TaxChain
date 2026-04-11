"""
FIFO Cost Basis Calculator
Rules:
- First In First Out (FIFO) — default for most jurisdictions
- Each buy creates a "lot" with quantity + cost per unit
- Each sell consumes oldest lots first
- Gain/Loss = proceeds - cost_basis
- Short-term: held < 365 days
"""

from decimal import Decimal
from datetime import datetime, timedelta
from collections import deque
from typing import List, Deque, Dict, Any
from app.models.transaction import Transaction
from app.models.tax_event import TaxEvent


class FIFOTaxCalculator:
    """FIFO cost basis calculator for crypto transactions."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.lots: Deque[Dict[str, Any]] = deque()

    def add_lot(
        self, quantity: Decimal, cost_per_unit: Decimal, acquired_at: datetime
    ) -> None:
        """Add a new cost basis lot to the queue."""
        if quantity <= Decimal("0"):
            raise ValueError("Lot quantity must be positive")
        if cost_per_unit < Decimal("0"):
            raise ValueError("Cost per unit cannot be negative")

        self.lots.append(
            {
                "quantity": quantity,
                "cost_per_unit": cost_per_unit,
                "acquired_at": acquired_at,
            }
        )

    def consume_lots(
        self,
        quantity_to_sell: Decimal,
        proceeds_per_unit: Decimal,
        disposed_at: datetime,
    ) -> Dict[str, Any]:
        """Consume lots from the front of the queue and calculate gain/loss."""
        if quantity_to_sell <= Decimal("0"):
            raise ValueError("Sell quantity must be positive")
        if proceeds_per_unit < Decimal("0"):
            raise ValueError("Proceeds per unit cannot be negative")

        remaining_quantity = quantity_to_sell
        total_cost_basis = Decimal("0")
        total_proceeds = quantity_to_sell * proceeds_per_unit
        oldest_lot_date = None

        while remaining_quantity > Decimal("0") and self.lots:
            lot = self.lots[0]

            if oldest_lot_date is None or lot["acquired_at"] < oldest_lot_date:
                oldest_lot_date = lot["acquired_at"]

            if lot["quantity"] <= remaining_quantity:
                # Consume entire lot
                total_cost_basis += lot["quantity"] * lot["cost_per_unit"]
                remaining_quantity -= lot["quantity"]
                self.lots.popleft()
            else:
                # Partial lot consumption
                consumed_quantity = remaining_quantity
                total_cost_basis += consumed_quantity * lot["cost_per_unit"]
                lot["quantity"] -= consumed_quantity
                remaining_quantity = Decimal("0")

        if remaining_quantity > Decimal("0"):
            raise ValueError(
                f"Insufficient lots to cover sale of {quantity_to_sell} units"
            )

        # Calculate gain/loss
        gain_loss = total_proceeds - total_cost_basis

        # Determine short-term vs long-term
        holding_period = (
            disposed_at - oldest_lot_date if oldest_lot_date else timedelta(days=0)
        )
        is_short_term = holding_period.days < 365

        return {
            "quantity": quantity_to_sell,
            "proceeds_usd": total_proceeds,
            "cost_basis_usd": total_cost_basis,
            "gain_loss_usd": gain_loss,
            "is_short_term": is_short_term,
            "acquired_at": oldest_lot_date,
            "disposed_at": disposed_at,
        }


def calculate_fifo(
    user_id: str, token_symbol: str, transactions: List[Transaction]
) -> List[TaxEvent]:
    """
    Process transactions chronologically.
    Buys → add to lot queue.
    Sells → consume from front of queue, calculate gain/loss.
    """

    calculator = FIFOTaxCalculator(user_id)
    tax_events = []

    for tx in sorted(transactions, key=lambda t: t.timestamp):
        try:
            # Extract values from SQLAlchemy Column objects
            tx_quantity = tx.quantity
            tx_price = tx.price_usd if tx.price_usd is not None else Decimal("0")
            tx_timestamp = tx.timestamp

            if tx.tx_type in ("transfer_in", "airdrop", "staking"):
                # Treat as buy at market price
                calculator.add_lot(
                    quantity=tx_quantity,
                    cost_per_unit=tx_price,
                    acquired_at=tx_timestamp,
                )

            elif tx.tx_type in ("transfer_out", "trade"):
                # Sell transaction
                result = calculator.consume_lots(
                    quantity_to_sell=tx_quantity,
                    proceeds_per_unit=tx_price,
                    disposed_at=tx_timestamp,
                )

                # Create tax event
                tax_event = TaxEvent(
                    user_id=user_id,
                    token_symbol=token_symbol,
                    quantity=result["quantity"],
                    proceeds_usd=result["proceeds_usd"],
                    cost_basis_usd=result["cost_basis_usd"],
                    gain_loss_usd=result["gain_loss_usd"],
                    is_short_term=result["is_short_term"],
                    acquired_at=result["acquired_at"],
                    disposed_at=result["disposed_at"],
                    sale_tx_id=tx.id,
                )
                tax_events.append(tax_event)

        except (ValueError, TypeError) as e:
            # Skip invalid transactions but log the error
            print(f"Warning: Skipping transaction {tx.tx_hash}: {e}")
            continue

    return tax_events
