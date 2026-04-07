from sqlalchemy import Column, String, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import DECIMAL
from app.database import Base
import uuid


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_id = Column(
        UUID(as_uuid=True), ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    tx_hash = Column(String(255), nullable=False)
    chain = Column(String(20), nullable=False)
    tx_type = Column(
        String(30), nullable=False
    )  # trade | transfer_in | transfer_out | staking | airdrop | nft_sale | fee
    token_symbol = Column(String(50))
    token_address = Column(String(255))
    quantity = Column(DECIMAL(36, 18), nullable=False)
    price_usd = Column(DECIMAL(20, 8))
    value_usd = Column(DECIMAL(20, 8))
    fee_usd = Column(DECIMAL(20, 8))
    timestamp = Column(DateTime, nullable=False)
    raw_data = Column(JSONB)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="transactions")
    wallet = relationship("Wallet", back_populates="transactions")
    cost_basis_lot = relationship(
        "CostBasisLot", back_populates="source_transaction", uselist=False
    )
    sale_tax_event = relationship(
        "TaxEvent", back_populates="sale_transaction", uselist=False
    )

    __table_args__ = (
        UniqueConstraint("tx_hash", "chain", name="unique_tx_hash_chain"),
    )
