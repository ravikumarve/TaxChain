from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()


@router.get("/")
async def list_transactions(db: AsyncSession = Depends(get_db)):
    return {"message": "List transactions endpoint - TODO"}


@router.get("/summary")
async def get_transaction_summary(db: AsyncSession = Depends(get_db)):
    return {"message": "Transaction summary endpoint - TODO"}
