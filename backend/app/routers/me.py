from typing import Annotated, List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.db.models.user import User
from app.repositories.enrollment_repo import EnrollmentRepository
from app.repositories.course_repo import CourseRepository
from app.repositories.product_repo import ProductRepository
from app.repositories.purchase_repo import PurchaseRepository
from app.services.enrollment_service import EnrollmentService
from app.services.access_service import AccessService
from app.services.storage_service import StorageService
from app.services.purchase_service import PurchaseService
from app.schemas.enrollment import (
    EnrollmentCreate,
    EnrollmentResponse,
    EnrollmentProgressUpdate,
    SignedUrlResponse,
)
from app.schemas.course import CourseDetailResponse
from app.schemas.purchase import (
    PurchaseCreate,
    PurchaseResponse,
    PurchaseWithDetails,
)

router = APIRouter()


def get_enrollment_service(db: Annotated[Session, Depends(get_db)]) -> EnrollmentService:
    """Dependency to get enrollment service instance."""
    enrollment_repo = EnrollmentRepository(db)
    course_repo = CourseRepository(db)
    return EnrollmentService(enrollment_repo, course_repo)


def get_access_service(db: Annotated[Session, Depends(get_db)]) -> AccessService:
    """Dependency to get access service instance."""
    enrollment_repo = EnrollmentRepository(db)
    course_repo = CourseRepository(db)
    product_repo = ProductRepository(db)
    return AccessService(enrollment_repo, course_repo, product_repo)


def get_purchase_service(db: Annotated[Session, Depends(get_db)]) -> PurchaseService:
    """Dependency to get purchase service instance."""
    purchase_repo = PurchaseRepository(db)
    course_repo = CourseRepository(db)
    product_repo = ProductRepository(db)
    enrollment_repo = EnrollmentRepository(db)
    return PurchaseService(purchase_repo, course_repo, product_repo, enrollment_repo)


# ============================================================================
# Enrollment Endpoints
# ============================================================================

@router.post("/enrollments/{course_id}", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def enroll_in_course(
    course_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: EnrollmentService = Depends(get_enrollment_service)
):
    """
    Enroll in a course.

    Rules:
    - Free courses (price = 0) can be enrolled in immediately
    - Paid courses require a completed purchase
    - Cannot enroll in draft courses
    - Cannot enroll twice in the same course

    Args:
        course_id: Course ID to enroll in
        current_user: Authenticated user
        service: Enrollment service

    Returns:
        Created enrollment

    Raises:
        404: Course not found
        400: Already enrolled
        402: Paid course requires purchase
        403: Cannot enroll in draft course
    """
    return service.enroll_in_course(current_user, course_id)


@router.get("/enrollments", response_model=List[EnrollmentResponse])
def list_my_enrollments(
    current_user: Annotated[User, Depends(get_current_user)],
    service: EnrollmentService = Depends(get_enrollment_service)
):
    """
    List all enrollments for the current user.

    Args:
        current_user: Authenticated user
        service: Enrollment service

    Returns:
        List of user's enrollments
    """
    return service.get_user_enrollments(current_user)


@router.get("/enrollments/{course_id}", response_model=EnrollmentResponse)
def get_my_enrollment(
    course_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: EnrollmentService = Depends(get_enrollment_service)
):
    """
    Get enrollment details for a specific course.

    Args:
        course_id: Course ID
        current_user: Authenticated user
        service: Enrollment service

    Returns:
        Enrollment details

    Raises:
        404: Enrollment not found
        403: Not authorized
    """
    return service.get_enrollment(current_user, course_id)


@router.put("/enrollments/{course_id}/progress", response_model=EnrollmentResponse)
def update_enrollment_progress(
    course_id: uuid.UUID,
    progress_data: EnrollmentProgressUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: EnrollmentService = Depends(get_enrollment_service)
):
    """
    Update progress for a course enrollment.

    Progress must be between 0 and 100.

    Args:
        course_id: Course ID
        progress_data: Progress update data
        current_user: Authenticated user
        service: Enrollment service

    Returns:
        Updated enrollment

    Raises:
        404: Enrollment not found
        403: Not authorized
        422: Invalid progress value
    """
    return service.update_progress(current_user, course_id, progress_data)


# ============================================================================
# Protected Course Access
# ============================================================================

@router.get("/courses/{course_id}", response_model=CourseDetailResponse)
def get_my_course(
    course_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    access_service: AccessService = Depends(get_access_service),
    db: Session = Depends(get_db)
):
    """
    Get course content with access control.

    Access rules:
    - Free course + enrolled → ALLOW
    - Paid course + completed purchase → ALLOW
    - Otherwise → DENY

    Args:
        course_id: Course ID
        current_user: Authenticated user
        access_service: Access service
        db: Database session

    Returns:
        Course details with sections and lessons

    Raises:
        403: Access denied
        404: Course not found
    """
    # Check access
    has_access, reason = access_service.has_course_access(current_user, course_id)

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: {reason}"
        )

    # Get course with details
    course_repo = CourseRepository(db)
    course = course_repo.get_course_with_sections_and_lessons(course_id)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Sort sections and lessons
    course.sections.sort(key=lambda s: s.order_index)
    for section in course.sections:
        section.lessons.sort(key=lambda l: l.order_index)

    return course


