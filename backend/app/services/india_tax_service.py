import logging
from decimal import Decimal
from typing import List, Dict, Any, Optional
from app.models.tax_event import TaxEvent
from app.models.transaction import Transaction
from app.services.exchange_rate import get_usd_rate

logger = logging.getLogger(__name__)

INDIA_TDS_RATE = Decimal("0.01")
INDIA_FLAT_TAX_RATE = Decimal("0.30")


def calculate_tds(proceeds_usd: Decimal) -> Decimal:
    if proceeds_usd <= Decimal("0"):
        return Decimal("0")
    return (proceeds_usd * INDIA_TDS_RATE).quantize(Decimal("0.01"))


async def calculate_india_tax_liability(
    tax_events: List[TaxEvent],
    transactions: List[Transaction],
    db_session,
    user_id: str,
    financial_year: str,
    usd_to_inr_rate: Optional[Decimal] = None,
) -> Dict[str, Any]:
    if usd_to_inr_rate is None:
        usd_to_inr_rate = await get_usd_rate("INR")

    total_gains_usd = Decimal("0")
    total_losses_usd = Decimal("0")
    gain_events = []
    loss_events = []
    total_tds_usd = Decimal("0")

    for event in tax_events:
        if event.gain_loss_usd > Decimal("0"):
            total_gains_usd += event.gain_loss_usd
            gain_events.append(event)
        else:
            total_losses_usd += abs(event.gain_loss_usd)
            loss_events.append(event)

    for tx in transactions:
        if tx.tx_type in ("transfer_out", "trade", "lp_withdraw", "liquidation") and tx.value_usd:
            tds = calculate_tds(tx.value_usd)
            total_tds_usd += tds
            if tx.tds_usd is None or tx.tds_usd == Decimal("0"):
                tx.tds_usd = tds

    if db_session:
        try:
            await db_session.commit()
        except Exception as e:
            logger.warning(f"Failed to commit TDS updates: {e}")
            await db_session.rollback()

    taxable_amount_usd = total_gains_usd
    estimated_tax_usd = (taxable_amount_usd * INDIA_FLAT_TAX_RATE).quantize(Decimal("0.01"))

    total_gains_inr = (total_gains_usd * usd_to_inr_rate).quantize(Decimal("0.01"))
    total_losses_inr = (total_losses_usd * usd_to_inr_rate).quantize(Decimal("0.01"))
    taxable_amount_inr = (taxable_amount_usd * usd_to_inr_rate).quantize(Decimal("0.01"))
    estimated_tax_inr = (estimated_tax_usd * usd_to_inr_rate).quantize(Decimal("0.01"))
    total_tds_inr = (total_tds_usd * usd_to_inr_rate).quantize(Decimal("0.01"))

    net_tax_due_usd = max(Decimal("0"), estimated_tax_usd - total_tds_usd)
    net_tax_due_inr = max(Decimal("0"), estimated_tax_inr - total_tds_inr)

    return {
        "jurisdiction": "India",
        "tax_regime": "Section 115BBH (Virtual Digital Assets)",
        "financial_year": financial_year,
        "fx_rate_usd_to_inr": usd_to_inr_rate,
        "total_gains_usd": total_gains_usd,
        "total_gains_inr": total_gains_inr,
        "total_losses_usd": total_losses_usd,
        "total_losses_inr": total_losses_inr,
        "net_result_usd": total_gains_usd - total_losses_usd,
        "taxable_amount_usd": taxable_amount_usd,
        "taxable_amount_inr": taxable_amount_inr,
        "tax_rate": INDIA_FLAT_TAX_RATE,
        "tax_rate_display": "30% flat (Section 115BBH)",
        "estimated_tax_usd": estimated_tax_usd,
        "estimated_tax_inr": estimated_tax_inr,
        "tds_rate": INDIA_TDS_RATE,
        "tds_rate_display": "1% (Section 194S)",
        "total_tds_deducted_usd": total_tds_usd,
        "total_tds_deducted_inr": total_tds_inr,
        "net_tax_due_usd": net_tax_due_usd,
        "net_tax_due_inr": net_tax_due_inr,
        "loss_offsetting": "Losses from VDAs cannot be set off against gains per Indian tax law (Section 115BBH)",
        "loss_carry_forward": "Losses from VDAs cannot be carried forward per Indian tax law",
        "gain_event_count": len(gain_events),
        "loss_event_count": len(loss_events),
    }


async def calculate_tds_for_transaction(tx: Transaction, db_session) -> Decimal:
    if tx.tx_type in ("transfer_out", "trade", "lp_withdraw", "liquidation") and tx.value_usd:
        tds = calculate_tds(tx.value_usd)
        tx.tds_usd = tds
        return tds
    return Decimal("0")
