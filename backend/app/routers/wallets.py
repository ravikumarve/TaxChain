from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()


@router.get("/")
async def list_wallets(db: AsyncSession = Depends(get_db)):
    return {"message": "List wallets endpoint - TODO"}


@router.post("/")
async def add_wallet(db: AsyncSession = Depends(get_db)):
    return {"message": "Add wallet endpoint - TODO"}


@router.delete("/{wallet_id}")
async def delete_wallet(wallet_id: str, db: AsyncSession = Depends(get_db)):
    return {"message": f"Delete wallet {wallet_id} - TODO"}


@router.post("/{wallet_id}/sync")
async def sync_wallet(wallet_id: str, db: AsyncSession = Depends(get_db)):
    return {"message": f"Sync wallet {wallet_id} - TODO"}
