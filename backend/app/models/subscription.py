from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.database_utils import uuid_column, uuid_foreign_key


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = uuid_column()
    user_id = uuid_foreign_key("users.id")
    provider = Column(String(20), nullable=False)  # razorpay | lemonsqueezy
    provider_sub_id = Column(String(255))
    plan = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)  # active | cancelled | expired
    current_period_end = Column(DateTime)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="subscriptions")
