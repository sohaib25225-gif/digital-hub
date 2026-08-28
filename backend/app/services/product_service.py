import re
import uuid
from typing import Optional
from fastapi import HTTPException, status

from app.repositories.product_repo import ProductRepository
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductListResponse,
    ProductListItem,
)
from app.db.models.product import Product
from app.db.models.user import User


class ProductService:
    """Service layer for product business logic."""

    def __init__(self, repository: ProductRepository):
        self.repository = repository

    # ============================================================================
    # Utility Methods
    # ============================================================================

    @staticmethod
    def generate_slug(title: str) -> str:
        """
        Generate a URL-friendly slug from a title.

        Args:
            title: The product title

        Returns:
            A slugified version of the title
        """
        # Convert to lowercase
        slug = title.lower()

        # Replace spaces and special characters with hyphens
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)

        # Remove leading/trailing hyphens
        slug = slug.strip('-')

        # Ensure slug is not empty
        if not slug:
            slug = "product"

        return slug

    def ensure_unique_slug(self, base_slug: str, exclude_product_id: Optional[uuid.UUID] = None) -> str:
        """
        Ensure slug is unique by appending a number if necessary.

        Args:
            base_slug: The base slug to check
            exclude_product_id: Optional product ID to exclude from uniqueness check

        Returns:
            A unique slug
        """
        slug = base_slug
        counter = 1

        while not self.repository.is_slug_available(slug, exclude_product_id):
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def get_creator_id_for_user(self, user: User) -> uuid.UUID:
        """
        Get the creator ID for a user.

        Args:
            user: The user object

        Returns:
            The creator ID

        Raises:
            HTTPException: If user doesn't have a creator profile
        """
        if not user.creator:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have a creator profile"
            )

        return user.creator.id

    # ============================================================================
    # Product Operations
    # ============================================================================

    def create_product(self, product_data: ProductCreate, current_user: User) -> Product:
        """
        Create a new product.

        Args:
            product_data: Product creation data
            current_user: The authenticated admin user

        Returns:
            The created product

        Raises:
            HTTPException: If user doesn't have creator profile
        """
        # Get or validate creator
        creator_id = self.get_creator_id_for_user(current_user)

        # Generate unique slug
        base_slug = self.generate_slug(product_data.title)
        unique_slug = self.ensure_unique_slug(base_slug)

        # Create product
        product = self.repository.create_product(
            product_data=product_data,
            creator_id=creator_id,
            slug=unique_slug
        )

        return product

    def get_product_by_id(self, product_id: uuid.UUID) -> Product:
        """
        Get product by ID.

        Args:
            product_id: The product ID

        Returns:
            The product

        Raises:
            HTTPException: If product not found
        """
        product = self.repository.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product

    def get_published_product_by_slug(self, slug: str) -> Product:
        """
        Get published product by slug.

        Args:
            slug: The product slug

        Returns:
            The published product

        Raises:
            HTTPException: If product not found or not published
        """
        product = self.repository.get_published_product_by_slug(slug)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        return product

    def get_all_products(self, page: int = 1, page_size: int = 20) -> ProductListResponse:
        """
        Get all products with pagination (admin only).

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            Paginated product list
        """
        skip = (page - 1) * page_size
        products, total = self.repository.get_all_products(skip=skip, limit=page_size)

        total_pages = (total + page_size - 1) // page_size

        return ProductListResponse(
            products=[ProductListItem.model_validate(product) for product in products],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    def get_published_products(self, page: int = 1, page_size: int = 20) -> ProductListResponse:
        """
        Get published products with pagination (public).

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            Paginated product list
        """
        skip = (page - 1) * page_size
        products, total = self.repository.get_published_products(skip=skip, limit=page_size)

        total_pages = (total + page_size - 1) // page_size

        return ProductListResponse(
            products=[ProductListItem.model_validate(product) for product in products],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    def update_product(self, product_id: uuid.UUID, product_data: ProductUpdate) -> Product:
        """
        Update a product.

        Args:
            product_id: The product ID
            product_data: Product update data

        Returns:
            The updated product

        Raises:
            HTTPException: If product not found or slug already exists
        """
        product = self.get_product_by_id(product_id)

        # If slug is being updated, ensure it's unique
        if product_data.slug is not None:
            if not self.repository.is_slug_available(product_data.slug, exclude_product_id=product_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Slug already exists"
                )

        return self.repository.update_product(product, product_data)

    def delete_product(self, product_id: uuid.UUID) -> None:
        """
        Delete a product.

        Args:
            product_id: The product ID

        Raises:
            HTTPException: If product not found
        """
        product = self.get_product_by_id(product_id)
        self.repository.delete_product(product)
