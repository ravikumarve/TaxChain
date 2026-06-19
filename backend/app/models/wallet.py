from sqlalchemy import Column, String, DateTime, Integer, func
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.database_utils import uuid_column, uuid_foreign_key


class Wallet(Base):
    __tablename__ = "wallets"

    id = uuid_column()
    user_id = uuid_foreign_key("users.id")
    address = Column(String(255), nullable=False)
    chain = Column(String(20), nullable=False)  # eth | bnb | polygon | sol
    label = Column(String(100))
    last_synced_at = Column(DateTime)
    tx_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="wallets")
    transactions = relationship(
        "Transaction", back_populates="wallet", cascade="all, delete-orphan"
    )
