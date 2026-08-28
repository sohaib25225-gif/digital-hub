import uuid
from typing import Tuple
from decimal import Decimal

from app.repositories.enrollment_repo import EnrollmentRepository
from app.repositories.course_repo import CourseRepository
from app.repositories.product_repo import ProductRepository
from app.db.models.user import User


class AccessService:
    """Service for centralized access control logic."""

    def __init__(
        self,
        enrollment_repo: EnrollmentRepository,
        course_repo: CourseRepository,
        product_repo: ProductRepository
    ):
        self.enrollment_repo = enrollment_repo
        self.course_repo = course_repo
        self.product_repo = product_repo

    # ============================================================================
    # Course Access Control
    # ============================================================================

    def has_course_access(
        self,
        user: User,
        course_id: uuid.UUID
    ) -> Tuple[bool, str]:
        """
        Check if user has access to a course.

        Access rules:
        - Free course (price = 0) + enrolled → ALLOW
        - Paid course + completed purchase → ALLOW
        - Paid course + no purchase → DENY
        - Not enrolled → DENY

        Args:
            user: User object
            course_id: Course ID

        Returns:
            Tuple of (has_access: bool, reason: str)
        """
        # Get course
        course = self.course_repo.get_course_by_id(course_id)
        if not course:
            return False, "Course not found"

        # Check if published
        from app.db.models.course import CourseStatus
        if course.status != CourseStatus.PUBLISHED:
            return False, "Course not published"

        # Check enrollment
        has_enrollment = self.enrollment_repo.has_course_enrollment(user.id, course_id)

        # Free course logic
        if course.price == Decimal("0.00") or course.price == 0:
            if has_enrollment:
                return True, "Free course with enrollment"
            else:
                return False, "Not enrolled"

        # Paid course logic
        has_purchase = self.enrollment_repo.has_completed_course_purchase(user.id, course_id)

        if has_purchase:
            return True, "Paid course with completed purchase"
        else:
            return False, "Paid course requires purchase"

    # ============================================================================
    # Product Access Control
    # ============================================================================

    def has_product_access(
        self,
        user: User,
        product_id: uuid.UUID
    ) -> Tuple[bool, str]:
        """
        Check if user has access to a product.

        Access rules:
        - Must have completed purchase

        Args:
            user: User object
            product_id: Product ID

        Returns:
            Tuple of (has_access: bool, reason: str)
        """
        # Get product
        product = self.product_repo.get_product_by_id(product_id)
        if not product:
            return False, "Product not found"

        # Check if published
        from app.db.models.product import ProductStatus
        if product.status != ProductStatus.PUBLISHED:
            return False, "Product not published"

        # Check purchase
        has_purchase = self.enrollment_repo.has_completed_product_purchase(user.id, product_id)

        if has_purchase:
            return True, "Product purchased"
        else:
            return False, "Product requires purchase"

    # ============================================================================
    # Lesson Access Control
    # ============================================================================

    def has_lesson_access(
        self,
        user: User,
        course_id: uuid.UUID,
        lesson_id: uuid.UUID
    ) -> Tuple[bool, str]:
        """
        Check if user has access to a specific lesson.

        Args:
            user: User object
            course_id: Course ID
            lesson_id: Lesson ID

        Returns:
            Tuple of (has_access: bool, reason: str)
        """
        # First check course access
        has_access, reason = self.has_course_access(user, course_id)
        if not has_access:
            return False, reason

        # Verify lesson belongs to course
        from app.repositories.course_repo import CourseRepository
        lesson = self.course_repo.repository.get_lesson_by_id(lesson_id)
        if not lesson:
            return False, "Lesson not found"

        # Check lesson belongs to a section of this course
        from app.db.models.section import Section
        section = (
            self.enrollment_repo.db.query(Section)
            .filter(
                Section.id == lesson.section_id,
                Section.course_id == course_id
            )
            .first()
        )

        if not section:
            return False, "Lesson does not belong to this course"

        return True, "Authorized"

    # ============================================================================
    # Preview Lesson Access
    # ============================================================================

    def is_preview_lesson_accessible(
        self,
        course_id: uuid.UUID,
        lesson_id: uuid.UUID
    ) -> Tuple[bool, str]:
        """
        Check if a lesson is a publicly accessible preview.

        Args:
            course_id: Course ID
            lesson_id: Lesson ID

        Returns:
            Tuple of (is_accessible: bool, reason: str)
        """
        # Get course
        course = self.course_repo.get_course_by_id(course_id)
        if not course:
            return False, "Course not found"

        # Check if published
        from app.db.models.course import CourseStatus
        if course.status != CourseStatus.PUBLISHED:
            return False, "Course not published"

        # Get lesson
        from app.repositories.course_repo import CourseRepository
        lesson = self.course_repo.repository.get_lesson_by_id(lesson_id)
        if not lesson:
            return False, "Lesson not found"

        # Verify lesson belongs to course
        from app.db.models.section import Section
        section = (
            self.enrollment_repo.db.query(Section)
            .filter(
                Section.id == lesson.section_id,
                Section.course_id == course_id
            )
            .first()
        )

        if not section:
            return False, "Lesson does not belong to this course"

        # Check if preview
        if not lesson.is_preview:
            return False, "Lesson is not a preview"

        return True, "Preview accessible"
