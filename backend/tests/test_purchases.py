import pytest
from fastapi import status
from sqlalchemy.orm import Session
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import UUID

from app.main import app
from app.core.dependencies import get_safepay_client
from app.db.models.user import User, UserRole
from app.db.models.creator import Creator
from app.db.models.course import Course, CourseStatus
from app.db.models.product import Product, ProductStatus
from app.db.models.purchase import Purchase, PurchaseStatus
from app.db.models.enrollment import Enrollment
from app.core.security import get_password_hash


# ============================================================================
# Mock Safepay Client (Phase 6)
# ============================================================================

class MockSafepayClient:
    """Mock Safepay client for testing purchase creation."""

    async def create_payment_session(
        self,
        purchase_id: UUID,
        amount: float,
        currency: str
    ):
        """Mock payment session creation."""
        return {
            "tracker_token": f"track_test_{str(purchase_id)[:8]}",
            "tracker_state": "TRACKER_STARTED",
            "intent": "CYBERSOURCE",
            "mode": "payment",
            "next_actions": {
                "CYBERSOURCE": {"kind": "GENERATE_CAPTURE_CONTEXT"}
            },
            "full_response": {
                "data": {
                    "tracker": {
                        "token": f"track_test_{str(purchase_id)[:8]}",
                        "state": "TRACKER_STARTED"
                    }
                }
            }
        }


@pytest.fixture
def mock_safepay_client():
    """Provide mock Safepay client for purchase tests."""
    return MockSafepayClient()


