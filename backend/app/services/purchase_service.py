import uuid
from typing import List
from fastapi import HTTPException, status
from decimal import Decimal

from app.repositories.purchase_repo import PurchaseRepository
from app.repositories.course_repo import CourseRepository
from app.repositories.product_repo import ProductRepository
from app.repositories.enrollment_repo import EnrollmentRepository
from app.schemas.purchase import PurchaseCreate
from app.db.models.purchase import Purchase, PurchaseStatus
from app.db.models.user import User
from app.db.models.course import CourseStatus
from app.db.models.product import ProductStatus


class PurchaseService:
    """Service layer for purchase business logic."""

    def __init__(
        self,
        purchase_repo: PurchaseRepository,
        course_repo: CourseRepository,
        product_repo: ProductRepository,
        enrollment_repo: EnrollmentRepository
    ):
        self.purchase_repo = purchase_repo
        self.course_repo = course_repo
        self.product_repo = product_repo
        self.enrollment_repo = enrollment_repo

    # ============================================================================
    # Purchase Creation
    # ============================================================================

    def create_purchase(
        self,
        user: User,
        purchase_data: PurchaseCreate
    ) -> Purchase:
        """
        Create a new purchase.

        Validates:
        - Item exists and is published
        - Item is not free
        - No duplicate pending/completed purchase
        - Amount matches item price

        Args:
            user: User object
            purchase_data: Purchase creation data

        Returns:
            Created purchase

        Raises:
            HTTPException: If validation fails
        """
        # Validate course purchase
        if purchase_data.course_id:
            return self._create_course_purchase(user, purchase_data)

        # Validate product purchase
        if purchase_data.product_id:
            return self._create_product_purchase(user, purchase_data)

        # Should not reach here due to Pydantic validation
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must specify either course_id or product_id"
        )

    def _create_course_purchase(
        self,
        user: User,
        purchase_data: PurchaseCreate
    ) -> Purchase:
        """Create a course purchase with validation."""
        course_id = purchase_data.course_id

        # Get course
        course = self.course_repo.get_course_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        # Must be published
        if course.status != CourseStatus.PUBLISHED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot purchase draft course"
            )

        # Must be paid
        if course.price == Decimal("0.00") or course.price == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This course is free. Use enrollment endpoint instead."
            )

        # Check for duplicate pending purchase
        if self.purchase_repo.has_pending_purchase(user.id, course_id, None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have a pending purchase for this course"
            )

        # Check for duplicate completed purchase
        if self.purchase_repo.has_completed_purchase(user.id, course_id, None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already purchased this course"
            )

        # Verify amount matches course price
        if purchase_data.amount != course.price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Amount must match course price ({course.price} {purchase_data.currency})"
            )

        # Create purchase
        purchase = self.purchase_repo.create_purchase(
            user_id=user.id,
            course_id=course_id,
            product_id=None,
            amount=purchase_data.amount,
            currency=purchase_data.currency
        )

        return purchase

    def _create_product_purchase(
        self,
        user: User,
        purchase_data: PurchaseCreate
    ) -> Purchase:
        """Create a product purchase with validation."""
        product_id = purchase_data.product_id

        # Get product
        product = self.product_repo.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # Must be published
        if product.status != ProductStatus.PUBLISHED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot purchase draft product"
            )

        # Products must be paid (no free products in our model)
        if product.price == Decimal("0.00") or product.price == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid product price"
            )

        # Check for duplicate pending purchase
        if self.purchase_repo.has_pending_purchase(user.id, None, product_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have a pending purchase for this product"
            )

        # Check for duplicate completed purchase
        if self.purchase_repo.has_completed_purchase(user.id, None, product_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already purchased this product"
            )

        # Verify amount matches product price
        if purchase_data.amount != product.price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Amount must match product price ({product.price} {purchase_data.currency})"
            )

        # Create purchase
        purchase = self.purchase_repo.create_purchase(
            user_id=user.id,
            course_id=None,
            product_id=product_id,
            amount=purchase_data.amount,
            currency=purchase_data.currency
        )

        return purchase

    # ============================================================================
    # Purchase Retrieval
    # ============================================================================

    def get_user_purchases(self, user: User) -> List[dict]:
        """
        Get all purchases for a user with item details.

        Args:
            user: User object

        Returns:
            List of purchases with item details
        """
        return self.purchase_repo.get_user_purchases_with_details(user.id)

    def get_purchase(self, user: User, purchase_id: uuid.UUID) -> dict:
        """
        Get a specific purchase with item details.

        Args:
            user: User object
            purchase_id: Purchase ID

        Returns:
            Purchase with item details

        Raises:
            HTTPException: If purchase not found or doesn't belong to user
        """
        purchase_data = self.purchase_repo.get_purchase_with_details(purchase_id)

        if not purchase_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase not found"
            )

        purchase = purchase_data["purchase"]

        # Verify ownership (users can only view their own purchases)
        if purchase.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this purchase"
            )

        return purchase_data

    # ============================================================================
    # Admin Operations
    # ============================================================================

    def complete_purchase(self, purchase_id: uuid.UUID) -> Purchase:
        """
        Mark purchase as completed (admin only).

        For course purchases: Auto-creates enrollment if not exists.
        For product purchases: No additional action needed.

        Idempotent: Safe to call on already-completed purchase.

        Args:
            purchase_id: Purchase ID

        Returns:
            Updated purchase

        Raises:
            HTTPException: If purchase not found
        """
        purchase = self.purchase_repo.get_purchase_by_id(purchase_id)

        if not purchase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase not found"
            )

        # If already completed, return as-is (idempotent)
        if purchase.status == PurchaseStatus.COMPLETED:
            return purchase

        # Cannot complete a failed purchase
        if purchase.status == PurchaseStatus.FAILED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot complete a failed purchase"
            )

        # Update status to completed
        purchase = self.purchase_repo.update_status(purchase, PurchaseStatus.COMPLETED)

        # If course purchase, auto-enroll user
        if purchase.course_id:
            self._auto_enroll_user(purchase.user_id, purchase.course_id)

        return purchase

    def fail_purchase(self, purchase_id: uuid.UUID) -> Purchase:
        """
        Mark purchase as failed (admin only).

        Args:
            purchase_id: Purchase ID

        Returns:
            Updated purchase

        Raises:
            HTTPException: If purchase not found or already completed
        """
        purchase = self.purchase_repo.get_purchase_by_id(purchase_id)

        if not purchase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase not found"
            )

        # If already failed, return as-is (idempotent)
        if purchase.status == PurchaseStatus.FAILED:
            return purchase

        # Cannot fail a completed purchase
        if purchase.status == PurchaseStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot fail a completed purchase"
            )

        # Update status to failed
        purchase = self.purchase_repo.update_status(purchase, PurchaseStatus.FAILED)

        return purchase

    # ============================================================================
    # Helper Methods
    # ============================================================================

    def _auto_enroll_user(self, user_id: uuid.UUID, course_id: uuid.UUID) -> None:
        """
        Auto-enroll user in course after purchase completion.

        Idempotent: Safe to call if already enrolled.

        Args:
            user_id: User ID
            course_id: Course ID
        """
        # Check if already enrolled
        existing_enrollment = self.enrollment_repo.get_enrollment(user_id, course_id)

        if not existing_enrollment:
            # Create enrollment
            self.enrollment_repo.create_enrollment(user_id, course_id)
