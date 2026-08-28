from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import uuid

from app.db.models.product import ProductStatus


# ============================================================================
# Product Schemas
# ============================================================================

class ProductCreate(BaseModel):
    """Schema for creating a product."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0)
    file_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    status: ProductStatus = ProductStatus.DRAFT


class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    file_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    status: Optional[ProductStatus] = None


class ProductBase(BaseModel):
    """Base product schema with common fields."""
    id: uuid.UUID
    creator_id: uuid.UUID
    title: str
    slug: str
    description: Optional[str]
    price: Decimal
    file_url: Optional[str]
    thumbnail_url: Optional[str]
    status: ProductStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductResponse(ProductBase):
    """Schema for product response."""
    pass


class ProductListItem(BaseModel):
    """Schema for product in list response."""
    id: uuid.UUID
    title: str
    slug: str
    description: Optional[str]
    price: Decimal
    thumbnail_url: Optional[str]
    status: ProductStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    """Schema for paginated product list response."""
    products: List[ProductListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
