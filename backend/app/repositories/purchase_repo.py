from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
import uuid
from decimal import Decimal

from app.db.models.purchase import Purchase, PurchaseStatus
from app.db.models.course import Course
from app.db.models.product import Product


class PurchaseRepository:
    """Repository for purchase database operations."""

    def __init__(self, db: Session):
        self.db = db

    # ============================================================================
    # Creation
    # ============================================================================

    def create_purchase(
        self,
        user_id: uuid.UUID,
        course_id: Optional[uuid.UUID],
        product_id: Optional[uuid.UUID],
        amount: Decimal,
        currency: str
    ) -> Purchase:
        """
        Create a new purchase.

        Args:
            user_id: User ID
            course_id: Course ID (nullable)
            product_id: Product ID (nullable)
            amount: Purchase amount
            currency: 3-letter currency code

        Returns:
            Created purchase
        """
        purchase = Purchase(
            user_id=user_id,
            course_id=course_id,
            product_id=product_id,
            amount=amount,
            currency=currency,
            status=PurchaseStatus.PENDING
        )
        self.db.add(purchase)
        self.db.commit()
        self.db.refresh(purchase)
        return purchase

    # ============================================================================
    # Retrieval
    # ============================================================================

    def get_purchase_by_id(self, purchase_id: uuid.UUID) -> Optional[Purchase]:
        """
        Get purchase by ID.

        Args:
            purchase_id: Purchase ID

        Returns:
            Purchase if found, None otherwise
        """
        return (
            self.db.query(Purchase)
            .filter(Purchase.id == purchase_id)
            .first()
        )

    def get_purchase_with_details(self, purchase_id: uuid.UUID) -> Optional[dict]:
        """
        Get purchase by ID with item details.

        Args:
            purchase_id: Purchase ID

        Returns:
            Dict with purchase and item details, or None if not found
        """
        purchase = (
            self.db.query(Purchase)
            .options(
                joinedload(Purchase.course),
                joinedload(Purchase.product)
            )
            .filter(Purchase.id == purchase_id)
            .first()
        )

        if not purchase:
            return None

        # Build response with item details
        item_title = ""
        item_type = ""

        if purchase.course_id and purchase.course:
            item_title = purchase.course.title
            item_type = "course"
        elif purchase.product_id and purchase.product:
            item_title = purchase.product.title
            item_type = "product"

        return {
            "purchase": purchase,
            "item_title": item_title,
            "item_type": item_type
        }

    def get_user_purchases(self, user_id: uuid.UUID) -> List[Purchase]:
        """
        Get all purchases for a user.

        Args:
            user_id: User ID

        Returns:
            List of purchases
        """
        return (
            self.db.query(Purchase)
            .filter(Purchase.user_id == user_id)
            .order_by(Purchase.created_at.desc())
            .all()
        )

    def get_user_purchases_with_details(self, user_id: uuid.UUID) -> List[dict]:
        """
        Get all purchases for a user with item details.

        Args:
            user_id: User ID

        Returns:
            List of dicts with purchase and item details
        """
        purchases = (
            self.db.query(Purchase)
            .options(
                joinedload(Purchase.course),
                joinedload(Purchase.product)
            )
            .filter(Purchase.user_id == user_id)
            .order_by(Purchase.created_at.desc())
            .all()
        )

        results = []
        for purchase in purchases:
            item_title = ""
            item_type = ""

            if purchase.course_id and purchase.course:
                item_title = purchase.course.title
                item_type = "course"
            elif purchase.product_id and purchase.product:
                item_title = purchase.product.title
                item_type = "product"

            results.append({
                "purchase": purchase,
                "item_title": item_title,
                "item_type": item_type
            })

        return results

    # ============================================================================
    # State Checks
    # ============================================================================

    def has_pending_purchase(
        self,
        user_id: uuid.UUID,
        course_id: Optional[uuid.UUID],
        product_id: Optional[uuid.UUID]
    ) -> bool:
        """
        Check if user has a pending purchase for an item.

        Args:
            user_id: User ID
            course_id: Course ID (nullable)
            product_id: Product ID (nullable)

        Returns:
            True if pending purchase exists, False otherwise
        """
        query = (
            self.db.query(Purchase)
            .filter(
                Purchase.user_id == user_id,
                Purchase.status == PurchaseStatus.PENDING
            )
        )

        if course_id:
            query = query.filter(Purchase.course_id == course_id)
        elif product_id:
            query = query.filter(Purchase.product_id == product_id)

        return query.count() > 0

    def has_completed_purchase(
        self,
        user_id: uuid.UUID,
        course_id: Optional[uuid.UUID],
        product_id: Optional[uuid.UUID]
    ) -> bool:
        """
        Check if user has a completed purchase for an item.

        Args:
            user_id: User ID
            course_id: Course ID (nullable)
            product_id: Product ID (nullable)

        Returns:
            True if completed purchase exists, False otherwise
        """
        query = (
            self.db.query(Purchase)
            .filter(
                Purchase.user_id == user_id,
                Purchase.status == PurchaseStatus.COMPLETED
            )
        )

        if course_id:
            query = query.filter(Purchase.course_id == course_id)
        elif product_id:
            query = query.filter(Purchase.product_id == product_id)

        return query.count() > 0

    # ============================================================================
    # Updates
    # ============================================================================

    def update_status(self, purchase: Purchase, new_status: PurchaseStatus) -> Purchase:
        """
        Update purchase status.

        Args:
            purchase: Purchase to update
            new_status: New status

        Returns:
            Updated purchase
        """
        purchase.status = new_status
        self.db.commit()
        self.db.refresh(purchase)
        return purchase
