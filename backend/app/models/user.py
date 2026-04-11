from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.database_utils import uuid_column


class User(Base):
    __tablename__ = "users"

    id = uuid_column()
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    plan = Column(String(20), default="free")
    country = Column(String(10), default="IN")
    financial_year_start = Column(String(5), default="04-01")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    wallets = relationship(
        "Wallet", back_populates="user", cascade="all, delete-orphan"
    )
    transactions = relationship("Transaction", back_populates="user")
    cost_basis_lots = relationship("CostBasisLot", back_populates="user")
    tax_events = relationship("TaxEvent", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
