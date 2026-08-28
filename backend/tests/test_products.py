import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.db.models.user import User, UserRole
from app.db.models.creator import Creator
from app.db.models.product import Product, ProductStatus
from app.core.security import get_password_hash
from decimal import Decimal


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def admin_user_with_creator(db_session: Session):
    """Create an admin user with creator profile."""
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    creator = Creator(
        user_id=user.id,
        display_name="Admin Creator",
        bio="Test creator bio",
        revenue_share_percent=Decimal("100.00")
    )
    db_session.add(creator)
    db_session.commit()
    db_session.refresh(creator)

    return user


@pytest.fixture
def admin_token(client, admin_user_with_creator):
    """Get admin authentication token."""
    response = client.post(
        "/auth/login",
        json={
            "email": "admin@example.com",
            "password": "password123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def student_user(db_session: Session):
    """Create a student user."""
    user = User(
        email="student@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Student User",
        role=UserRole.STUDENT,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def student_token(client, student_user):
    """Get student authentication token."""
    response = client.post(
        "/auth/login",
        json={
            "email": "student@example.com",
            "password": "password123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def sample_product(db_session: Session, admin_user_with_creator):
    """Create a sample published product."""
    creator = db_session.query(Creator).filter(Creator.user_id == admin_user_with_creator.id).first()

    product = Product(
        creator_id=creator.id,
        title="Sample Product",
        slug="sample-product",
        description="A sample product for testing",
        price=Decimal("49.99"),
        file_url="https://example.com/file.pdf",
        thumbnail_url="https://example.com/thumb.jpg",
        status=ProductStatus.PUBLISHED
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def draft_product(db_session: Session, admin_user_with_creator):
    """Create a draft product."""
    creator = db_session.query(Creator).filter(Creator.user_id == admin_user_with_creator.id).first()

    product = Product(
        creator_id=creator.id,
        title="Draft Product",
        slug="draft-product",
        description="A draft product",
        price=Decimal("29.99"),
        status=ProductStatus.DRAFT
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


# ============================================================================
# Public Product Listing Tests
# ============================================================================

class TestPublicProductListing:
    """Tests for public product listing endpoint."""

    def test_list_published_products(self, client, sample_product):
        """Test listing published products returns only published products."""
        response = client.get("/products/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "products" in data
        assert "total" in data
        assert data["total"] >= 1
        assert len(data["products"]) >= 1

        # Verify product data
        product = data["products"][0]
        assert product["slug"] == "sample-product"
        assert product["title"] == "Sample Product"
        assert product["status"] == "published"

    def test_list_products_excludes_drafts(self, client, sample_product, draft_product):
        """Test that draft products are not visible in public listing."""
        response = client.get("/products/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify only published product is returned
        slugs = [product["slug"] for product in data["products"]]
        assert "sample-product" in slugs
        assert "draft-product" not in slugs

    def test_list_products_pagination(self, client, admin_user_with_creator, db_session):
        """Test product listing pagination."""
        creator = db_session.query(Creator).filter(Creator.user_id == admin_user_with_creator.id).first()

        # Create multiple products
        for i in range(5):
            product = Product(
                creator_id=creator.id,
                title=f"Product {i}",
                slug=f"product-{i}",
                price=Decimal("9.99"),
                status=ProductStatus.PUBLISHED
            )
            db_session.add(product)
        db_session.commit()

        # Test page 1
        response = client.get("/products/?page=1&page_size=3")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["products"]) == 3
        assert data["page"] == 1
        assert data["page_size"] == 3

        # Test page 2
        response = client.get("/products/?page=2&page_size=3")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["products"]) >= 1


# ============================================================================
# Public Product Detail Tests
# ============================================================================

class TestPublicProductDetail:
    """Tests for public product detail endpoint."""

    def test_get_published_product_by_slug(self, client, sample_product):
        """Test getting published product by slug."""
        response = client.get(f"/products/{sample_product.slug}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["slug"] == "sample-product"
        assert data["title"] == "Sample Product"
        assert data["description"] == "A sample product for testing"
        assert float(data["price"]) == 49.99
        assert data["file_url"] == "https://example.com/file.pdf"
        assert data["thumbnail_url"] == "https://example.com/thumb.jpg"
        assert data["status"] == "published"

    def test_get_draft_product_returns_404(self, client, draft_product):
        """Test that draft products cannot be accessed publicly."""
        response = client.get(f"/products/{draft_product.slug}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_nonexistent_product_returns_404(self, client):
        """Test getting non-existent product returns 404."""
        response = client.get("/products/nonexistent-slug")

        assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Admin Product Creation Tests
# ============================================================================

class TestAdminProductCreation:
    """Tests for admin product creation."""

    def test_create_product_success(self, client, admin_token):
        """Test successful product creation by admin."""
        response = client.post(
            "/admin/products",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "New Product",
                "description": "A brand new product",
                "price": 79.99,
                "file_url": "https://example.com/new-file.pdf",
                "thumbnail_url": "https://example.com/new-thumb.jpg",
                "status": "draft"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "New Product"
        assert data["slug"] == "new-product"  # Auto-generated slug
        assert data["description"] == "A brand new product"
        assert float(data["price"]) == 79.99
        assert data["file_url"] == "https://example.com/new-file.pdf"
        assert data["thumbnail_url"] == "https://example.com/new-thumb.jpg"
        assert data["status"] == "draft"
        assert "id" in data
        assert "creator_id" in data

    def test_create_product_generates_unique_slug(self, client, admin_token, sample_product):
        """Test that duplicate titles generate unique slugs."""
        # Create product with same title as existing
        response = client.post(
            "/admin/products",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Sample Product",  # Same as existing
                "description": "Another product",
                "price": 19.99,
                "status": "draft"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Sample Product"
        assert data["slug"] != "sample-product"  # Should be unique
        assert data["slug"].startswith("sample-product-")

    def test_create_product_without_auth_fails(self, client):
        """Test that unauthenticated users cannot create products."""
        response = client.post(
            "/admin/products",
            json={
                "title": "Unauthorized Product",
                "price": 9.99,
                "status": "draft"
            }
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_product_as_student_fails(self, client, student_token):
        """Test that students cannot create products."""
        response = client.post(
            "/admin/products",
            headers={"Authorization": f"Bearer {student_token}"},
            json={
                "title": "Student Product",
                "price": 9.99,
                "status": "draft"
            }
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


# ============================================================================
# Admin Product Management Tests
# ============================================================================

class TestAdminProductManagement:
    """Tests for admin product management."""

    def test_list_all_products_includes_drafts(self, client, admin_token, sample_product, draft_product):
        """Test that admin can see both published and draft products."""
        response = client.get(
            "/admin/products",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        slugs = [product["slug"] for product in data["products"]]
        assert "sample-product" in slugs
        assert "draft-product" in slugs

    def test_get_product_detail_by_id(self, client, admin_token, sample_product):
        """Test getting product detail by ID."""
        response = client.get(
            f"/admin/products/{sample_product.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(sample_product.id)
        assert data["title"] == sample_product.title

    def test_update_product(self, client, admin_token, sample_product):
        """Test updating product fields."""
        response = client.put(
            f"/admin/products/{sample_product.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Updated Product Title",
                "price": 99.99
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Product Title"
        assert float(data["price"]) == 99.99

    def test_publish_product(self, client, admin_token, draft_product):
        """Test publishing a draft product."""
        response = client.put(
            f"/admin/products/{draft_product.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "status": "published"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "published"

    def test_unpublish_product(self, client, admin_token, sample_product):
        """Test unpublishing a product."""
        response = client.put(
            f"/admin/products/{sample_product.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "status": "draft"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "draft"

    def test_delete_product(self, client, admin_token, draft_product):
        """Test deleting a product."""
        response = client.delete(
            f"/admin/products/{draft_product.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify product is deleted
        response = client.get(
            f"/admin/products/{draft_product.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Authorization Tests
# ============================================================================

class TestAuthorization:
    """Tests for endpoint authorization."""

    def test_student_cannot_access_admin_endpoints(self, client, student_token, sample_product):
        """Test that students cannot access admin endpoints."""
        # Try to create product
        response = client.post(
            "/admin/products",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"title": "Unauthorized", "price": 9.99, "status": "draft"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Try to update product
        response = client.put(
            f"/admin/products/{sample_product.id}",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"title": "Hacked"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Try to delete product
        response = client.delete(
            f"/admin/products/{sample_product.id}",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_access_admin_endpoints(self, client, sample_product):
        """Test that unauthenticated users cannot access admin endpoints."""
        # Try to list all products (including drafts)
        response = client.get("/admin/products")
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Try to create product
        response = client.post(
            "/admin/products",
            json={"title": "Unauthorized", "price": 9.99, "status": "draft"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ============================================================================
# Edge Cases and Validation Tests
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and validation."""

    def test_create_product_with_special_characters_in_title(self, client, admin_token):
        """Test slug generation with special characters."""
        response = client.post(
            "/admin/products",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "E-Book: Python for Beginners!",
                "price": 19.99,
                "status": "draft"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        # Slug should be cleaned of special characters
        assert "e-book" in data["slug"].lower()
        assert "python" in data["slug"].lower()

    def test_create_product_with_negative_price_fails(self, client, admin_token):
        """Test that negative prices are rejected."""
        response = client.post(
            "/admin/products",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Free Product",
                "price": -10.00,
                "status": "draft"
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_product_with_zero_price(self, client, admin_token):
        """Test that zero price is allowed (free products)."""
        response = client.post(
            "/admin/products",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Free Product",
                "price": 0.00,
                "status": "draft"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert float(data["price"]) == 0.00

    def test_update_product_with_duplicate_slug(self, client, admin_token, sample_product, draft_product):
        """Test that updating to a duplicate slug fails."""
        response = client.put(
            f"/admin/products/{draft_product.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "slug": sample_product.slug  # Duplicate slug
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()

    def test_create_product_with_minimal_fields(self, client, admin_token):
        """Test creating product with only required fields."""
        response = client.post(
            "/admin/products",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Minimal Product",
                "price": 9.99
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Minimal Product"
        assert data["description"] is None
        assert data["file_url"] is None
        assert data["thumbnail_url"] is None
        assert data["status"] == "draft"  # Default status

    def test_update_product_partial_fields(self, client, admin_token, sample_product):
        """Test updating only some fields preserves others."""
        original_price = sample_product.price
        original_description = sample_product.description

        response = client.put(
            f"/admin/products/{sample_product.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "New Title Only"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "New Title Only"
        assert float(data["price"]) == float(original_price)  # Unchanged
        assert data["description"] == original_description  # Unchanged

    def test_get_product_by_invalid_uuid(self, client, admin_token):
        """Test getting product with invalid UUID format."""
        response = client.get(
            "/admin/products/not-a-uuid",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_product_ordering_by_creation_date(self, client, admin_user_with_creator, db_session):
        """Test that products are ordered by creation date (newest first)."""
        creator = db_session.query(Creator).filter(Creator.user_id == admin_user_with_creator.id).first()

        # Create products in order
        product1 = Product(
            creator_id=creator.id,
            title="First Product",
            slug="first-product",
            price=Decimal("10.00"),
            status=ProductStatus.PUBLISHED
        )
        db_session.add(product1)
        db_session.commit()

        product2 = Product(
            creator_id=creator.id,
            title="Second Product",
            slug="second-product",
            price=Decimal("20.00"),
            status=ProductStatus.PUBLISHED
        )
        db_session.add(product2)
        db_session.commit()

        # Get products
        response = client.get("/products/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Most recent should be first
        assert data["products"][0]["slug"] == "second-product"
        assert data["products"][1]["slug"] == "first-product"
