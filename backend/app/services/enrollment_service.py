import uuid
from typing import List
from fastapi import HTTPException, status
from decimal import Decimal

from app.repositories.enrollment_repo import EnrollmentRepository
from app.repositories.course_repo import CourseRepository
from app.schemas.enrollment import EnrollmentProgressUpdate
from app.db.models.enrollment import Enrollment
from app.db.models.user import User
from app.db.models.course import CourseStatus


class EnrollmentService:
    """Service layer for enrollment business logic."""

    def __init__(
        self,
        enrollment_repo: EnrollmentRepository,
        course_repo: CourseRepository
    ):
        self.enrollment_repo = enrollment_repo
        self.course_repo = course_repo

    # ============================================================================
    # Enrollment Operations
    # ============================================================================

    def enroll_in_course(
        self,
        user: User,
        course_id: uuid.UUID
    ) -> Enrollment:
        """
        Enroll user in a course.

        Rules:
        - Course must exist and be published
        - User must not already be enrolled
        - Free courses (price = 0) can be enrolled in immediately
        - Paid courses require a completed purchase

        Args:
            user: User object
            course_id: Course ID

        Returns:
            Created enrollment

        Raises:
            HTTPException: If enrollment not allowed
        """
        # Get course
        course = self.course_repo.get_course_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        # Check if published
        if course.status != CourseStatus.PUBLISHED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot enroll in unpublished course"
            )

        # Check for duplicate enrollment
        existing = self.enrollment_repo.get_enrollment(user.id, course_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already enrolled in this course"
            )

        # Check if free course
        if course.price == Decimal("0.00") or course.price == 0:
            # Free course - create enrollment
            enrollment = self.enrollment_repo.create_enrollment(user.id, course_id)
            return enrollment
        else:
            # Paid course - check for completed purchase
            has_purchase = self.enrollment_repo.has_completed_course_purchase(
                user.id,
                course_id
            )

            if not has_purchase:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="This course requires purchase before enrollment"
                )

            # Has purchase - create enrollment
            enrollment = self.enrollment_repo.create_enrollment(user.id, course_id)
            return enrollment

    def get_user_enrollments(self, user: User) -> List[Enrollment]:
        """
        Get all enrollments for a user.

        Args:
            user: User object

        Returns:
            List of enrollments
        """
        return self.enrollment_repo.get_user_enrollments(user.id)

    def get_enrollment(
        self,
        user: User,
        course_id: uuid.UUID
    ) -> Enrollment:
        """
        Get a specific enrollment for a user.

        Args:
            user: User object
            course_id: Course ID

        Returns:
            Enrollment

        Raises:
            HTTPException: If enrollment not found or doesn't belong to user
        """
        enrollment = self.enrollment_repo.get_enrollment(user.id, course_id)

        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found"
            )

        # Verify ownership (already filtered by user_id in query, but double-check)
        if enrollment.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this enrollment"
            )

        return enrollment

    def update_progress(
        self,
        user: User,
        course_id: uuid.UUID,
        progress_data: EnrollmentProgressUpdate
    ) -> Enrollment:
        """
        Update enrollment progress.

        Args:
            user: User object
            course_id: Course ID
            progress_data: Progress update data

        Returns:
            Updated enrollment

        Raises:
            HTTPException: If enrollment not found or user not authorized
        """
        # Get enrollment
        enrollment = self.get_enrollment(user, course_id)

        # Update progress
        updated_enrollment = self.enrollment_repo.update_progress(
            enrollment,
            progress_data.progress_percent
        )

        return updated_enrollment