@pytest.fixture(autouse=True)
def override_safepay_dependency(mock_safepay_client):
    """
    Auto-override Safepay client dependency for all purchase tests.

    Phase 6 integration: PurchaseService now calls SafepayClient.
    Tests must mock this to avoid requiring real credentials.
    """
    app.dependency_overrides[get_safepay_client] = lambda: mock_safepay_client
    yield
    app.dependency_overrides.pop(get_safepay_client, None)


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
def paid_course(db_session: Session, admin_user_with_creator):
    """Create a paid published course."""
    creator = db_session.query(Creator).filter(Creator.user_id == admin_user_with_creator.id).first()

    course = Course(
        creator_id=creator.id,
        title="Paid Course",
        slug="paid-course",
        description="A paid course for testing",
        price=Decimal("99.99"),
        status=CourseStatus.PUBLISHED
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course


@pytest.fixture
def free_course(db_session: Session, admin_user_with_creator):
    """Create a free published course."""
    creator = db_session.query(Creator).filter(Creator.user_id == admin_user_with_creator.id).first()

    course = Course(
        creator_id=creator.id,
        title="Free Course",
        slug="free-course",
        description="A free course for testing",
        price=Decimal("0.00"),
        status=CourseStatus.PUBLISHED
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course


@pytest.fixture
def draft_course(db_session: Session, admin_user_with_creator):
    """Create a draft course."""
    creator = db_session.query(Creator).filter(Creator.user_id == admin_user_with_creator.id).first()

    course = Course(
        creator_id=creator.id,
        title="Draft Course",
        slug="draft-course",
        description="A draft course for testing",
        price=Decimal("49.99"),
        status=CourseStatus.DRAFT
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course


@pytest.fixture
def paid_product(db_session: Session, admin_user_with_creator):
    """Create a paid published product."""
    creator = db_session.query(Creator).filter(Creator.user_id == admin_user_with_creator.id).first()

    product = Product(
        creator_id=creator.id,
        title="Paid Product",
        slug="paid-product",
        description="A paid product for testing",
        price=Decimal("29.99"),
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
        description="A draft product for testing",
        price=Decimal("19.99"),
        status=ProductStatus.DRAFT
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


# ============================================================================
# Purchase Creation Tests
# ============================================================================

def test_create_course_purchase_success(client, student_token, paid_course):
    """Test creating a course purchase successfully (Phase 6: with Safepay integration)."""
    response = client.post(
        "/me/purchases",
        json={
            "course_id": str(paid_course.id),
            "product_id": None,
            "amount": float(paid_course.price),
            "currency": "USD"
        },
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    # Phase 6: Response now includes payment session info
    assert "purchase" in data
    assert "tracker_token" in data
    assert data["payment_provider"] == "safepay"

    # Verify purchase data
    purchase = data["purchase"]
    assert purchase["course_id"] == str(paid_course.id)
    assert purchase["product_id"] is None
    assert Decimal(str(purchase["amount"])) == paid_course.price
    assert purchase["currency"] == "USD"
    assert purchase["status"] == "pending"

    # Verify tracker token was generated
    assert data["tracker_token"].startswith("track_test_")


def test_create_product_purchase_success(client, student_token, paid_product):
    """Test creating a product purchase successfully (Phase 6: with Safepay integration)."""
    response = client.post(
        "/me/purchases",
        json={
            "course_id": None,
            "product_id": str(paid_product.id),
            "amount": float(paid_product.price),
            "currency": "PKR"
        },
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    # Phase 6: Response now includes payment session info
    assert "purchase" in data
    assert "tracker_token" in data
    assert data["payment_provider"] == "safepay"

    # Verify purchase data
    purchase = data["purchase"]
    assert purchase["product_id"] == str(paid_product.id)
    assert purchase["course_id"] is None
    assert Decimal(str(purchase["amount"])) == paid_product.price
    assert purchase["currency"] == "PKR"
    assert purchase["status"] == "pending"

    # Verify tracker token was generated
    assert data["tracker_token"].startswith("track_test_")


def test_create_purchase_course_not_found(client, student_token):
    """Test creating purchase for non-existent course returns 404."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.post(
        "/me/purchases",
        json={
            "course_id": fake_id,
            "product_id": None,
            "amount": 99.99,
            "currency": "USD"
        },
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


def test_create_purchase_product_not_found(client, student_token):
    """Test creating purchase for non-existent product returns 404."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.post(
        "/me/purchases",
        json={
            "course_id": None,
            "product_id": fake_id,
            "amount": 29.99,
            "currency": "USD"
        },
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


def test_create_purchase_draft_course_rejected(client, student_token, draft_course):
    """Test cannot purchase draft course."""
    response = client.post(
        "/me/purchases",
        json={
            "course_id": str(draft_course.id),
            "product_id": None,
            "amount": float(draft_course.price),
            "currency": "USD"
        },
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "draft" in response.json()["detail"].lower()


def test_create_purchase_draft_product_rejected(client, student_token, draft_product):
    """Test cannot purchase draft product."""
    response = client.post(
        "/me/purchases",
        json={
            "course_id": None,
            "product_id": str(draft_product.id),
            "amount": float(draft_product.price),
            "currency": "USD"
        },
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "draft" in response.json()["detail"].lower()


def test_create_purchase_free_course_rejected(client, student_token, free_course):
    """Test cannot purchase free course."""
    response = client.post(
        "/me/purchases",
        json={
            "course_id": str(free_course.id),
            "product_id": None,
            "amount": 0.00,
            "currency": "USD"
        },
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "free" in response.json()["detail"].lower()


def test_create_purchase_amount_mismatch(client, student_token, paid_course):
    """Test purchase rejected when amount doesn't match price."""
    response = client.post(
        "/me/purchases",
        json={
            "course_id": str(paid_course.id),
            "product_id": None,
            "amount": 50.00,  # Wrong amount
            "currency": "USD"
        },
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "amount" in response.json()["detail"].lower()


def test_create_purchase_duplicate_pending(client, student_token, paid_course, db_session, student_user):
    """Test cannot create duplicate pending purchase."""
    # Create first purchase
    purchase = Purchase(
        user_id=student_user.id,
        course_id=paid_course.id,
        amount=paid_course.price,
        currency="USD",
        status=PurchaseStatus.PENDING
    )
    db_session.add(purchase)
    db_session.commit()

    # Try to create another pending purchase
    response = client.post(
        "/me/purchases",
        json={
            "course_id": str(paid_course.id),
            "product_id": None,
            "amount": float(paid_course.price),
            "currency": "USD"
        },
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "pending" in response.json()["detail"].lower()


def test_create_purchase_duplicate_completed(client, student_token, paid_course, db_session, student_user):
    """Test cannot purchase already purchased course."""
    # Create completed purchase
    purchase = Purchase(
        user_id=student_user.id,
        course_id=paid_course.id,
        amount=paid_course.price,
        currency="USD",
        status=PurchaseStatus.COMPLETED
    )
    db_session.add(purchase)
    db_session.commit()

    # Try to create another purchase
    response = client.post(
        "/me/purchases",
        json={
            "course_id": str(paid_course.id),
            "product_id": None,
            "amount": float(paid_course.price),
            "currency": "USD"
        },
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already purchased" in response.json()["detail"].lower()


def test_create_purchase_must_specify_one_item(client, student_token):
    """Test must specify either course_id or product_id."""
    # Neither specified
    response = client.post(
        "/me/purchases",
        json={
            "course_id": None,
            "product_id": None,
            "amount": 99.99,
            "currency": "USD"
        },
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_purchase_cannot_specify_both_items(client, student_token, paid_course, paid_product):
    """Test cannot specify both course_id and product_id."""
    response = client.post(
        "/me/purchases",
        json={
            "course_id": str(paid_course.id),
            "product_id": str(paid_product.id),
            "amount": 99.99,
            "currency": "USD"
        },
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_purchase_unauthenticated(client, paid_course):
    """Test unauthenticated user cannot create purchase."""
    response = client.post(
        "/me/purchases",
        json={
            "course_id": str(paid_course.id),
            "product_id": None,
            "amount": float(paid_course.price),
            "currency": "USD"
        }
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_currency_uppercase_normalization(client, student_token, paid_course):
    """Test currency is normalized to uppercase (Phase 6: with Safepay integration)."""
    response = client.post(
        "/me/purchases",
        json={
            "course_id": str(paid_course.id),
            "product_id": None,
            "amount": float(paid_course.price),
            "currency": "usd"  # lowercase
        },
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    # Phase 6: Response now includes payment session info
    assert "purchase" in data
    purchase = data["purchase"]
    assert purchase["currency"] == "USD"


# ============================================================================
# Purchase Retrieval Tests
# ============================================================================

def test_list_user_purchases(client, student_token, student_user, paid_course, db_session):
    """Test user can list their own purchases."""
    # Create some purchases
    purchase1 = Purchase(
        user_id=student_user.id,
        course_id=paid_course.id,
        amount=paid_course.price,
        currency="USD",
        status=PurchaseStatus.COMPLETED
    )
    db_session.add(purchase1)
    db_session.commit()

    response = client.get(
        "/me/purchases",
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["item_title"] == paid_course.title
    assert data[0]["item_type"] == "course"


def test_get_specific_purchase(client, student_token, student_user, paid_course, db_session):
    """Test user can get specific purchase details."""
    purchase = Purchase(
        user_id=student_user.id,
        course_id=paid_course.id,
        amount=paid_course.price,
        currency="USD",
        status=PurchaseStatus.PENDING
    )
    db_session.add(purchase)
    db_session.commit()
    db_session.refresh(purchase)

    response = client.get(
        f"/me/purchases/{purchase.id}",
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(purchase.id)
    assert data["item_title"] == paid_course.title
    assert data["status"] == "pending"


def test_cannot_view_other_user_purchase(client, admin_token, student_user, paid_course, db_session):
    """Test user cannot view another user's purchase."""
    # Create purchase for student
    purchase = Purchase(
        user_id=student_user.id,
        course_id=paid_course.id,
        amount=paid_course.price,
        currency="USD",
        status=PurchaseStatus.PENDING
    )
    db_session.add(purchase)
    db_session.commit()
    db_session.refresh(purchase)

    # Try to view as admin (different user)
    response = client.get(
        f"/me/purchases/{purchase.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_purchases_unauthenticated(client):
    """Test unauthenticated user cannot list purchases."""
    response = client.get("/me/purchases")
    assert response.status_code == status.HTTP_403_FORBIDDEN


# ============================================================================
# Admin Purchase Management Tests
# ============================================================================

def test_admin_complete_purchase(client, admin_token, student_user, paid_course, db_session):
    """Test admin can mark purchase as completed."""
    purchase = Purchase(
        user_id=student_user.id,
        course_id=paid_course.id,
        amount=paid_course.price,
        currency="USD",
        status=PurchaseStatus.PENDING
    )
    db_session.add(purchase)
    db_session.commit()
    db_session.refresh(purchase)

    response = client.put(
        f"/admin/purchases/{purchase.id}/complete",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "completed"


def test_admin_fail_purchase(client, admin_token, student_user, paid_course, db_session):
    """Test admin can mark purchase as failed."""
    purchase = Purchase(
        user_id=student_user.id,
        course_id=paid_course.id,
        amount=paid_course.price,
        currency="USD",
        status=PurchaseStatus.PENDING
    )
    db_session.add(purchase)
    db_session.commit()
    db_session.refresh(purchase)

    response = client.put(
        f"/admin/purchases/{purchase.id}/fail",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "failed"


def test_student_cannot_complete_purchase(client, student_token, student_user, paid_course, db_session):
    """Test student cannot complete purchase."""
    purchase = Purchase(
        user_id=student_user.id,
        course_id=paid_course.id,
        amount=paid_course.price,
        currency="USD",
        status=PurchaseStatus.PENDING
    )
    db_session.add(purchase)
    db_session.commit()
    db_session.refresh(purchase)

    response = client.put(
        f"/admin/purchases/{purchase.id}/complete",
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_complete_already_completed_purchase_idempotent(client, admin_token, student_user, paid_course, db_session):
    """Test completing already-completed purchase is idempotent."""
    purchase = Purchase(
        user_id=student_user.id,
        course_id=paid_course.id,
        amount=paid_course.price,
        currency="USD",
        status=PurchaseStatus.COMPLETED
    )
    db_session.add(purchase)
    db_session.commit()
    db_session.refresh(purchase)

    response = client.put(
        f"/admin/purchases/{purchase.id}/complete",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "completed"


def test_cannot_complete_failed_purchase(client, admin_token, student_user, paid_course, db_session):
    """Test cannot complete a failed purchase."""
    purchase = Purchase(
        user_id=student_user.id,
        course_id=paid_course.id,
        amount=paid_course.price,
        currency="USD",
        status=PurchaseStatus.FAILED
    )
    db_session.add(purchase)
    db_session.commit()
    db_session.refresh(purchase)

    response = client.put(
        f"/admin/purchases/{purchase.id}/complete",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_cannot_fail_completed_purchase(client, admin_token, student_user, paid_course, db_session):
    """Test cannot fail a completed purchase."""
    purchase = Purchase(
        user_id=student_user.id,
        course_id=paid_course.id,
        amount=paid_course.price,
        currency="USD",
        status=PurchaseStatus.COMPLETED
    )
    db_session.add(purchase)
    db_session.commit()
    db_session.refresh(purchase)

    response = client.put(
        f"/admin/purchases/{purchase.id}/fail",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============================================================================
# Auto-Enrollment Tests
# ============================================================================

def test_complete_course_purchase_creates_enrollment(client, admin_token, student_user, paid_course, db_session):
    """Test completing course purchase automatically creates enrollment."""
    purchase = Purchase(
        user_id=student_user.id,
        course_id=paid_course.id,
        amount=paid_course.price,
        currency="USD",
        status=PurchaseStatus.PENDING
    )
    db_session.add(purchase)
    db_session.commit()
    db_session.refresh(purchase)

    # Complete purchase
    response = client.put(
        f"/admin/purchases/{purchase.id}/complete",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    # Check enrollment was created
    enrollment = db_session.query(Enrollment).filter(
        Enrollment.user_id == student_user.id,
        Enrollment.course_id == paid_course.id
    ).first()

    assert enrollment is not None
    assert enrollment.progress_percent == Decimal("0.00")


def test_complete_course_purchase_already_enrolled_safe(client, admin_token, student_user, paid_course, db_session):
    """Test completing course purchase when already enrolled is safe."""
    # Create purchase
    purchase = Purchase(
        user_id=student_user.id,
        course_id=paid_course.id,
        amount=paid_course.price,
        currency="USD",
        status=PurchaseStatus.PENDING
    )
    db_session.add(purchase)

    # Create existing enrollment
    enrollment = Enrollment(
        user_id=student_user.id,
        course_id=paid_course.id,
        progress_percent=Decimal("50.00")
    )
    db_session.add(enrollment)
    db_session.commit()
    db_session.refresh(purchase)

    # Complete purchase
    response = client.put(
        f"/admin/purchases/{purchase.id}/complete",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    # Check original enrollment still exists with same progress
    enrollments = db_session.query(Enrollment).filter(
        Enrollment.user_id == student_user.id,
        Enrollment.course_id == paid_course.id
    ).all()

    assert len(enrollments) == 1
    assert enrollments[0].progress_percent == Decimal("50.00")


def test_complete_product_purchase_no_enrollment(client, admin_token, student_user, paid_product, db_session):
    """Test completing product purchase does not create enrollment."""
    purchase = Purchase(
        user_id=student_user.id,
        product_id=paid_product.id,
        amount=paid_product.price,
        currency="USD",
        status=PurchaseStatus.PENDING
    )
    db_session.add(purchase)
    db_session.commit()
    db_session.refresh(purchase)

    # Complete purchase
    response = client.put(
        f"/admin/purchases/{purchase.id}/complete",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    # Check no enrollments were created
    enrollments = db_session.query(Enrollment).filter(
        Enrollment.user_id == student_user.id
    ).all()

    assert len(enrollments) == 0


def test_failed_purchase_no_enrollment(client, admin_token, student_user, paid_course, db_session):
    """Test failed purchase does not create enrollment."""
    purchase = Purchase(
        user_id=student_user.id,
        course_id=paid_course.id,
        amount=paid_course.price,
        currency="USD",
        status=PurchaseStatus.PENDING
    )
    db_session.add(purchase)
    db_session.commit()
    db_session.refresh(purchase)

    # Fail purchase
    response = client.put(
        f"/admin/purchases/{purchase.id}/fail",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    # Check no enrollment was created
    enrollment = db_session.query(Enrollment).filter(
        Enrollment.user_id == student_user.id,
        Enrollment.course_id == paid_course.id
    ).first()

    assert enrollment is None


# ============================================================================
# Access Control Integration Tests
# ============================================================================

def test_completed_purchase_grants_course_access(client, student_token, student_user, paid_course, db_session):
    """Test completed purchase grants access to course content."""
    # Create completed purchase
    purchase = Purchase(
        user_id=student_user.id,
        course_id=paid_course.id,
        amount=paid_course.price,
        currency="USD",
        status=PurchaseStatus.COMPLETED
    )
    db_session.add(purchase)

    # Create enrollment (would happen via auto-enroll)
    enrollment = Enrollment(
        user_id=student_user.id,
        course_id=paid_course.id
    )
    db_session.add(enrollment)
    db_session.commit()

    # Try to access course
    response = client.get(
        f"/me/courses/{paid_course.id}",
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == status.HTTP_200_OK


def test_pending_purchase_denies_course_access(client, student_token, student_user, paid_course, db_session):
    """Test pending purchase does not grant access to course."""
    # Create pending purchase (no enrollment)
    purchase = Purchase(
        user_id=student_user.id,
        course_id=paid_course.id,
        amount=paid_course.price,
        currency="USD",
        status=PurchaseStatus.PENDING
    )
    db_session.add(purchase)
    db_session.commit()

    # Try to access course
    response = client.get(
        f"/me/courses/{paid_course.id}",
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_completed_purchase_grants_product_access(client, student_token, student_user, paid_product, db_session):
    """Test completed purchase grants access to product download."""
    # Create completed purchase
    purchase = Purchase(
        user_id=student_user.id,
        product_id=paid_product.id,
        amount=paid_product.price,
        currency="USD",
        status=PurchaseStatus.COMPLETED
    )
    db_session.add(purchase)

    # Set product file_url
    paid_product.file_url = "https://example.com/product.pdf"
    db_session.commit()

    # Try to download product (would return signed URL if file exists)
    response = client.get(
        f"/me/products/{paid_product.id}/download",
        headers={"Authorization": f"Bearer {student_token}"}
    )

    # Will fail at signed URL generation but passes access check
    # (Actual signed URL generation requires Supabase)
    assert response.status_code != status.HTTP_403_FORBIDDEN


def test_pending_purchase_denies_product_access(client, student_token, student_user, paid_product, db_session):
    """Test pending purchase does not grant product download access."""
    # Create pending purchase
    purchase = Purchase(
        user_id=student_user.id,
        product_id=paid_product.id,
        amount=paid_product.price,
        currency="USD",
        status=PurchaseStatus.PENDING
    )
    db_session.add(purchase)
    db_session.commit()

    # Try to download product
    response = client.get(
        f"/me/products/{paid_product.id}/download",
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
