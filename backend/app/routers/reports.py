from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()


@router.get("/tax/summary")
async def get_tax_summary(db: AsyncSession = Depends(get_db)):
    return {"message": "Tax summary endpoint - TODO"}


@router.post("/csv")
async def generate_csv_report(db: AsyncSession = Depends(get_db)):
    return {"message": "CSV report endpoint - TODO"}


@router.post("/pdf")
async def generate_pdf_report(db: AsyncSession = Depends(get_db)):
    return {"message": "PDF report endpoint - TODO"}


@router.post("/itr")
async def generate_itr_report(db: AsyncSession = Depends(get_db)):
    return {"message": "ITR report endpoint - TODO"}
