from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List
import re
from app.database import get_db
from app.services.auth_service import get_current_user
from app.models.user import User
from app.models.wallet import Wallet

router = APIRouter()

# Chain-specific address validation regex patterns
CHAIN_VALIDATION = {
    "eth": r"^0x[a-fA-F0-9]{40}$",
    "bnb": r"^0x[a-fA-F0-9]{40}$",
    "polygon": r"^0x[a-fA-F0-9]{40}$",
    "sol": r"^[1-9A-HJ-NP-Za-km-z]{32,44}$",
}

VALID_CHAINS = {"eth", "bnb", "polygon", "sol"}


def validate_wallet_address(address: str, chain: str) -> bool:
    """Validate wallet address format for specific chain"""
    if chain not in VALID_CHAINS:
        return False

    pattern = CHAIN_VALIDATION[chain]
    return bool(re.match(pattern, address))


@router.get("/", response_model=None)
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
