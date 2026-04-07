from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import DECIMAL
from app.database import Base
import uuid


class TaxEvent(Base):
    __tablename__ = "tax_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_symbol = Column(String(50), nullable=False)
    quantity = Column(DECIMAL(36, 18), nullable=False)
    proceeds_usd = Column(DECIMAL(20, 8), nullable=False)
    cost_basis_usd = Column(DECIMAL(20, 8), nullable=False)
    gain_loss_usd = Column(DECIMAL(20, 8), nullable=False)
    is_short_term = Column(Boolean)
    sale_tx_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"))
    acquired_at = Column(DateTime)
    disposed_at = Column(DateTime, nullable=False)
    financial_year = Column(String(10))

    # Relationships
    user = relationship("User", back_populates="tax_events")
    sale_transaction = relationship("Transaction", back_populates="sale_tax_event")
