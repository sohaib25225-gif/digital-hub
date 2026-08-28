import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Numeric, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class CourseStatus(str, enum.Enum):
    """Course status enum: draft or published."""
    DRAFT = "draft"
    PUBLISHED = "published"


class Course(Base):
    """Course model."""
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("creators.id", ondelete="RESTRICT"), nullable=False, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    price = Column(Numeric(10, 2), default=0.00, nullable=False)
    status = Column(SQLEnum(CourseStatus), default=CourseStatus.DRAFT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    creator = relationship("Creator", back_populates="courses")
    sections = relationship("Section", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    purchases = relationship("Purchase", back_populates="course")
