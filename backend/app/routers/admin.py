from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
import uuid

from app.core.dependencies import get_current_admin
from app.db.session import get_db
from app.db.models.user import User
from app.repositories.course_repo import CourseRepository
from app.services.course_service import CourseService
from app.repositories.product_repo import ProductRepository
from app.services.product_service import ProductService
from app.schemas.course import (
    CourseCreate,
    CourseUpdate,
    CourseResponse,
    CourseListResponse,
    CourseDetailResponse,
    SectionCreate,
    SectionUpdate,
    SectionResponse,
    LessonCreate,
    LessonUpdate,
    LessonResponse,
)
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)

router = APIRouter()


def get_course_service(db: Annotated[Session, Depends(get_db)]) -> CourseService:
    """Dependency to get course service instance."""
    repository = CourseRepository(db)
    return CourseService(repository)


def get_product_service(db: Annotated[Session, Depends(get_db)]) -> ProductService:
    """Dependency to get product service instance."""
    repository = ProductRepository(db)
    return ProductService(repository)


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
def admin_health(
    current_admin: Annotated[User, Depends(get_current_admin)]
):
    """
    Health check endpoint for admin router.
    Requires admin authentication.
    """
    return {
        "status": "ok",
        "router": "admin",
        "admin_user": current_admin.email
    }


# ============================================================================
# Course Endpoints
# ============================================================================

@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course_data: CourseCreate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    service: CourseService = Depends(get_course_service)
):
    """
    Create a new course (admin only).

    Generates a unique slug from the title.
    Sets the creator to the current admin user's creator profile.

    Args:
        course_data: Course creation data
        current_admin: Authenticated admin user
        service: Course service instance

    Returns:
        The created course

    Raises:
        403: If user doesn't have a creator profile
    """
    return service.create_course(course_data, current_admin)


@router.get("/courses", response_model=CourseListResponse)
def list_all_courses(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_admin: Annotated[User, Depends(get_current_admin)] = None,
    service: CourseService = Depends(get_course_service)
):
    """
    List all courses including drafts (admin only).

    Returns both published and draft courses.

    Args:
        page: Page number (default: 1)
        page_size: Items per page (default: 20, max: 100)
        current_admin: Authenticated admin user
        service: Course service instance

    Returns:
        Paginated list of all courses
    """
    return service.get_all_courses(page=page, page_size=page_size)


@router.get("/courses/{course_id}", response_model=CourseDetailResponse)
def get_course_detail(
    course_id: uuid.UUID,
    current_admin: Annotated[User, Depends(get_current_admin)],
    service: CourseService = Depends(get_course_service)
):
    """
    Get course details by ID (admin only).

    Returns course with all sections and lessons, regardless of status.

    Args:
        course_id: Course UUID
        current_admin: Authenticated admin user
        service: Course service instance

    Returns:
        Course details with sections and lessons

    Raises:
        404: If course not found
    """
    return service.get_course_with_details(course_id)


@router.put("/courses/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: uuid.UUID,
    course_data: CourseUpdate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    service: CourseService = Depends(get_course_service)
):
    """
    Update a course (admin only).

    Can update any field including slug and status.
    Use this to publish/unpublish courses by changing status.

    Args:
        course_id: Course UUID
        course_data: Course update data
        current_admin: Authenticated admin user
        service: Course service instance

    Returns:
        The updated course

    Raises:
        404: If course not found
        400: If slug already exists
    """
    return service.update_course(course_id, course_data)


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: uuid.UUID,
    current_admin: Annotated[User, Depends(get_current_admin)],
    service: CourseService = Depends(get_course_service)
):
    """
    Delete a course (admin only).

    Cascades to delete all sections and lessons.

    Args:
        course_id: Course UUID
        current_admin: Authenticated admin user
        service: Course service instance

    Raises:
        404: If course not found
    """
    service.delete_course(course_id)
    return None


# ============================================================================
# Section Endpoints
# ============================================================================

@router.post("/courses/{course_id}/sections", response_model=SectionResponse, status_code=status.HTTP_201_CREATED)
def create_section(
    course_id: uuid.UUID,
    section_data: SectionCreate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    service: CourseService = Depends(get_course_service)
):
    """
    Create a new section in a course (admin only).

    Args:
        course_id: Course UUID
        section_data: Section creation data
        current_admin: Authenticated admin user
        service: Course service instance

    Returns:
        The created section

    Raises:
        404: If course not found
    """
    return service.create_section(course_id, section_data)


