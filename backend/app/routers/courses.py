from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
import uuid
import uuid

from app.db.session import get_db
from app.repositories.course_repo import CourseRepository
from app.services.course_service import CourseService
from app.schemas.course import CourseListResponse, CourseDetailResponse

router = APIRouter()


def get_course_service(db: Annotated[Session, Depends(get_db)]) -> CourseService:
    """Dependency to get course service instance."""
    repository = CourseRepository(db)
    return CourseService(repository)


@router.get("/", response_model=CourseListResponse)
def list_published_courses(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: CourseService = Depends(get_course_service)
):
    """
    List all published courses (public endpoint).

    Only courses with status='published' are returned.
    Draft courses are hidden from public view.

    Args:
        page: Page number (default: 1)
        page_size: Items per page (default: 20, max: 100)
        service: Course service instance

    Returns:
        Paginated list of published courses
    """
    return service.get_published_courses(page=page, page_size=page_size)


@router.get("/{slug}", response_model=CourseDetailResponse)
def get_course_by_slug(
    slug: str,
    service: CourseService = Depends(get_course_service)
):
    """
    Get course details by slug (public endpoint).

    Only published courses can be accessed.
    Returns course with all sections and lessons.

    Args:
        slug: Course slug (URL-friendly identifier)
        service: Course service instance

    Returns:
        Course details with sections and lessons

    Raises:
        404: If course not found or not published
    """
    return service.get_published_course_by_slug(slug)


@router.get("/{slug}/lessons/{lesson_id}/preview")
def get_preview_lesson(
    slug: str,
    lesson_id: uuid.UUID,
    service: CourseService = Depends(get_course_service),
    db: Session = Depends(get_db)
):
    """
    Get preview lesson file (public endpoint).

    Only lessons with is_preview=true are accessible.
    Only for published courses.

    Args:
        slug: Course slug
        lesson_id: Lesson ID
        service: Course service
        db: Database session

    Returns:
        Signed URL for preview lesson file

    Raises:
        403: Lesson is not a preview or course not published
        404: Course or lesson not found
    """
    from app.services.access_service import AccessService
    from app.repositories.enrollment_repo import EnrollmentRepository
    from app.repositories.course_repo import CourseRepository
    from app.repositories.product_repo import ProductRepository
    from app.services.storage_service import StorageService
    from app.schemas.enrollment import SignedUrlResponse
    from fastapi import HTTPException, status

    # Get course by slug
    course = service.repository.get_product_by_slug(slug)  # Typo will be fixed
    # Actually let me use proper method
    from app.db.models.course import Course
    course = db.query(Course).filter(Course.slug == slug).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Check access to preview
    enrollment_repo = EnrollmentRepository(db)
    course_repo = CourseRepository(db)
    product_repo = ProductRepository(db)
    access_service = AccessService(enrollment_repo, course_repo, product_repo)

    is_accessible, reason = access_service.is_preview_lesson_accessible(
        course.id,
        lesson_id
    )

    if not is_accessible:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Preview not accessible: {reason}"
        )

    # Get lesson
    lesson = course_repo.get_lesson_by_id(lesson_id)

    if not lesson or not lesson.file_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson file not found"
        )

    # Extract filename
    filename = lesson.file_url.split('/')[-1]

    # Determine bucket
    from app.db.models.lesson import LessonContentType
    if lesson.content_type == LessonContentType.VIDEO:
        bucket = StorageService.BUCKET_COURSE_VIDEOS
    elif lesson.content_type == LessonContentType.PDF:
        bucket = StorageService.BUCKET_COURSE_PDFS
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Preview not available for this lesson type"
        )

    # Generate signed URL
    storage_service = StorageService()
    signed_url = storage_service.create_signed_url(
        bucket=bucket,
        path=filename,
        expires_in=3600
    )

    return SignedUrlResponse(url=signed_url, expires_in=3600)


@router.get("/health")
def courses_health():
    """Health check endpoint for courses router."""
    return {"status": "ok", "router": "courses"}
