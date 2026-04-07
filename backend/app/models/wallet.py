from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
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