@router.put("/sections/{section_id}", response_model=SectionResponse)
def update_section(
    section_id: uuid.UUID,
    section_data: SectionUpdate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    service: CourseService = Depends(get_course_service)
):
    """
    Update a section (admin only).

    Args:
        section_id: Section UUID
        section_data: Section update data
        current_admin: Authenticated admin user
        service: Course service instance

    Returns:
        The updated section

    Raises:
        404: If section not found
    """
    return service.update_section(section_id, section_data)


@router.delete("/sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_section(
    section_id: uuid.UUID,
    current_admin: Annotated[User, Depends(get_current_admin)],
    service: CourseService = Depends(get_course_service)
):
    """
    Delete a section (admin only).

    Cascades to delete all lessons in the section.

    Args:
        section_id: Section UUID
        current_admin: Authenticated admin user
        service: Course service instance

    Raises:
        404: If section not found
    """
    service.delete_section(section_id)
    return None


# ============================================================================
# Lesson Endpoints
# ============================================================================

@router.post("/sections/{section_id}/lessons", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def create_lesson(
    section_id: uuid.UUID,
    lesson_data: LessonCreate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    service: CourseService = Depends(get_course_service)
):
    """
    Create a new lesson in a section (admin only).

    Args:
        section_id: Section UUID
        lesson_data: Lesson creation data
        current_admin: Authenticated admin user
        service: Course service instance

    Returns:
        The created lesson

    Raises:
        404: If section not found
    """
    return service.create_lesson(section_id, lesson_data)


@router.put("/lessons/{lesson_id}", response_model=LessonResponse)
def update_lesson(
    lesson_id: uuid.UUID,
    lesson_data: LessonUpdate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    service: CourseService = Depends(get_course_service)
):
    """
    Update a lesson (admin only).

    Args:
        lesson_id: Lesson UUID
        lesson_data: Lesson update data
        current_admin: Authenticated admin user
        service: Course service instance

    Returns:
        The updated lesson

    Raises:
        404: If lesson not found
    """
    return service.update_lesson(lesson_id, lesson_data)


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(
    lesson_id: uuid.UUID,
    current_admin: Annotated[User, Depends(get_current_admin)],
    service: CourseService = Depends(get_course_service)
):
    """
    Delete a lesson (admin only).

    Args:
        lesson_id: Lesson UUID
        current_admin: Authenticated admin user
        service: Course service instance

    Raises:
        404: If lesson not found
    """
    service.delete_lesson(lesson_id)
    return None


# ============================================================================
# Product Endpoints
# ============================================================================

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    service: ProductService = Depends(get_product_service)
):
    """
    Create a new product (admin only).

    Generates a unique slug from the title.
    Sets the creator to the current admin user's creator profile.

    Args:
        product_data: Product creation data
        current_admin: Authenticated admin user
        service: Product service instance

    Returns:
        The created product

    Raises:
        403: If user doesn't have a creator profile
    """
    return service.create_product(product_data, current_admin)


@router.get("/products", response_model=ProductListResponse)
def list_all_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_admin: Annotated[User, Depends(get_current_admin)] = None,
    service: ProductService = Depends(get_product_service)
):
    """
    List all products including drafts (admin only).

    Returns both published and draft products.

    Args:
        page: Page number (default: 1)
        page_size: Items per page (default: 20, max: 100)
        current_admin: Authenticated admin user
        service: Product service instance

    Returns:
        Paginated list of all products
    """
    return service.get_all_products(page=page, page_size=page_size)


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product_detail(
    product_id: uuid.UUID,
    current_admin: Annotated[User, Depends(get_current_admin)],
    service: ProductService = Depends(get_product_service)
):
    """
    Get product details by ID (admin only).

    Returns product regardless of status.

    Args:
        product_id: Product UUID
        current_admin: Authenticated admin user
        service: Product service instance

    Returns:
        Product details

    Raises:
        404: If product not found
    """
    return service.get_product_by_id(product_id)


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: uuid.UUID,
    product_data: ProductUpdate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    service: ProductService = Depends(get_product_service)
):
    """
    Update a product (admin only).

    Can update any field including slug and status.
    Use this to publish/unpublish products by changing status.

    Args:
        product_id: Product UUID
        product_data: Product update data
        current_admin: Authenticated admin user
        service: Product service instance

    Returns:
        The updated product

    Raises:
        404: If product not found
        400: If slug already exists
    """
    return service.update_product(product_id, product_data)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: uuid.UUID,
    current_admin: Annotated[User, Depends(get_current_admin)],
    service: ProductService = Depends(get_product_service)
):
    """
    Delete a product (admin only).

    Args:
        product_id: Product UUID
        current_admin: Authenticated admin user
        service: Product service instance

    Raises:
        404: If product not found
    """
    service.delete_product(product_id)
    return None
