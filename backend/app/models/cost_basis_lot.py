from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import DECIMAL
from app.database import Base
from app.utils.database_utils import uuid_column, uuid_foreign_key


class CostBasisLot(Base):
    __tablename__ = "cost_basis_lots"

    id = uuid_column()
    user_id = uuid_foreign_key("users.id")
    token_symbol = Column(String(50), nullable=False)
    chain = Column(String(20), nullable=False)
    quantity_remaining = Column(DECIMAL(36, 18), nullable=False)
    cost_per_unit_usd = Column(DECIMAL(20, 8), nullable=False)
    acquired_at = Column(DateTime, nullable=False)
    source_tx_id = uuid_foreign_key("transactions.id")

    # Relationships
    user = relationship("User", back_populates="cost_basis_lots")
    source_transaction = relationship("Transaction", back_populates="cost_basis_lot")
