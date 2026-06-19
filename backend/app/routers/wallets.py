from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
import re
from decimal import Decimal
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
