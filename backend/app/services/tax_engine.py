"""
Cost Basis Calculator Engine

Supports 4 accounting methods:
- FIFO (First In, First Out) — default
- LIFO (Last In, First Out)
- HIFO (Highest Cost, First Out)
- Average Cost

Each method is a subclass of CostBasisCalculator.
Use the factory function get_calculator() or calculate_with_method().
"""

import logging
from decimal import Decimal
from datetime import datetime, timedelta
from collections import deque
from typing import List, Deque, Dict, Any, Optional
from abc import ABC, abstractmethod
from app.models.transaction import Transaction
from app.models.tax_event import TaxEvent
from app.models.cost_basis_lot import CostBasisLot

logger = logging.getLogger(__name__)


async def load_lots_from_db(db, user_id: str, token_symbol: str) -> Deque[Dict[str, Any]]:
    from sqlalchemy.future import select

    result = await db.execute(
        select(CostBasisLot)
        .where(
            CostBasisLot.user_id == user_id,
            CostBasisLot.token_symbol == token_symbol,
            CostBasisLot.quantity_remaining > Decimal("0"),
        )
        .order_by(CostBasisLot.acquired_at)
    )
    lots = result.scalars().all()

    return deque(
        {
            "quantity": lot.quantity_remaining,
            "cost_per_unit": lot.cost_per_unit_usd,
            "acquired_at": lot.acquired_at,
            "db_id": lot.id,
        }
        for lot in lots
    )


async def persist_lots_to_db(
    db, user_id: str, token_symbol: str, chain: str,
    calculator: "CostBasisCalculator",
) -> None:
    from sqlalchemy import delete

    await db.execute(
        delete(CostBasisLot).where(
            CostBasisLot.user_id == user_id,
            CostBasisLot.token_symbol == token_symbol,
        )
    )

    if calculator.method == "avg_cost":
        avg_calc = calculator  # type: AverageCostCalculator
        if avg_calc.total_quantity > Decimal("0"):
            db_lot = CostBasisLot(
                user_id=user_id,
                token_symbol=token_symbol,
                chain=chain,
                quantity_remaining=avg_calc.total_quantity,
                cost_per_unit_usd=avg_calc.average_cost,
                acquired_at=avg_calc.latest_acquired_at or datetime.utcnow(),
            )
            db.add(db_lot)
    else:
        for lot in calculator.lots:
            db_lot = CostBasisLot(
                user_id=user_id,
                token_symbol=token_symbol,
                chain=chain,
                quantity_remaining=lot["quantity"],
                cost_per_unit_usd=lot["cost_per_unit"],
                acquired_at=lot["acquired_at"],
                source_tx_id=lot.get("source_tx_id"),
            )
            db.add(db_lot)

    await db.commit()


