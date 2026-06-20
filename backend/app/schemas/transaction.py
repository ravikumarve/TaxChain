from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime


class ManualTransactionCreate(BaseModel):
    wallet_id: Optional[str] = None
    chain: str
    tx_type: str
    token_symbol: str
    token_address: Optional[str] = None
    quantity: Decimal
    price_usd: Optional[Decimal] = None
    value_usd: Optional[Decimal] = None
    fee_usd: Optional[Decimal] = None
    timestamp: datetime
    tx_hash: Optional[str] = None
    notes: Optional[str] = None


class ManualTransactionUpdate(BaseModel):
    chain: Optional[str] = None
    tx_type: Optional[str] = None
    token_symbol: Optional[str] = None
    token_address: Optional[str] = None
    quantity: Optional[Decimal] = None
    price_usd: Optional[Decimal] = None
    value_usd: Optional[Decimal] = None
    fee_usd: Optional[Decimal] = None
    timestamp: Optional[datetime] = None
    notes: Optional[str] = None
