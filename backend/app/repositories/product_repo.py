from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
import uuid

from app.db.models.product import Product, ProductStatus
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository:
    """Repository for product database operations."""

    def __init__(self, db: Session):
        self.db = db

    # ============================================================================
    # Product Operations
    # ============================================================================

    def create_product(self, product_data: ProductCreate, creator_id: uuid.UUID, slug: str) -> Product:
        """Create a new product."""
        product = Product(
            creator_id=creator_id,
            title=product_data.title,
            slug=slug,
            description=product_data.description,
            price=product_data.price,
            file_url=product_data.file_url,
            thumbnail_url=product_data.thumbnail_url,
            status=product_data.status,
        )
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def get_product_by_id(self, product_id: uuid.UUID) -> Optional[Product]:
        """Get product by ID."""
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_product_by_slug(self, slug: str) -> Optional[Product]:
        """Get product by slug."""
        return self.db.query(Product).filter(Product.slug == slug).first()

    def get_published_product_by_slug(self, slug: str) -> Optional[Product]:
        """Get published product by slug."""
        return (
            self.db.query(Product)
            .filter(Product.slug == slug, Product.status == ProductStatus.PUBLISHED)
            .first()
        )

    def get_all_products(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ProductStatus] = None
    ) -> Tuple[List[Product], int]:
        """
        Get all products with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Optional status filter

        Returns:
            Tuple of (products list, total count)
        """
        query = self.db.query(Product)

        if status:
            query = query.filter(Product.status == status)

        total = query.count()
        products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()

        return products, total

    def get_published_products(self, skip: int = 0, limit: int = 100) -> Tuple[List[Product], int]:
        """Get published products with pagination."""
        return self.get_all_products(skip=skip, limit=limit, status=ProductStatus.PUBLISHED)

    def update_product(self, product: Product, product_data: ProductUpdate) -> Product:
        """Update product fields."""
        update_data = product_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(product, field, value)

        self.db.commit()
        self.db.refresh(product)
        return product

    def delete_product(self, product: Product) -> None:
        """Delete a product."""
        self.db.delete(product)
        self.db.commit()

    def is_slug_available(self, slug: str, exclude_product_id: Optional[uuid.UUID] = None) -> bool:
        """Check if a slug is available."""
        query = self.db.query(Product).filter(Product.slug == slug)

        if exclude_product_id:
            query = query.filter(Product.id != exclude_product_id)

        return query.first() is None
