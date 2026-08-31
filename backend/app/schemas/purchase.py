from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, Literal
from datetime import datetime
from decimal import Decimal
import uuid


# ============================================================================
# Purchase Schemas
# ============================================================================

class PurchaseCreate(BaseModel):
    """Schema for creating a purchase."""
    course_id: Optional[uuid.UUID] = None
    product_id: Optional[uuid.UUID] = None
    amount: Decimal = Field(..., ge=0, description="Purchase amount")
    currency: str = Field(..., min_length=3, max_length=3, description="3-letter currency code (e.g. USD, PKR)")

    @field_validator('currency')
    @classmethod
    def currency_uppercase(cls, v: str) -> str:
        """Ensure currency is uppercase."""
        return v.upper()

    @model_validator(mode='after')
    def check_exactly_one_item(self):
        """Ensure exactly one of course_id or product_id is set."""
        course_set = self.course_id is not None
        product_set = self.product_id is not None

        if not course_set and not product_set:
            raise ValueError("Must specify either course_id or product_id")

        if course_set and product_set:
            raise ValueError("Cannot purchase both course and product in same purchase")

        return self


class PurchaseResponse(BaseModel):
    """Schema for purchase response."""
    id: uuid.UUID
    user_id: uuid.UUID
    course_id: Optional[uuid.UUID]
    product_id: Optional[uuid.UUID]
    amount: Decimal
    currency: str
    status: str  # PENDING, COMPLETED, FAILED
    created_at: datetime

    # Payment provider fields (Phase 6)
    payment_provider_tx_id: Optional[str] = None
    payment_method: Optional[str] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PurchaseWithDetails(BaseModel):
    """Schema for purchase with item details."""
    id: uuid.UUID
    user_id: uuid.UUID
    course_id: Optional[uuid.UUID]
    product_id: Optional[uuid.UUID]
    amount: Decimal
    currency: str
    status: str
    created_at: datetime
    item_title: str
    item_type: str  # "course" or "product"

    model_config = ConfigDict(from_attributes=True)


class PurchaseStatusUpdate(BaseModel):
    """Schema for admin updating purchase status."""
    status: Literal["COMPLETED", "FAILED"] = Field(..., description="New purchase status")
