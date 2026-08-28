import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Numeric, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class ProductStatus(str, enum.Enum):
    """Product status enum: draft or published."""
    DRAFT = "draft"
    PUBLISHED = "published"


class Product(Base):
    """Digital product model."""
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("creators.id", ondelete="RESTRICT"), nullable=False, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    file_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    status = Column(SQLEnum(ProductStatus), default=ProductStatus.DRAFT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    creator = relationship("Creator", back_populates="products")
    purchases = relationship("Purchase", back_populates="product")
