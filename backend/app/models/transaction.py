from sqlalchemy import Column, String, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy import DECIMAL
from app.database import Base
from app.utils.database_utils import uuid_column, uuid_foreign_key, jsonb_column


class Transaction(Base):
    __tablename__ = "transactions"

    id = uuid_column()
    wallet_id = uuid_foreign_key("wallets.id")
    user_id = uuid_foreign_key("users.id")
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
    raw_data = jsonb_column()
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