@router.get("/courses/{course_id}/lessons/{lesson_id}/file", response_model=SignedUrlResponse)
def get_lesson_file(
    course_id: uuid.UUID,
    lesson_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    access_service: AccessService = Depends(get_access_service),
    db: Session = Depends(get_db)
):
    """
    Get signed URL for lesson file.

    Verifies user has access to the course before generating URL.

    Args:
        course_id: Course ID
        lesson_id: Lesson ID
        current_user: Authenticated user
        access_service: Access service
        db: Database session

    Returns:
        Signed URL for lesson file

    Raises:
        403: Access denied
        404: Lesson not found
    """
    # Check access
    has_access, reason = access_service.has_lesson_access(
        current_user,
        course_id,
        lesson_id
    )

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: {reason}"
        )

    # Get lesson to extract file info
    from app.repositories.course_repo import CourseRepository

    course_repo = CourseRepository(db)
    lesson = course_repo.get_lesson_by_id(lesson_id)

    if not lesson or not lesson.file_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson file not found"
        )

    # Extract filename from URL (simplified - assumes Supabase URL structure)
    # In production, parse the URL properly
    filename = lesson.file_url.split('/')[-1]

    # Determine bucket based on content type
    from app.db.models.lesson import LessonContentType
    if lesson.content_type == LessonContentType.VIDEO:
        bucket = StorageService.BUCKET_COURSE_VIDEOS
    elif lesson.content_type == LessonContentType.PDF:
        bucket = StorageService.BUCKET_COURSE_PDFS
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lesson content type does not support file download"
        )

    # Generate signed URL
    storage_service = StorageService()
    signed_url = storage_service.create_signed_url(
        bucket=bucket,
        path=filename,
        expires_in=3600  # 1 hour
    )

    return SignedUrlResponse(url=signed_url, expires_in=3600)


# ============================================================================
# Protected Product Access
# ============================================================================

@router.get("/products/{product_id}/download", response_model=SignedUrlResponse)
def download_product(
    product_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    access_service: AccessService = Depends(get_access_service),
    db: Session = Depends(get_db)
):
    """
    Get signed URL for product download.

    Requires completed purchase.

    Args:
        product_id: Product ID
        current_user: Authenticated user
        access_service: Access service
        db: Database session

    Returns:
        Signed URL for product file

    Raises:
        403: Access denied (no purchase)
        404: Product not found
    """
    # Check access
    has_access, reason = access_service.has_product_access(current_user, product_id)

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: {reason}"
        )

    # Get product to extract file info
    from app.repositories.product_repo import ProductRepository

    product_repo = ProductRepository(db)
    product = product_repo.get_product_by_id(product_id)

    if not product or not product.file_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product file not found"
        )

    # Extract filename from URL
    filename = product.file_url.split('/')[-1]

    # Generate signed URL
    storage_service = StorageService()
    signed_url = storage_service.create_signed_url(
        bucket=StorageService.BUCKET_PRODUCT_FILES,
        path=filename,
        expires_in=3600  # 1 hour
    )

    return SignedUrlResponse(url=signed_url, expires_in=3600)


# ============================================================================
# Purchase Endpoints
# ============================================================================

@router.post("/purchases", response_model=PurchaseResponse, status_code=status.HTTP_201_CREATED)
def create_purchase(
    purchase_data: PurchaseCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: PurchaseService = Depends(get_purchase_service)
):
    """
    Create a new purchase for a course or product.

    Creates a purchase in PENDING status. Admin must mark it as COMPLETED later.

    Rules:
    - Item must exist and be published
    - Item must be paid (free courses use enrollment endpoint)
    - No duplicate pending/completed purchases
    - Amount must match item price

    Args:
        purchase_data: Purchase creation data
        current_user: Authenticated user
        service: Purchase service

    Returns:
        Created purchase (status=PENDING)

    Raises:
        400: Invalid purchase (draft, free, duplicate, price mismatch)
        404: Item not found
    """
    return service.create_purchase(current_user, purchase_data)


@router.get("/purchases", response_model=List[PurchaseWithDetails])
def list_my_purchases(
    current_user: Annotated[User, Depends(get_current_user)],
    service: PurchaseService = Depends(get_purchase_service)
):
    """
    List all purchases for the current user.

    Includes item details (title, type).

    Args:
        current_user: Authenticated user
        service: Purchase service

    Returns:
        List of user's purchases with item details
    """
    purchases_data = service.get_user_purchases(current_user)

    # Convert to response format
    results = []
    for data in purchases_data:
        purchase = data["purchase"]
        results.append(
            PurchaseWithDetails(
                id=purchase.id,
                user_id=purchase.user_id,
                course_id=purchase.course_id,
                product_id=purchase.product_id,
                amount=purchase.amount,
                currency=purchase.currency,
                status=purchase.status.value,
                created_at=purchase.created_at,
                item_title=data["item_title"],
                item_type=data["item_type"]
            )
        )

    return results


@router.get("/purchases/{purchase_id}", response_model=PurchaseWithDetails)
def get_my_purchase(
    purchase_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: PurchaseService = Depends(get_purchase_service)
):
    """
    Get details of a specific purchase.

    User can only view their own purchases.

    Args:
        purchase_id: Purchase ID
        current_user: Authenticated user
        service: Purchase service

    Returns:
        Purchase details with item information

    Raises:
        404: Purchase not found
        403: Not authorized to access this purchase
    """
    purchase_data = service.get_purchase(current_user, purchase_id)
    purchase = purchase_data["purchase"]

    return PurchaseWithDetails(
        id=purchase.id,
        user_id=purchase.user_id,
        course_id=purchase.course_id,
        product_id=purchase.product_id,
        amount=purchase.amount,
        currency=purchase.currency,
        status=purchase.status.value,
        created_at=purchase.created_at,
        item_title=purchase_data["item_title"],
        item_type=purchase_data["item_type"]
    )
