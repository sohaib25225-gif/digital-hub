from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import uuid

from app.db.models.course import CourseStatus
from app.db.models.lesson import LessonContentType


# ============================================================================
# Course Schemas
# ============================================================================

class CourseCreate(BaseModel):
    """Schema for creating a course."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    price: Decimal = Field(default=Decimal("0.00"), ge=0)
    status: CourseStatus = CourseStatus.DRAFT


class CourseUpdate(BaseModel):
    """Schema for updating a course."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    status: Optional[CourseStatus] = None


class CourseBase(BaseModel):
    """Base course schema with common fields."""
    id: uuid.UUID
    creator_id: uuid.UUID
    title: str
    slug: str
    description: Optional[str]
    thumbnail_url: Optional[str]
    price: Decimal
    status: CourseStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseResponse(CourseBase):
    """Schema for course detail response."""
    pass


class CourseListItem(BaseModel):
    """Schema for course in list response."""
    id: uuid.UUID
    title: str
    slug: str
    description: Optional[str]
    thumbnail_url: Optional[str]
    price: Decimal
    status: CourseStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseListResponse(BaseModel):
    """Schema for paginated course list response."""
    courses: List[CourseListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# Section Schemas
# ============================================================================

class SectionCreate(BaseModel):
    """Schema for creating a section."""
    title: str = Field(..., min_length=1, max_length=255)
    order_index: int = Field(..., ge=0)


class SectionUpdate(BaseModel):
    """Schema for updating a section."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    order_index: Optional[int] = Field(None, ge=0)


class SectionResponse(BaseModel):
    """Schema for section response."""
    id: uuid.UUID
    course_id: uuid.UUID
    title: str
    order_index: int

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Lesson Schemas
# ============================================================================

class LessonCreate(BaseModel):
    """Schema for creating a lesson."""
    title: str = Field(..., min_length=1, max_length=255)
    content_type: LessonContentType
    file_url: Optional[str] = None
    order_index: int = Field(..., ge=0)
    is_preview: bool = False


class LessonUpdate(BaseModel):
    """Schema for updating a lesson."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content_type: Optional[LessonContentType] = None
    file_url: Optional[str] = None
    order_index: Optional[int] = Field(None, ge=0)
    is_preview: Optional[bool] = None


class LessonResponse(BaseModel):
    """Schema for lesson response."""
    id: uuid.UUID
    section_id: uuid.UUID
    title: str
    content_type: LessonContentType
    file_url: Optional[str]
    order_index: int
    is_preview: bool

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Detailed Course with Sections and Lessons
# ============================================================================

class LessonInSection(BaseModel):
    """Lesson nested in section."""
    id: uuid.UUID
    title: str
    content_type: LessonContentType
    file_url: Optional[str]
    order_index: int
    is_preview: bool

    model_config = ConfigDict(from_attributes=True)


class SectionWithLessons(BaseModel):
    """Section with nested lessons."""
    id: uuid.UUID
    title: str
    order_index: int
    lessons: List[LessonInSection]

    model_config = ConfigDict(from_attributes=True)


class CourseDetailResponse(CourseBase):
    """Detailed course response including sections and lessons."""
    sections: List[SectionWithLessons]

    model_config = ConfigDict(from_attributes=True)
