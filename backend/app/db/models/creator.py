import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Creator(Base):
    """Creator model - one-to-one with User, allows future multi-creator."""
    __tablename__ = "creators"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, unique=True, index=True)
    display_name = Column(String, nullable=False)
    bio = Column(Text, nullable=True)
    revenue_share_percent = Column(Numeric(5, 2), default=100.00, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="creator")
    courses = relationship("Course", back_populates="creator")
    products = relationship("Product", back_populates="creator")
