from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal
import uuid


# ============================================================================
# Enrollment Schemas
# ============================================================================

class EnrollmentCreate(BaseModel):
    """Schema for enrolling in a course."""
    # No additional fields needed - course_id comes from URL
    pass


class EnrollmentProgressUpdate(BaseModel):
    """Schema for updating enrollment progress."""
    progress_percent: Decimal = Field(..., ge=0, le=100, description="Progress percentage (0-100)")


class EnrollmentResponse(BaseModel):
    """Schema for enrollment response."""
    id: uuid.UUID
    user_id: uuid.UUID
    course_id: uuid.UUID
    enrolled_at: datetime
    progress_percent: Decimal

    model_config = ConfigDict(from_attributes=True)


class EnrollmentWithCourse(BaseModel):
    """Schema for enrollment with course details."""
    id: uuid.UUID
    user_id: uuid.UUID
    course_id: uuid.UUID
    enrolled_at: datetime
    progress_percent: Decimal
    course_title: str
    course_slug: str
    course_thumbnail_url: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Protected Access Schemas
# ============================================================================

class SignedUrlResponse(BaseModel):
    """Schema for signed URL response."""
    url: str
    expires_in: int = 3600  # seconds


class CourseAccessResponse(BaseModel):
    """Schema for course access response."""
    access_granted: bool
    reason: Optional[str] = None


class ProductAccessResponse(BaseModel):
    """Schema for product access response."""
    access_granted: bool
    reason: Optional[str] = None
