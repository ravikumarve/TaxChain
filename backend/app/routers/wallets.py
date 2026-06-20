from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
import re
from decimal import Decimal
from datetime import datetime, timedelta
from app.database import get_db
from app.services.auth_service import get_current_user
from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import Transaction
from app.constants import ALL_CHAINS, CHAIN_ADDRESS_PATTERNS, CHAIN_DISPLAY_NAMES

router = APIRouter()


def validate_wallet_address(address: str, chain: str) -> bool:
    """Validate wallet address format for specific chain"""
    pattern = CHAIN_ADDRESS_PATTERNS.get(chain)
    if not pattern:
        return False
    return bool(re.match(pattern, address))


@router.get("/")
async def list_wallets(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """List all wallets for the authenticated user"""
    result = await db.execute(
        select(Wallet)
        .where(Wallet.user_id == current_user.id)
        .order_by(Wallet.created_at)
    )
    wallets = result.scalars().all()

    return [
        {
            "id": str(wallet.id),
            "address": wallet.address,
            "chain": wallet.chain,
            "label": wallet.label,
            "last_synced_at": wallet.last_synced_at,
            "tx_count": wallet.tx_count,
            "created_at": wallet.created_at,
        }
        for wallet in wallets
    ]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_wallet(
    address: str,
    chain: str,
    label: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a new wallet for the authenticated user"""
    # Validate chain
    chain = chain.lower()
    if chain not in ALL_CHAINS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid chain. Supported chains: {', '.join(sorted(ALL_CHAINS))}",
        )

    # Validate address format
    if not validate_wallet_address(address, chain):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {chain.upper()} address format",
        )

    # Check if wallet already exists for this user
    result = await db.execute(
        select(Wallet).where(
            Wallet.user_id == current_user.id,
            Wallet.address == address,
            Wallet.chain == chain,
        )
    )
    existing_wallet = result.scalar_one_or_none()

    if existing_wallet:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Wallet already exists for this user",
        )

    # Check plan limits (free tier: 1 wallet)
    if current_user.plan == "free":
        result = await db.execute(
            select(func.count()).where(Wallet.user_id == current_user.id)
        )
        wallet_count = result.scalar()

        if wallet_count and wallet_count >= 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Free tier limited to 1 wallet. Upgrade to add more.",
            )

    # Create new wallet
    new_wallet = Wallet(
        user_id=current_user.id, address=address, chain=chain, label=label
    )

    db.add(new_wallet)
    await db.commit()
    await db.refresh(new_wallet)

    return {
        "message": "Wallet added successfully",
        "wallet_id": str(new_wallet.id),
        "address": new_wallet.address,
        "chain": new_wallet.chain,
    }


@router.delete("/{wallet_id}")
async def delete_wallet(
    wallet_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a wallet and its transactions"""
    result = await db.execute(
        select(Wallet).where(Wallet.id == wallet_id, Wallet.user_id == current_user.id)
    )
    wallet = result.scalar_one_or_none()

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found"
        )

    await db.delete(wallet)
    await db.commit()

    return {"message": "Wallet deleted successfully"}


@router.post("/{wallet_id}/sync")
async def sync_wallet(
    wallet_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Trigger manual sync for a wallet.

    Fetches transactions from blockchain, stores them in database,
    categorizes transactions, and updates wallet sync status.
    """
    from app.services.chain_sync import fetch_transactions_with_retry, ChainSyncError
    from app.services.categoriser import TransactionCategorizer
    from app.services.price_engine import get_historical_price
    from sqlalchemy import exists
    import asyncio

    result = await db.execute(
        select(Wallet).where(Wallet.id == wallet_id, Wallet.user_id == current_user.id)
    )
    wallet = result.scalar_one_or_none()

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found"
        )

    try:
        # Fetch transactions from blockchain
        transactions = await fetch_transactions_with_retry(
            str(wallet.address), str(wallet.chain), max_retries=3, retry_delay=2.0
        )

        if not transactions:
            # Update sync timestamp even if no transactions found
            wallet.last_synced_at = func.now()
            wallet.tx_count = 0
            await db.commit()
            return {
                "message": f"No transactions found for wallet {wallet.address}",
                "transactions_processed": 0,
                "new_transactions": 0,
            }

        new_transactions_count = 0
        processed_count = 0
        batch_size = 50  # Process in batches to avoid memory issues

        for i in range(0, len(transactions), batch_size):
            batch = transactions[i : i + batch_size]

            for tx_data in batch:
                processed_count += 1

                # Check if transaction already exists
                tx_exists = await db.execute(
                    select(
                        exists().where(
                            Transaction.tx_hash == tx_data.get("tx_hash"),
                            Transaction.chain == wallet.chain,
                        )
                    )
                )

                if tx_exists.scalar():
                    continue  # Skip existing transactions

                # Categorize transaction
                tx_type = TransactionCategorizer.categorize_transaction(
                    str(wallet.chain), tx_data
                )

                # Extract token symbol (try multiple fields)
                token_symbol = (
                    tx_data.get("token_symbol")
                    or tx_data.get("token_name")
                    or (
                        "ETH"
                        if wallet.chain == "eth"
                        else "BNB"
                        if wallet.chain == "bnb"
                        else "MATIC"
                        if wallet.chain == "polygon"
                        else "SOL"
                    )
                )

                # Extract quantity (handle different field names)
                quantity = Decimal(tx_data.get("value", 0))

                # Get historical price if available
                price_usd = Decimal("0")
                if tx_data.get("timestamp"):
                    try:
                        price_usd = await get_historical_price(
                            token_symbol, tx_data["timestamp"]
                        )
                    except Exception:
                        price_usd = Decimal("0")

                # Calculate value in USD
                value_usd = quantity * price_usd if price_usd > 0 else Decimal("0")

                # Create transaction record
                transaction = Transaction(
                    wallet_id=wallet.id,
                    user_id=current_user.id,
                    tx_hash=tx_data.get("tx_hash", ""),
                    chain=wallet.chain,
                    tx_type=tx_type,
                    token_symbol=token_symbol,
                    token_address=tx_data.get("contract_address", ""),
                    quantity=quantity,
                    price_usd=price_usd,
                    value_usd=value_usd,
                    fee_usd=Decimal(tx_data.get("fee", 0))
                    if tx_data.get("fee")
                    else Decimal("0"),
                    timestamp=tx_data.get("timestamp")
                    or tx_data.get("block_time")
                    or func.now(),
                    raw_data=tx_data.get("raw_data", {}),
                )

                db.add(transaction)
                new_transactions_count += 1

            # Commit batch to database
            await db.commit()

            # Add small delay between batches to respect rate limits
            await asyncio.sleep(0.1)

        # Update wallet sync status
        wallet.last_synced_at = func.now()

        # Update transaction count
        tx_count_result = await db.execute(
            select(func.count()).where(Transaction.wallet_id == wallet.id)
        )
        wallet.tx_count = tx_count_result.scalar()

        await db.commit()

        return {
            "message": f"Successfully synced wallet {wallet.address}",
            "transactions_processed": processed_count,
            "new_transactions": new_transactions_count,
            "total_transactions": wallet.tx_count,
        }

    except ChainSyncError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch transactions from blockchain: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during wallet sync: {str(e)}",
        )


@router.get("/portfolio")
async def get_portfolio(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get aggregated portfolio data for the authenticated user.
    Returns live data from DB if wallets/transactions exist,
    otherwise returns realistic simulated data with 'source: simulated'.
    """
    from decimal import Decimal as D
    from collections import defaultdict

    # 1. Fetch user's wallets
    wallet_result = await db.execute(
        select(Wallet).where(Wallet.user_id == current_user.id)
    )
    wallets = wallet_result.scalars().all()
    wallet_count = len(wallets)

    # 2. Fetch user's transactions
    tx_result = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .order_by(Transaction.timestamp)
    )
    transactions = tx_result.scalars().all()
    tx_count = len(transactions)

    # ── LIVE DATA PATH ──────────────────────────────────────────────
    if wallet_count > 0 and tx_count > 0:
        # Chain breakdown: sum value_usd per chain
        chain_values = defaultdict(D)
        for tx in transactions:
            if tx.value_usd:
                chain_values[tx.chain] += D(str(tx.value_usd))

        total_value = sum(chain_values.values(), D("0"))
        chain_breakdown = [
            {
                "chain": chain,
                "value_usd": float(val),
                "percentage": round(float(val / total_value * 100), 1) if total_value > 0 else 0,
            }
            for chain, val in sorted(chain_values.items(), key=lambda x: -x[1])
        ]

        # Token breakdown: sum value_usd per token_symbol
        token_values = defaultdict(lambda: {"value_usd": D("0"), "quantity": D("0")})
        for tx in transactions:
            sym = tx.token_symbol or "UNKNOWN"
            token_values[sym]["value_usd"] += D(str(tx.value_usd or 0))
            token_values[sym]["quantity"] += D(str(tx.quantity or 0))

        sorted_tokens = sorted(token_values.items(), key=lambda x: -x[1]["value_usd"])
        token_breakdown = [
            {
                "token_symbol": sym,
                "value_usd": float(data["value_usd"]),
                "percentage": round(float(data["value_usd"] / total_value * 100), 1) if total_value > 0 else 0,
                "quantity": float(data["quantity"]),
            }
            for sym, data in sorted_tokens
        ]

        # Cost basis / unrealized P&L from cost_basis_lots
        from app.models.cost_basis_lot import CostBasisLot

        cb_result = await db.execute(
            select(CostBasisLot).where(CostBasisLot.user_id == current_user.id)
        )
        cost_basis_lots = cb_result.scalars().all()

        total_cost_basis = sum(D(str(lot.cost_per_unit_usd)) * D(str(lot.quantity_remaining)) for lot in cost_basis_lots) if cost_basis_lots else D("0")

        if total_cost_basis > 0:
            unrealized_pnl = total_value - total_cost_basis
            unrealized_pnl_percent = round(float(unrealized_pnl / total_cost_basis * 100), 2) if total_cost_basis > 0 else 0
        else:
            unrealized_pnl = total_value
            unrealized_pnl_percent = 100.0

        # P&L timeline: monthly snapshots of cumulative value
        monthly_values = defaultdict(D)
        for tx in transactions:
            if tx.timestamp and tx.value_usd:
                month_key = tx.timestamp.strftime("%Y-%m")
                monthly_values[month_key] += D(str(tx.value_usd))

        sorted_months = sorted(monthly_values.keys())
        cumulative = D("0")
        pnl_timeline = []
        for month in sorted_months:
            cumulative += monthly_values[month]
            pnl_timeline.append({
                "date": f"{month}-01",
                "value_usd": float(cumulative),
            })

        if not pnl_timeline:
            pnl_timeline = [
                {"date": "2026-01-01", "value_usd": float(total_value)},
            ]

        # Top movers: per-token unrealized P&L
        top_movers = []
        for sym, data in sorted_tokens[:5]:
            qty = data["quantity"]
            val = data["value_usd"]
            # Estimate cost from lots if available
            token_cost = D("0")
            if cost_basis_lots:
                for lot in cost_basis_lots:
                    if lot.token_symbol == sym:
                        token_cost += D(str(lot.cost_per_unit_usd)) * D(str(lot.quantity_remaining))
            pnl_val = val - float(token_cost) if token_cost > 0 else val * D("0.05")
            pnl_pct = round(float(pnl_val / val * 100), 1) if val > 0 else 0
            chain_for_token = "unknown"
            for tx in transactions:
                if tx.token_symbol == sym and tx.chain:
                    chain_for_token = tx.chain
                    break
            top_movers.append({
                "token_symbol": sym,
                "pnl_usd": round(float(pnl_val), 2),
                "pnl_percent": pnl_pct,
                "chain": chain_for_token,
            })

        return {
            "total_value_usd": float(total_value),
            "total_cost_basis_usd": float(total_cost_basis),
            "unrealized_pnl_usd": round(float(unrealized_pnl), 2),
            "unrealized_pnl_percent": unrealized_pnl_percent,
            "wallet_count": wallet_count,
            "transaction_count": tx_count,
            "chain_breakdown": chain_breakdown,
            "token_breakdown": token_breakdown,
            "pnl_timeline": pnl_timeline,
            "top_movers": top_movers,
            "source": "live",
        }

    # ── SIMULATED DATA PATH ─────────────────────────────────────────
    simulated_data = {
        "total_value_usd": 12420.50,
        "total_cost_basis_usd": 11180.20,
        "unrealized_pnl_usd": 1240.30,
        "unrealized_pnl_percent": 11.09,
        "wallet_count": 3,
        "transaction_count": 145,
        "chain_breakdown": [
            {"chain": "eth", "value_usd": 8200.00, "percentage": 66.0},
            {"chain": "bnb", "value_usd": 3220.50, "percentage": 25.9},
            {"chain": "polygon", "value_usd": 1000.00, "percentage": 8.1},
        ],
        "token_breakdown": [
            {"token_symbol": "ETH", "value_usd": 7200.00, "percentage": 57.9, "quantity": 2.5},
            {"token_symbol": "BNB", "value_usd": 3220.50, "percentage": 25.9, "quantity": 15.0},
            {"token_symbol": "MATIC", "value_usd": 1000.00, "percentage": 8.1, "quantity": 2000.0},
            {"token_symbol": "USDC", "value_usd": 500.00, "percentage": 4.0, "quantity": 500.0},
            {"token_symbol": "LINK", "value_usd": 500.00, "percentage": 4.0, "quantity": 25.0},
        ],
        "pnl_timeline": [
            {"date": "2026-01-01", "value_usd": 10000.00},
            {"date": "2026-02-01", "value_usd": 11200.00},
            {"date": "2026-03-01", "value_usd": 10900.00},
            {"date": "2026-04-01", "value_usd": 11450.00},
            {"date": "2026-05-01", "value_usd": 11900.00},
            {"date": "2026-06-01", "value_usd": 12420.50},
        ],
        "top_movers": [
            {"token_symbol": "ETH", "pnl_usd": 520.00, "pnl_percent": 12.0, "chain": "eth"},
            {"token_symbol": "BNB", "pnl_usd": 280.50, "pnl_percent": 9.5, "chain": "bnb"},
            {"token_symbol": "MATIC", "pnl_usd": -120.00, "pnl_percent": -5.5, "chain": "polygon"},
            {"token_symbol": "LINK", "pnl_usd": 85.00, "pnl_percent": 20.5, "chain": "eth"},
        ],
        "source": "simulated",
    }

    return simulated_data


@router.get("/{wallet_id}/status")
async def get_wallet_status(
    wallet_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get sync status and transaction count for a wallet"""
    result = await db.execute(
        select(Wallet).where(Wallet.id == wallet_id, Wallet.user_id == current_user.id)
    )
    wallet = result.scalar_one_or_none()

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found"
        )

    # Get transaction count
    result = await db.execute(
        select(func.count()).where(Transaction.wallet_id == wallet_id)
    )
    tx_count = result.scalar()

    return {
        "wallet_id": str(wallet.id),
        "address": wallet.address,
        "chain": wallet.chain,
        "last_synced_at": wallet.last_synced_at,
        "transaction_count": tx_count,
        "status": "synced" if wallet.last_synced_at else "pending",
    }


@router.get("/defi-positions")
async def get_defi_positions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Aggregate DeFi positions across all user wallets.
    Returns active liquidity pools, lending positions, and yield farms.
    """
    from app.services.defi_positions import DeFiPositionTracker

    try:
        lp_positions = await DeFiPositionTracker.get_lp_positions(db, str(current_user.id))
        lending = await DeFiPositionTracker.get_lending_positions(db, str(current_user.id))
        yield_farms = await DeFiPositionTracker.get_yield_farm_positions(db, str(current_user.id))

        return {
            "lp_positions": lp_positions,
            "lending": lending,
            "yield_farms": yield_farms,
            "total_positions": len(lp_positions) + lending["total_active_borrows"] + len(yield_farms),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching DeFi positions: {str(e)}",
        )
