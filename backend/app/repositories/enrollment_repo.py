from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
import uuid
from decimal import Decimal

from app.db.models.enrollment import Enrollment
from app.db.models.purchase import Purchase, PurchaseStatus


class EnrollmentRepository:
    """Repository for enrollment database operations."""

    def __init__(self, db: Session):
        self.db = db

    # ============================================================================
    # Enrollment Operations
    # ============================================================================

    def create_enrollment(
        self,
        user_id: uuid.UUID,
        course_id: uuid.UUID
    ) -> Enrollment:
        """
        Create a new enrollment.

        Args:
            user_id: User ID
            course_id: Course ID

        Returns:
            Created enrollment
        """
        enrollment = Enrollment(
            user_id=user_id,
            course_id=course_id,
            progress_percent=Decimal("0.00")
        )
        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment

    def get_enrollment_by_id(self, enrollment_id: uuid.UUID) -> Optional[Enrollment]:
        """Get enrollment by ID."""
        return self.db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()

    def get_enrollment(
        self,
        user_id: uuid.UUID,
        course_id: uuid.UUID
    ) -> Optional[Enrollment]:
        """
        Get enrollment for a specific user and course.

        Args:
            user_id: User ID
            course_id: Course ID

        Returns:
            Enrollment if exists, None otherwise
        """
        return (
            self.db.query(Enrollment)
            .filter(
                Enrollment.user_id == user_id,
                Enrollment.course_id == course_id
            )
            .first()
        )

    def get_user_enrollments(self, user_id: uuid.UUID) -> List[Enrollment]:
        """
        Get all enrollments for a user.

        Args:
            user_id: User ID

        Returns:
            List of enrollments
        """
        return (
            self.db.query(Enrollment)
            .options(joinedload(Enrollment.course))
            .filter(Enrollment.user_id == user_id)
            .order_by(Enrollment.enrolled_at.desc())
            .all()
        )

    def update_progress(
        self,
        enrollment: Enrollment,
        progress_percent: Decimal
    ) -> Enrollment:
        """
        Update enrollment progress.

        Args:
            enrollment: Enrollment to update
            progress_percent: New progress percentage

        Returns:
            Updated enrollment
        """
        enrollment.progress_percent = progress_percent
        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment

    # ============================================================================
    # Access Control Queries
    # ============================================================================

    def has_course_enrollment(
        self,
        user_id: uuid.UUID,
        course_id: uuid.UUID
    ) -> bool:
        """
        Check if user has an enrollment for a course.

        Args:
            user_id: User ID
            course_id: Course ID

        Returns:
            True if enrolled, False otherwise
        """
        return (
            self.db.query(Enrollment)
            .filter(
                Enrollment.user_id == user_id,
                Enrollment.course_id == course_id
            )
            .count() > 0
        )

    def has_completed_course_purchase(
        self,
        user_id: uuid.UUID,
        course_id: uuid.UUID
    ) -> bool:
        """
        Check if user has a completed purchase for a course.

        Args:
            user_id: User ID
            course_id: Course ID

        Returns:
            True if has completed purchase, False otherwise
        """
        return (
            self.db.query(Purchase)
            .filter(
                Purchase.user_id == user_id,
                Purchase.course_id == course_id,
                Purchase.status == PurchaseStatus.COMPLETED
            )
            .count() > 0
        )

    def has_completed_product_purchase(
        self,
        user_id: uuid.UUID,
        product_id: uuid.UUID
    ) -> bool:
        """
        Check if user has a completed purchase for a product.

        Args:
            user_id: User ID
            product_id: Product ID

        Returns:
            True if has completed purchase, False otherwise
        """
        return (
            self.db.query(Purchase)
            .filter(
                Purchase.user_id == user_id,
                Purchase.product_id == product_id,
                Purchase.status == PurchaseStatus.COMPLETED
            )
            .count() > 0
        )
