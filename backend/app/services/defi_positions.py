"""
DeFi Position Tracker

Aggregates user's DeFi positions from their transaction history.
Tracks LP positions, lending deposits/borrows, and yield farming positions.
"""

import logging
from decimal import Decimal
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.transaction import Transaction

logger = logging.getLogger(__name__)


class DeFiPositionTracker:
    """Tracks active DeFi positions from historical transactions."""

    @staticmethod
    async def get_lp_positions(db: AsyncSession, user_id: str) -> List[Dict[str, Any]]:
        """Get active liquidity pool positions."""
        result = await db.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .where(Transaction.tx_type.in_(["lp_deposit", "lp_withdraw"]))
            .order_by(Transaction.timestamp)
        )
        txs = result.scalars().all()

        positions = {}
        for tx in txs:
            key = f"{tx.chain}:{tx.token_symbol}"
            if tx.tx_type == "lp_deposit":
                if key not in positions:
                    positions[key] = {
                        "chain": tx.chain,
                        "token_symbol": tx.token_symbol,
                        "total_deposited": Decimal("0"),
                        "total_withdrawn": Decimal("0"),
                        "net_quantity": Decimal("0"),
                        "deposits": 0,
                        "withdrawals": 0,
                        "last_activity": tx.timestamp,
                    }
                positions[key]["total_deposited"] += tx.quantity
                positions[key]["net_quantity"] += tx.quantity
                positions[key]["deposits"] += 1
                if tx.timestamp > positions[key]["last_activity"]:
                    positions[key]["last_activity"] = tx.timestamp
            elif tx.tx_type == "lp_withdraw":
                if key not in positions:
                    continue
                positions[key]["total_withdrawn"] += tx.quantity
                positions[key]["net_quantity"] -= tx.quantity
                positions[key]["withdrawals"] += 1
                if tx.timestamp > positions[key]["last_activity"]:
                    positions[key]["last_activity"] = tx.timestamp

        return [
            {
                "chain": p["chain"],
                "token_symbol": p["token_symbol"],
                "total_deposited": float(p["total_deposited"]),
                "total_withdrawn": float(p["total_withdrawn"]),
                "net_quantity": float(p["net_quantity"]),
                "deposit_count": p["deposits"],
                "withdrawal_count": p["withdrawals"],
                "is_active": p["net_quantity"] > Decimal("0"),
                "last_activity": p["last_activity"].isoformat() if p["last_activity"] else None,
            }
            for p in positions.values()
        ]

    @staticmethod
    async def get_lending_positions(db: AsyncSession, user_id: str) -> Dict[str, Any]:
        """Get active lending positions."""
        result = await db.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .where(Transaction.tx_type.in_(["borrow", "repay"]))
            .order_by(Transaction.timestamp)
        )
        txs = result.scalars().all()

        supplies = {}
        borrows = {}
        for tx in txs:
            key = f"{tx.chain}:{tx.token_symbol}"
            if tx.tx_type == "borrow":
                if key not in borrows:
                    borrows[key] = Decimal("0")
                borrows[key] += tx.quantity
            elif tx.tx_type == "repay":
                if key not in borrows:
                    borrows[key] = Decimal("0")
                borrows[key] -= tx.quantity

        positions = []
        all_keys = set(list(borrows.keys()))
        for key in all_keys:
            chain, token = key.split(":", 1)
            net_borrowed = borrows.get(key, Decimal("0"))
            positions.append({
                "chain": chain,
                "token_symbol": token,
                "net_borrowed": float(net_borrowed),
                "is_active": net_borrowed > Decimal("0"),
            })

        return {
            "borrowed_positions": positions,
            "total_active_borrows": sum(1 for p in positions if p["is_active"]),
        }

    @staticmethod
    async def get_yield_farm_positions(db: AsyncSession, user_id: str) -> List[Dict[str, Any]]:
        """Get active yield farming positions."""
        result = await db.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .where(Transaction.tx_type == "yield_farm")
            .order_by(Transaction.timestamp)
        )
        txs = result.scalars().all()

        positions = {}
        for tx in txs:
            key = f"{tx.chain}:{tx.token_symbol}"
            if key not in positions:
                positions[key] = {
                    "chain": tx.chain,
                    "token_symbol": tx.token_symbol,
                    "total_deposited": Decimal("0"),
                    "count": 0,
                    "last_deposit": tx.timestamp,
                }
            positions[key]["total_deposited"] += tx.quantity
            positions[key]["count"] += 1
            if tx.timestamp > positions[key]["last_deposit"]:
                positions[key]["last_deposit"] = tx.timestamp

        return [
            {
                "chain": p["chain"],
                "token_symbol": p["token_symbol"],
                "total_deposited": float(p["total_deposited"]),
                "deposit_count": p["count"],
                "last_deposit": p["last_deposit"].isoformat() if p["last_deposit"] else None,
            }
            for p in positions.values()
        ]
