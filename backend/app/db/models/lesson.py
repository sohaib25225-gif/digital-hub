import uuid
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class LessonContentType(str, enum.Enum):
    """Lesson content type enum."""
    VIDEO = "video"
    PDF = "pdf"
    TEXT = "text"
    QUIZ = "quiz"


class Lesson(Base):
    """Course lesson model."""
    __tablename__ = "lessons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    content_type = Column(SQLEnum(LessonContentType), nullable=False)
    file_url = Column(String, nullable=True)
    order_index = Column(Integer, nullable=False)
    is_preview = Column(Boolean, default=False, nullable=False)

    # Relationships
    section = relationship("Section", back_populates="lessons")
