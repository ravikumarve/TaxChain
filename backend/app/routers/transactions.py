from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_
from app.database import get_db
from app.services.auth_service import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.models.wallet import Wallet

router = APIRouter()

# Valid transaction types from AGENTS.md
VALID_TX_TYPES = {
    "trade",
    "transfer_in",
    "transfer_out",
    "staking",
    "airdrop",
    "nft_sale",
    "fee",
}
VALID_CHAINS = {"eth", "bnb", "polygon", "sol"}


@router.get("/")
async def list_transactions(
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    limit: int = Query(
        50, ge=1, le=200, description="Number of items per page (1-200)"
    ),
    chain: Optional[str] = Query(
        None, description="Filter by blockchain: eth, bnb, polygon, sol"
    ),
    tx_type: Optional[str] = Query(
        None,
        description="Filter by transaction type: trade, transfer_in, transfer_out, staking, airdrop, nft_sale, fee",
    ),
    start_date: Optional[date] = Query(
        None, description="Start date for filtering (YYYY-MM-DD)"
    ),
    end_date: Optional[date] = Query(
        None, description="End date for filtering (YYYY-MM-DD)"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get paginated list of transactions for authenticated user with filtering capabilities
    """
    # Validate filters
    if chain and chain not in VALID_CHAINS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid chain. Supported chains: {', '.join(VALID_CHAINS)}",
        )

    if tx_type and tx_type not in VALID_TX_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transaction type. Supported types: {', '.join(VALID_TX_TYPES)}",
        )

    # Build base query
    query = (
        select(Transaction)
        .join(Wallet, Transaction.wallet_id == Wallet.id)
        .where(Wallet.user_id == current_user.id)
        .order_by(Transaction.timestamp.desc())
    )

    # Apply filters
    if chain:
        query = query.where(Transaction.chain == chain)

    if tx_type:
        query = query.where(Transaction.tx_type == tx_type)

    if start_date:
        query = query.where(
            Transaction.timestamp >= datetime.combine(start_date, datetime.min.time())
        )

    if end_date:
        query = query.where(
            Transaction.timestamp <= datetime.combine(end_date, datetime.max.time())
        )

    # Get total count for pagination
    count_query = query.with_only_columns(func.count(Transaction.id))
    result = await db.execute(count_query)
    total_count = result.scalar()

    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    # Execute query
    result = await db.execute(query)
    transactions = result.scalars().all()

    # Format response
    return {
        "transactions": [
            {
                "id": str(tx.id),
                "tx_hash": tx.tx_hash,
                "chain": tx.chain,
                "tx_type": tx.tx_type,
                "token_symbol": tx.token_symbol,
                "token_address": tx.token_address,
                "quantity": float(tx.quantity) if tx.quantity else None,
                "price_usd": float(tx.price_usd) if tx.price_usd else None,
                "value_usd": float(tx.value_usd) if tx.value_usd else None,
                "fee_usd": float(tx.fee_usd) if tx.fee_usd else None,
                "timestamp": tx.timestamp,
                "created_at": tx.created_at,
                "wallet_id": str(tx.wallet_id),
            }
            for tx in transactions
        ],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total_count,
            "pages": (total_count + limit - 1) // limit if total_count > 0 else 0,
        },
    }


@router.get("/summary")
async def get_transaction_summary(
    chain: Optional[str] = Query(
        None, description="Filter by blockchain: eth, bnb, polygon, sol"
    ),
    tx_type: Optional[str] = Query(
        None,
        description="Filter by transaction type: trade, transfer_in, transfer_out, staking, airdrop, nft_sale, fee",
    ),
    start_date: Optional[date] = Query(
        None, description="Start date for filtering (YYYY-MM-DD)"
    ),
    end_date: Optional[date] = Query(
        None, description="End date for filtering (YYYY-MM-DD)"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get aggregated transaction statistics for authenticated user
    """
    # Validate filters
    if chain and chain not in VALID_CHAINS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid chain. Supported chains: {', '.join(VALID_CHAINS)}",
        )

    if tx_type and tx_type not in VALID_TX_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transaction type. Supported types: {', '.join(VALID_TX_TYPES)}",
        )

    # Build base query
    query = (
        select(
            func.count(Transaction.id).label("total_transactions"),
            func.count(func.distinct(Transaction.chain)).label("chains_count"),
            func.count(func.distinct(Transaction.tx_type)).label("types_count"),
            func.sum(Transaction.value_usd).label("total_value_usd"),
            func.sum(Transaction.fee_usd).label("total_fee_usd"),
            func.min(Transaction.timestamp).label("first_transaction"),
            func.max(Transaction.timestamp).label("last_transaction"),
        )
        .join(Wallet, Transaction.wallet_id == Wallet.id)
        .where(Wallet.user_id == current_user.id)
    )

    # Apply filters
    if chain:
        query = query.where(Transaction.chain == chain)

    if tx_type:
        query = query.where(Transaction.tx_type == tx_type)

    if start_date:
        query = query.where(
            Transaction.timestamp >= datetime.combine(start_date, datetime.min.time())
        )

    if end_date:
        query = query.where(
            Transaction.timestamp <= datetime.combine(end_date, datetime.max.time())
        )

    # Execute query
    result = await db.execute(query)
    summary = result.first()

    if not summary:
        return {
            "total_transactions": 0,
            "chains_count": 0,
            "types_count": 0,
            "total_value_usd": 0.0,
            "total_fee_usd": 0.0,
            "first_transaction": None,
            "last_transaction": None,
        }

    return {
        "total_transactions": summary.total_transactions,
        "chains_count": summary.chains_count,
        "types_count": summary.types_count,
        "total_value_usd": float(summary.total_value_usd)
        if summary.total_value_usd
        else 0.0,
        "total_fee_usd": float(summary.total_fee_usd) if summary.total_fee_usd else 0.0,
        "first_transaction": summary.first_transaction,
        "last_transaction": summary.last_transaction,
    }
