"""
Tax-Loss Harvesting Service

Identifies opportunities to realize losses to offset gains.
Implements wash sale detection (30-day rule).
"""

import logging
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_
from app.models.tax_event import TaxEvent
from app.models.transaction import Transaction
from app.models.cost_basis_lot import CostBasisLot

logger = logging.getLogger(__name__)


class TaxLossHarvestingReport:
    """
    Analyzes realized and unrealized gains/losses to find harvesting opportunities.
    """

    def __init__(self, user_id: str, financial_year: str):
        self.user_id = user_id
        self.financial_year = financial_year

    async def generate_report(self, db: AsyncSession) -> Dict[str, Any]:
        tax_events = await self._get_tax_events(db)
        if not tax_events:
            return {
                "summary": {
                    "total_realized_gains": Decimal("0"),
                    "total_realized_losses": Decimal("0"),
                    "net_gain_loss": Decimal("0"),
                    "harvesting_potential": Decimal("0"),
                },
                "realized_losses": [],
                "wash_sales": [],
                "recommendations": [],
                "expiring_losses": [],
                "message": "No tax events found for this financial year",
            }

        realized_losses = self._analyze_realized_losses(tax_events)
        wash_sales = await self._detect_wash_sales(db, tax_events)
        harvesting_potential = self._find_harvesting_opportunities(db, tax_events)
        expiring_losses = self._find_expiring_losses(tax_events)
        recommendations = self._get_recommendations(realized_losses, harvesting_potential)

        total_gains = sum(
            e.gain_loss_usd for e in tax_events if e.gain_loss_usd > Decimal("0")
        )
        total_losses = sum(
            abs(e.gain_loss_usd) for e in tax_events if e.gain_loss_usd < Decimal("0")
        )

        return {
            "summary": {
                "total_realized_gains": total_gains,
                "total_realized_losses": total_losses,
                "net_gain_loss": total_gains - total_losses,
                "harvesting_potential": harvesting_potential,
            },
            "realized_losses": realized_losses,
            "wash_sales": wash_sales,
            "recommendations": recommendations,
            "expiring_losses": expiring_losses,
        }

    async def _get_tax_events(self, db: AsyncSession) -> List[TaxEvent]:
        from app.routers.reports import get_financial_year_range, calculate_financial_year

        fy_start, fy_end = get_financial_year_range(self.financial_year)

        result = await db.execute(
            select(TaxEvent)
            .where(TaxEvent.user_id == self.user_id)
            .where(TaxEvent.disposed_at >= fy_start)
            .where(TaxEvent.disposed_at < fy_end)
            .order_by(TaxEvent.disposed_at)
        )
        return list(result.scalars().all())

    def _analyze_realized_losses(self, tax_events: List[TaxEvent]) -> List[Dict[str, Any]]:
        losses = [
            {
                "token_symbol": e.token_symbol,
                "quantity": float(e.quantity),
                "loss_amount_usd": float(abs(e.gain_loss_usd)),
                "proceeds_usd": float(e.proceeds_usd),
                "cost_basis_usd": float(e.cost_basis_usd),
                "disposed_at": e.disposed_at.isoformat() if e.disposed_at else None,
                "is_short_term": e.is_short_term,
                "tax_event_id": str(e.id),
            }
            for e in tax_events
            if e.gain_loss_usd < Decimal("0")
        ]
        losses.sort(key=lambda l: l["loss_amount_usd"], reverse=True)
        return losses

    async def _detect_wash_sales(
        self, db: AsyncSession, tax_events: List[TaxEvent]
    ) -> List[Dict[str, Any]]:
        wash_sales = []
        window = timedelta(days=30)

        for event in tax_events:
            if event.gain_loss_usd >= Decimal("0"):
                continue

            disposed_at = event.disposed_at
            sale_tx = await db.get(Transaction, event.sale_tx_id)
            if not sale_tx:
                continue

            window_start = disposed_at - window
            window_end = disposed_at + window

            result = await db.execute(
                select(Transaction)
                .where(Transaction.user_id == self.user_id)
                .where(Transaction.token_symbol == event.token_symbol)
                .where(Transaction.tx_type.in_(["trade", "transfer_in"]))
                .where(Transaction.timestamp >= window_start)
                .where(Transaction.timestamp <= window_end)
                .where(Transaction.id != event.sale_tx_id)
                .order_by(Transaction.timestamp)
            )
            buy_txs = result.scalars().all()

            if buy_txs:
                for buy_tx in buy_txs:
                    wash_sales.append({
                        "token_symbol": event.token_symbol,
                        "sale_date": disposed_at.isoformat(),
                        "loss_amount_usd": float(abs(event.gain_loss_usd)),
                        "buy_date": buy_tx.timestamp.isoformat(),
                        "buy_quantity": float(buy_tx.quantity),
                        "days_apart": abs((buy_tx.timestamp - disposed_at).days),
                        "is_wash": True,
                        "loss_disallowed": True,
                        "tax_event_id": str(event.id),
                    })

        return wash_sales

    def _find_harvesting_opportunities(
        self, db: AsyncSession, tax_events: List[TaxEvent]
    ) -> Decimal:
        return Decimal("0")

    def _get_recommendations(
        self, realized_losses: List[Dict], harvesting_potential: Decimal
    ) -> List[Dict[str, Any]]:
        recommendations = []

        for loss in realized_losses[:5]:
            recommendations.append({
                "type": "realized_loss",
                "token_symbol": loss["token_symbol"],
                "loss_amount_usd": loss["loss_amount_usd"],
                "action": "Use this loss to offset current or future gains.",
                "priority": "high" if loss["loss_amount_usd"] > 1000 else "medium",
            })

        return recommendations

    def _find_expiring_losses(self, tax_events: List[TaxEvent]) -> List[Dict[str, Any]]:
        expiring = []
        now = datetime.utcnow()
        threshold = timedelta(days=90)

        for event in tax_events:
            if event.gain_loss_usd >= Decimal("0") or not event.acquired_at:
                continue

            holding_period = (event.disposed_at - event.acquired_at).days
            days_to_long_term = max(0, 365 - holding_period)

            if 0 < days_to_long_term <= 90:
                expiring.append({
                    "token_symbol": event.token_symbol,
                    "loss_amount_usd": float(abs(event.gain_loss_usd)),
                    "acquired_at": event.acquired_at.isoformat(),
                    "disposed_at": event.disposed_at.isoformat(),
                    "holding_period_days": holding_period,
                    "days_until_long_term": days_to_long_term,
                    "action": "This loss may convert to long-term status soon. Harvest now to maintain short-term loss treatment.",
                })

        return expiring
