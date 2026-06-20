import csv
import io
import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_
from app.database import get_db
from app.services.auth_service import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.models.wallet import Wallet
from app.constants import ALL_CHAINS
from app.schemas.transaction import ManualTransactionCreate, ManualTransactionUpdate

router = APIRouter()

# Valid transaction types
VALID_TX_TYPES = {
    "trade",
    "transfer_in",
    "transfer_out",
    "staking",
    "airdrop",
    "nft_sale",
    "fee",
    "lp_deposit",
    "lp_withdraw",
    "borrow",
    "repay",
    "yield_farm",
    "liquidation",
}

# Known tokens for reconciliation check
KNOWN_TOKENS = {
    "ETH", "BTC", "BNB", "SOL", "MATIC", "ARB", "OP",
    "USDT", "USDC", "DAI", "BUSD", "WBTC", "WETH", "WBNB",
    "LINK", "UNI", "AAVE", "CRV", "MKR", "COMP", "SNX",
    "AXS", "SAND", "MANA", "APE", "SHIB", "FLOKI", "PEPE",
    "STETH", "LDO", "RPL", "CVX", "YFI", "SUSHI", "CAKE",
    "INJ", "TIA", "SEI", "SUI", "APT", "ARB",
}


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
    if chain and chain not in ALL_CHAINS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid chain. Supported chains: {', '.join(sorted(ALL_CHAINS))}",
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
    if chain and chain not in ALL_CHAINS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid chain. Supported chains: {', '.join(sorted(ALL_CHAINS))}",
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


async def _get_or_create_virtual_wallet(
    db: AsyncSession, user_id, chain: str
) -> Wallet:
    """Find existing virtual wallet for chain, or create one."""
    result = await db.execute(
        select(Wallet).where(
            Wallet.user_id == user_id,
            Wallet.address == f"manual_entry",
            Wallet.chain == chain,
        )
    )
    wallet = result.scalar_one_or_none()
    if wallet:
        return wallet

    wallet = Wallet(
        user_id=user_id,
        address="manual_entry",
        chain=chain,
        label="Manual Entry",
    )
    db.add(wallet)
    await db.commit()
    await db.refresh(wallet)
    return wallet


def _serialize_tx(tx: Transaction) -> dict:
    return {
        "id": str(tx.id),
        "wallet_id": str(tx.wallet_id),
        "tx_hash": tx.tx_hash,
        "chain": tx.chain,
        "tx_type": tx.tx_type,
        "token_symbol": tx.token_symbol,
        "token_address": tx.token_address,
        "quantity": float(tx.quantity) if tx.quantity else None,
        "price_usd": float(tx.price_usd) if tx.price_usd else None,
        "value_usd": float(tx.value_usd) if tx.value_usd else None,
        "fee_usd": float(tx.fee_usd) if tx.fee_usd else None,
        "timestamp": tx.timestamp.isoformat() if tx.timestamp else None,
        "created_at": tx.created_at.isoformat() if tx.created_at else None,
        "notes": (tx.raw_data or {}).get("notes") if tx.raw_data else None,
    }


