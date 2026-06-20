"""
Settings router — user preferences including cost basis method selection.
Changing the method triggers recalculation of all tax events.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.auth_service import get_current_user
from app.models.user import User
from app.schemas.user import UpdateCostBasisMethod

logger = logging.getLogger(__name__)
router = APIRouter()

VALID_METHODS = {"fifo", "lifo", "hifo", "avg_cost"}


@router.get("/cost-basis-method")
async def get_cost_basis_method(
    current_user: User = Depends(get_current_user),
):
    return {"method": current_user.cost_basis_method}


@router.put("/cost-basis-method")
async def update_cost_basis_method(
    data: UpdateCostBasisMethod,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    method = data.method.lower()
    if method not in VALID_METHODS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid method '{data.method}'. Must be one of: {', '.join(sorted(VALID_METHODS))}",
        )

    current_user.cost_basis_method = method
    await db.commit()

    # Recalculate all tax events for this user
    from app.models.transaction import Transaction
    from app.models.tax_event import TaxEvent
    from app.models.cost_basis_lot import CostBasisLot
    from app.services.tax_engine import calculate_with_method
    from sqlalchemy import delete, select
    from sqlalchemy.future import select as sql_select

    # Delete existing tax events and lots
    await db.execute(
        delete(TaxEvent).where(TaxEvent.user_id == current_user.id)
    )
    await db.execute(
        delete(CostBasisLot).where(CostBasisLot.user_id == current_user.id)
    )
    await db.commit()

    # Fetch all transactions grouped by token
    result = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .order_by(Transaction.timestamp)
    )
    transactions = result.scalars().all()

    transactions_by_token = {}
    for tx in transactions:
        if tx.token_symbol:
            if tx.token_symbol not in transactions_by_token:
                transactions_by_token[tx.token_symbol] = []
            transactions_by_token[tx.token_symbol].append(tx)

    new_events = []
    for token_symbol, token_txs in transactions_by_token.items():
        try:
            events = calculate_with_method(
                method, str(current_user.id), token_symbol, token_txs
            )
            for ev in events:
                db.add(ev)
                new_events.append(ev)
        except Exception as e:
            logger.error(f"Error recalculating {token_symbol}: {e}")
            continue

    await db.commit()

    return {
        "method": method,
        "recalculated": True,
        "events_recalculated": len(new_events),
    }