class CostBasisCalculator(ABC):
    """Abstract base class for all cost basis methods."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.lots: Deque[Dict[str, Any]] = deque()

    @property
    @abstractmethod
    def method(self) -> str:
        ...

    def add_lot(self, quantity: Decimal, cost_per_unit: Decimal, acquired_at: datetime) -> None:
        if quantity <= Decimal("0"):
            raise ValueError("Lot quantity must be positive")
        if cost_per_unit < Decimal("0"):
            raise ValueError("Cost per unit cannot be negative")
        self._add_lot_impl(quantity, cost_per_unit, acquired_at)

    @abstractmethod
    def _add_lot_impl(self, quantity: Decimal, cost_per_unit: Decimal, acquired_at: datetime) -> None:
        ...

    def consume_lots(
        self,
        quantity_to_sell: Decimal,
        proceeds_per_unit: Decimal,
        disposed_at: datetime,
    ) -> Dict[str, Any]:
        if quantity_to_sell <= Decimal("0"):
            raise ValueError("Sell quantity must be positive")
        if proceeds_per_unit < Decimal("0"):
            raise ValueError("Proceeds per unit cannot be negative")
        return self._consume_lots_impl(quantity_to_sell, proceeds_per_unit, disposed_at)

    @abstractmethod
    def _consume_lots_impl(
        self,
        quantity_to_sell: Decimal,
        proceeds_per_unit: Decimal,
        disposed_at: datetime,
    ) -> Dict[str, Any]:
        ...

    def _build_result(
        self,
        quantity: Decimal,
        total_proceeds: Decimal,
        total_cost_basis: Decimal,
        oldest_lot_date: datetime,
        disposed_at: datetime,
    ) -> Dict[str, Any]:
        gain_loss = total_proceeds - total_cost_basis
        holding_period = (
            disposed_at - oldest_lot_date if oldest_lot_date else timedelta(days=0)
        )
        is_short_term = holding_period.days < 365

        return {
            "quantity": quantity,
            "proceeds_usd": total_proceeds,
            "cost_basis_usd": total_cost_basis,
            "gain_loss_usd": gain_loss,
            "is_short_term": is_short_term,
            "acquired_at": oldest_lot_date,
            "disposed_at": disposed_at,
        }


class FIFOCalculator(CostBasisCalculator):
    """First In, First Out — consume from front of deque."""

    @property
    def method(self) -> str:
        return "fifo"

    def _add_lot_impl(self, quantity: Decimal, cost_per_unit: Decimal, acquired_at: datetime) -> None:
        self.lots.append({
            "quantity": quantity,
            "cost_per_unit": cost_per_unit,
            "acquired_at": acquired_at,
        })

    def _consume_lots_impl(
        self,
        quantity_to_sell: Decimal,
        proceeds_per_unit: Decimal,
        disposed_at: datetime,
    ) -> Dict[str, Any]:
        remaining = quantity_to_sell
        total_cost_basis = Decimal("0")
        total_proceeds = quantity_to_sell * proceeds_per_unit
        oldest_lot_date = None

        while remaining > Decimal("0") and self.lots:
            lot = self.lots[0]
            if oldest_lot_date is None or lot["acquired_at"] < oldest_lot_date:
                oldest_lot_date = lot["acquired_at"]

            if lot["quantity"] <= remaining:
                total_cost_basis += lot["quantity"] * lot["cost_per_unit"]
                remaining -= lot["quantity"]
                self.lots.popleft()
            else:
                consumed = remaining
                total_cost_basis += consumed * lot["cost_per_unit"]
                lot["quantity"] -= consumed
                remaining = Decimal("0")

        if remaining > Decimal("0"):
            raise ValueError(f"Insufficient lots to cover sale of {quantity_to_sell} units")

        return self._build_result(
            quantity_to_sell, total_proceeds, total_cost_basis,
            oldest_lot_date or disposed_at, disposed_at,
        )


class LIFOCalculator(CostBasisCalculator):
    """Last In, First Out — consume from end of deque."""

    @property
    def method(self) -> str:
        return "lifo"

    def _add_lot_impl(self, quantity: Decimal, cost_per_unit: Decimal, acquired_at: datetime) -> None:
        self.lots.append({
            "quantity": quantity,
            "cost_per_unit": cost_per_unit,
            "acquired_at": acquired_at,
        })

    def _consume_lots_impl(
        self,
        quantity_to_sell: Decimal,
        proceeds_per_unit: Decimal,
        disposed_at: datetime,
    ) -> Dict[str, Any]:
        remaining = quantity_to_sell
        total_cost_basis = Decimal("0")
        total_proceeds = quantity_to_sell * proceeds_per_unit
        oldest_lot_date = None

        while remaining > Decimal("0") and self.lots:
            lot = self.lots[-1]
            if oldest_lot_date is None or lot["acquired_at"] < oldest_lot_date:
                oldest_lot_date = lot["acquired_at"]

            if lot["quantity"] <= remaining:
                total_cost_basis += lot["quantity"] * lot["cost_per_unit"]
                remaining -= lot["quantity"]
                self.lots.pop()
            else:
                consumed = remaining
                total_cost_basis += consumed * lot["cost_per_unit"]
                lot["quantity"] -= consumed
                remaining = Decimal("0")

        if remaining > Decimal("0"):
            raise ValueError(f"Insufficient lots to cover sale of {quantity_to_sell} units")

        return self._build_result(
            quantity_to_sell, total_proceeds, total_cost_basis,
            oldest_lot_date or disposed_at, disposed_at,
        )


class HIFOCalculator(CostBasisCalculator):
    """Highest Cost, First Out — consume highest-cost lots first."""

    @property
    def method(self) -> str:
        return "hifo"

    def _add_lot_impl(self, quantity: Decimal, cost_per_unit: Decimal, acquired_at: datetime) -> None:
        self.lots.append({
            "quantity": quantity,
            "cost_per_unit": cost_per_unit,
            "acquired_at": acquired_at,
        })

    def _consume_lots_impl(
        self,
        quantity_to_sell: Decimal,
        proceeds_per_unit: Decimal,
        disposed_at: datetime,
    ) -> Dict[str, Any]:
        remaining = quantity_to_sell
        total_cost_basis = Decimal("0")
        total_proceeds = quantity_to_sell * proceeds_per_unit
        oldest_lot_date = None

        while remaining > Decimal("0") and self.lots:
            lot = max(self.lots, key=lambda l: (l["cost_per_unit"], l["acquired_at"]))
            if oldest_lot_date is None or lot["acquired_at"] < oldest_lot_date:
                oldest_lot_date = lot["acquired_at"]

            if lot["quantity"] <= remaining:
                total_cost_basis += lot["quantity"] * lot["cost_per_unit"]
                remaining -= lot["quantity"]
                self.lots.remove(lot)
            else:
                consumed = remaining
                total_cost_basis += consumed * lot["cost_per_unit"]
                lot["quantity"] -= consumed
                remaining = Decimal("0")

        if remaining > Decimal("0"):
            raise ValueError(f"Insufficient lots to cover sale of {quantity_to_sell} units")

        return self._build_result(
            quantity_to_sell, total_proceeds, total_cost_basis,
            oldest_lot_date or disposed_at, disposed_at,
        )


class AverageCostCalculator(CostBasisCalculator):
    """Average Cost Basis — maintains running average cost per unit."""

    def __init__(self, user_id: str):
        super().__init__(user_id)
        self.total_quantity: Decimal = Decimal("0")
        self.total_cost: Decimal = Decimal("0")
        self.average_cost: Decimal = Decimal("0")
        self.latest_acquired_at: Optional[datetime] = None

    @property
    def method(self) -> str:
        return "avg_cost"

    def _add_lot_impl(self, quantity: Decimal, cost_per_unit: Decimal, acquired_at: datetime) -> None:
        new_total_qty = self.total_quantity + quantity
        new_total_cost = self.total_cost + (quantity * cost_per_unit)
        if new_total_qty > Decimal("0"):
            self.average_cost = new_total_cost / new_total_qty
        self.total_quantity = new_total_qty
        self.total_cost = new_total_cost
        if self.latest_acquired_at is None or acquired_at > self.latest_acquired_at:
            self.latest_acquired_at = acquired_at

    def _consume_lots_impl(
        self,
        quantity_to_sell: Decimal,
        proceeds_per_unit: Decimal,
        disposed_at: datetime,
    ) -> Dict[str, Any]:
        if quantity_to_sell > self.total_quantity:
            raise ValueError(
                f"Insufficient quantity to cover sale of {quantity_to_sell} units "
                f"(only {self.total_quantity} available)"
            )

        total_proceeds = quantity_to_sell * proceeds_per_unit
        total_cost_basis = quantity_to_sell * self.average_cost

        self.total_quantity -= quantity_to_sell
        self.total_cost -= total_cost_basis

        return self._build_result(
            quantity_to_sell, total_proceeds, total_cost_basis,
            self.latest_acquired_at or disposed_at, disposed_at,
        )


def get_calculator(method: str, user_id: str) -> CostBasisCalculator:
    """Factory function — returns the right calculator for the given method."""
    method_map = {
        "fifo": FIFOCalculator,
        "lifo": LIFOCalculator,
        "hifo": HIFOCalculator,
        "avg_cost": AverageCostCalculator,
    }
    calc_class = method_map.get(method)
    if calc_class is None:
        logger.warning(f"Unknown cost basis method '{method}', falling back to FIFO")
        calc_class = FIFOCalculator
    return calc_class(user_id)


def calculate_with_method(
    method: str,
    user_id: str,
    token_symbol: str,
    transactions: List[Transaction],
) -> List[TaxEvent]:
    """Dispatch to the right calculator based on method string."""
    calculator = get_calculator(method, user_id)
    tax_events = []

    for tx in sorted(transactions, key=lambda t: t.timestamp):
        try:
            tx_quantity = tx.quantity
            tx_price = tx.price_usd if tx.price_usd is not None else Decimal("0")
            tx_timestamp = tx.timestamp

            # BUY events: add to cost basis lots
            if tx.tx_type in ("transfer_in", "airdrop", "staking", "lp_deposit", "yield_farm"):
                # LP Deposit: treat as buying LP tokens
                # Yield Farm deposit: no immediate tax event, but track as basis
                calculator.add_lot(
                    quantity=tx_quantity,
                    cost_per_unit=tx_price,
                    acquired_at=tx_timestamp,
                )

            # SELL / TAXABLE events: consume from lots
            elif tx.tx_type in ("transfer_out", "trade", "lp_withdraw", "liquidation"):
                # LP Withdraw: taxable — selling LP tokens for underlying
                # Liquidation: taxable — forced sale
                result = calculator.consume_lots(
                    quantity_to_sell=tx_quantity,
                    proceeds_per_unit=tx_price,
                    disposed_at=tx_timestamp,
                )

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

            # BORROW / REPAY: no taxable events
            # Borrow creates debt, not income. Repaying debt is not a disposal.
            # If repaid with different tokens, that's a separate trade event.
            elif tx.tx_type in ("borrow", "repay"):
                continue

        except (ValueError, TypeError) as e:
            logger.warning("Skipping transaction %s: %s", tx.tx_hash, e)
            continue

    return tax_events


# Backward-compatible aliases
FIFOTaxCalculator = FIFOCalculator


def calculate_fifo(
    user_id: str, token_symbol: str, transactions: List[Transaction]
) -> List[TaxEvent]:
    """Backward-compatible wrapper — delegates to calculate_with_method."""
    return calculate_with_method("fifo", user_id, token_symbol, transactions)