@router.post("/manual", status_code=201)
async def create_manual_transaction(
    tx_data: ManualTransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a manual transaction entry."""
    chain = tx_data.chain.lower()
    if chain not in ALL_CHAINS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid chain. Supported: {', '.join(sorted(ALL_CHAINS))}",
        )

    tx_type = tx_data.tx_type.lower()
    if tx_type not in VALID_TX_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transaction type. Supported: {', '.join(VALID_TX_TYPES)}",
        )

    tx_hash = tx_data.tx_hash
    if not tx_hash:
        tx_hash = f"manual_{uuid.uuid4().hex}"

    # Resolve wallet
    wallet_id = tx_data.wallet_id
    if wallet_id:
        result = await db.execute(
            select(Wallet).where(
                Wallet.id == wallet_id, Wallet.user_id == current_user.id
            )
        )
        wallet = result.scalar_one_or_none()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
    else:
        wallet = await _get_or_create_virtual_wallet(db, current_user.id, chain)
        wallet_id = wallet.id

    raw_data = {"notes": tx_data.notes} if tx_data.notes else {}

    tx = Transaction(
        wallet_id=wallet_id,
        user_id=current_user.id,
        tx_hash=tx_hash,
        chain=chain,
        tx_type=tx_type,
        token_symbol=tx_data.token_symbol,
        token_address=tx_data.token_address,
        quantity=tx_data.quantity,
        price_usd=tx_data.price_usd,
        value_usd=tx_data.value_usd,
        fee_usd=tx_data.fee_usd,
        timestamp=tx_data.timestamp,
        raw_data=raw_data,
    )
    db.add(tx)
    await db.commit()
    await db.refresh(tx)

    return _serialize_tx(tx)


@router.put("/{tx_id}")
async def update_transaction(
    tx_id: str,
    tx_data: ManualTransactionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a manual transaction. Rejects synced (non-manual) transactions."""
    result = await db.execute(
        select(Transaction)
        .join(Wallet, Transaction.wallet_id == Wallet.id)
        .where(Transaction.id == tx_id, Wallet.user_id == current_user.id)
    )
    tx = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if not tx.tx_hash.startswith("manual_"):
        raise HTTPException(status_code=403, detail="Cannot edit synced blockchain transactions")

    # Update only provided fields
    update_data = tx_data.model_dump(exclude_unset=True)
    notes = update_data.pop("notes", None)

    for field, value in update_data.items():
        if field == "chain" and value:
            value = value.lower()
        if field == "tx_type" and value:
            value = value.lower()
        setattr(tx, field, value)

    if notes is not None:
        raw = tx.raw_data or {}
        raw["notes"] = notes
        tx.raw_data = raw

    await db.commit()
    await db.refresh(tx)

    return _serialize_tx(tx)


@router.delete("/{tx_id}")
async def delete_transaction(
    tx_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a manual transaction. Rejects synced blockchain transactions."""
    result = await db.execute(
        select(Transaction)
        .join(Wallet, Transaction.wallet_id == Wallet.id)
        .where(Transaction.id == tx_id, Wallet.user_id == current_user.id)
    )
    tx = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if not tx.tx_hash.startswith("manual_"):
        raise HTTPException(status_code=403, detail="Cannot delete synced blockchain transactions")

    await db.delete(tx)
    await db.commit()

    return {"detail": "Transaction deleted successfully"}


COLUMN_ALIASES = {
    "date": "timestamp",
    "datetime": "timestamp",
    "time": "timestamp",
    "type": "tx_type",
    "transaction type": "tx_type",
    "tx_type": "tx_type",
    "token": "token_symbol",
    "currency": "token_symbol",
    "symbol": "token_symbol",
    "coin": "token_symbol",
    "asset": "token_symbol",
    "token symbol": "token_symbol",
    "qty": "quantity",
    "amount": "quantity",
    "quantity": "quantity",
    "price": "price_usd",
    "price usd": "price_usd",
    "value": "value_usd",
    "value usd": "value_usd",
    "fee": "fee_usd",
    "fee usd": "fee_usd",
    "chain": "chain",
    "network": "chain",
    "blockchain": "chain",
    "tx hash": "tx_hash",
    "txhash": "tx_hash",
    "transaction hash": "tx_hash",
    "hash": "tx_hash",
    "notes": "notes",
    "note": "notes",
    "comment": "notes",
}


def _normalize_column_name(name: str) -> Optional[str]:
    key = name.strip().lower().replace("-", " ").replace("_", " ")
    return COLUMN_ALIASES.get(key)


def _parse_csv_rows(reader: csv.DictReader) -> dict:
    headers = reader.fieldnames or []
    # Detect columns
    column_map = {}
    for h in headers:
        mapped = _normalize_column_name(h)
        if mapped:
            column_map[h] = mapped

    required = {"timestamp", "tx_type", "token_symbol", "quantity"}
    missing = required - set(column_map.values())
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"CSV missing required columns: {', '.join(missing)}. Found headers: {headers}",
        )

    rows = []
    valid_count = 0
    error_count = 0

    for i, row in enumerate(reader, start=1):
        entry = {"row": i, "data": {}, "warnings": [], "errors": []}
        try:
            for orig_col, mapped_col in column_map.items():
                val = row.get(orig_col, "").strip()
                if val:
                    entry["data"][mapped_col] = val

            # Validate timestamp
            ts = entry["data"].get("timestamp")
            if ts:
                try:
                    datetime.fromisoformat(ts.replace("Z", "+00:00"))
                except ValueError:
                    entry["errors"].append(f"Invalid date format: {ts}")

            # Validate tx_type
            ttype = entry["data"].get("tx_type", "").lower()
            if ttype not in VALID_TX_TYPES:
                entry["warnings"].append(f"Unknown type '{ttype}', will be saved as-is")

            # Validate chain
            chain = entry["data"].get("chain", "").lower()
            if chain and chain not in ALL_CHAINS:
                entry["warnings"].append(f"Unknown chain '{chain}', will be saved as-is")

            # Validate quantity
            qty = entry["data"].get("quantity")
            if qty:
                try:
                    Decimal(qty)
                except Exception:
                    entry["errors"].append(f"Invalid quantity: {qty}")

            if not entry["errors"]:
                valid_count += 1
            else:
                error_count += 1

        except Exception as e:
            entry["errors"].append(str(e))
            error_count += 1

        rows.append(entry)

    return {
        "columns": list(column_map.keys()),
        "rows": rows,
        "total_rows": len(rows),
        "valid_rows": valid_count,
        "error_rows": error_count,
    }


@router.post("/csv-preview")
async def preview_csv_import(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Preview CSV import without saving to database."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    content = await file.read()
    text = content.decode("utf-8-sig")

    reader = csv.DictReader(io.StringIO(text))
    return _parse_csv_rows(reader)


@router.post("/csv-commit")
async def commit_csv_import(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Parse CSV and import valid rows as manual transactions."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    content = await file.read()
    text = content.decode("utf-8-sig")

    reader = csv.DictReader(io.StringIO(text))
    parsed = _parse_csv_rows(reader)

    saved = 0
    errors = []

    for entry in parsed["rows"]:
        if entry["errors"]:
            errors.append({"row": entry["row"], "errors": entry["errors"]})
            continue

        data = entry["data"]
        chain = data.get("chain", "eth").lower()
        if chain not in ALL_CHAINS:
            chain = "eth"

        tx_type = data.get("tx_type", "").lower()
        if tx_type not in VALID_TX_TYPES:
            tx_type = "trade"

        try:
            timestamp = datetime.fromisoformat(
                data.get("timestamp", "").replace("Z", "+00:00")
            )
        except ValueError:
            timestamp = datetime.utcnow()

        quantity = Decimal(data.get("quantity", "0"))
        price_str = data.get("price_usd")
        price = Decimal(price_str) if price_str else None
        value_str = data.get("value_usd")
        value = Decimal(value_str) if value_str else None
        fee_str = data.get("fee_usd")
        fee = Decimal(fee_str) if fee_str else None
        tx_hash = data.get("tx_hash") or f"manual_{uuid.uuid4().hex}"

        wallet = await _get_or_create_virtual_wallet(db, current_user.id, chain)
        notes = data.get("notes")

        tx = Transaction(
            wallet_id=wallet.id,
            user_id=current_user.id,
            tx_hash=tx_hash,
            chain=chain,
            tx_type=tx_type,
            token_symbol=data.get("token_symbol", ""),
            token_address=data.get("token_address"),
            quantity=quantity,
            price_usd=price,
            value_usd=value,
            fee_usd=fee,
            timestamp=timestamp,
            raw_data={"notes": notes} if notes else {},
        )
        db.add(tx)
        saved += 1

    await db.commit()

    return {
        "saved": saved,
        "total": parsed["total_rows"],
        "errors": errors,
    }


@router.get("/reconcile")
async def reconcile_transactions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Analyze transactions for data quality issues."""
    # Base query for user's transactions
    base_query = (
        select(Transaction)
        .join(Wallet, Transaction.wallet_id == Wallet.id)
        .where(Wallet.user_id == current_user.id)
    )

    # 1. Missing price data (trade tx with null price_usd)
    missing_price_query = base_query.where(
        Transaction.tx_type == "trade",
        Transaction.price_usd.is_(None),
    )
    result = await db.execute(missing_price_query)
    missing_price_txs = result.scalars().all()

    # 2. Unknown token symbols (null or empty)
    unknown_token_query = base_query.where(
        or_(
            Transaction.token_symbol.is_(None),
            Transaction.token_symbol == "",
        )
    )
    result = await db.execute(unknown_token_query)
    unknown_token_txs = result.scalars().all()

    # 3. Unclassified types (not in VALID_TX_TYPES)
    unclassified_query = base_query.where(
        ~Transaction.tx_type.in_(VALID_TX_TYPES)
    )
    result = await db.execute(unclassified_query)
    unclassified_txs = result.scalars().all()

    # 4. Duplicate tx_hash for same user
    dup_subquery = (
        select(Transaction.tx_hash)
        .join(Wallet, Transaction.wallet_id == Wallet.id)
        .where(Wallet.user_id == current_user.id)
        .group_by(Transaction.tx_hash)
        .having(func.count(Transaction.id) > 1)
    )
    result = await db.execute(dup_subquery)
    dup_hashes = [row[0] for row in result.fetchall()]

    duplicate_txs = []
    if dup_hashes:
        dup_tx_query = base_query.where(Transaction.tx_hash.in_(dup_hashes)).order_by(
            Transaction.tx_hash, Transaction.timestamp
        )
        result = await db.execute(dup_tx_query)
        duplicate_txs = result.scalars().all()

    def _tx_minimal(tx):
        return {
            "id": str(tx.id),
            "tx_hash": tx.tx_hash,
            "token_symbol": tx.token_symbol,
            "chain": tx.chain,
            "tx_type": tx.tx_type,
            "quantity": float(tx.quantity) if tx.quantity else None,
            "price_usd": float(tx.price_usd) if tx.price_usd else None,
            "timestamp": tx.timestamp.isoformat() if tx.timestamp else None,
        }

    result = {
        "missing_price": {
            "count": len(missing_price_txs),
            "transactions": [_tx_minimal(tx) for tx in missing_price_txs],
        },
        "unknown_token": {
            "count": len(unknown_token_txs),
            "transactions": [_tx_minimal(tx) for tx in unknown_token_txs],
        },
        "unclassified_type": {
            "count": len(unclassified_txs),
            "transactions": [_tx_minimal(tx) for tx in unclassified_txs],
        },
        "duplicate_hash": {
            "count": len(duplicate_txs),
            "transactions": [_tx_minimal(tx) for tx in duplicate_txs],
        },
        "total_issues": len(missing_price_txs)
        + len(unknown_token_txs)
        + len(unclassified_txs)
        + len(duplicate_txs),
    }

    return result
