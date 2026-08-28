from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.product_repo import ProductRepository
from app.services.product_service import ProductService
from app.schemas.product import ProductListResponse, ProductResponse

router = APIRouter()


def get_product_service(db: Annotated[Session, Depends(get_db)]) -> ProductService:
    """Dependency to get product service instance."""
    repository = ProductRepository(db)
    return ProductService(repository)


@router.get("/", response_model=ProductListResponse)
def list_published_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: ProductService = Depends(get_product_service)
):
    """
    List all published products (public endpoint).

    Only products with status='published' are returned.
    Draft products are hidden from public view.

    Args:
        page: Page number (default: 1)
        page_size: Items per page (default: 20, max: 100)
        service: Product service instance

    Returns:
        Paginated list of published products
    """
    return service.get_published_products(page=page, page_size=page_size)


@router.get("/{slug}", response_model=ProductResponse)
def get_product_by_slug(
    slug: str,
    service: ProductService = Depends(get_product_service)
):
    """
    Get product details by slug (public endpoint).

    Only published products can be accessed.

    Args:
        slug: Product slug (URL-friendly identifier)
        service: Product service instance

    Returns:
        Product details

    Raises:
        404: If product not found or not published
    """
    return service.get_published_product_by_slug(slug)


@router.get("/health")
def products_health():
    """Health check endpoint for products router."""
    return {"status": "ok", "router": "products"}
