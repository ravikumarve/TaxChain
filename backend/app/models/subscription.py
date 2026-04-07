from sqlalchemy import Column, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    provider = Column(String(20), nullable=False)  # razorpay | lemonsqueezy
    provider_sub_id = Column(String(255))
    plan = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)  # active | cancelled | expired
    current_period_end = Column(DateTime)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="subscriptions")
