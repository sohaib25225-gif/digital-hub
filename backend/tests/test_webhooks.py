"""
Tests for Safepay webhook handling (Phase 6).

Tests cover all important webhook scenarios including:
- Valid payment.succeeded webhook
- Valid payment.failed webhook
- Invalid signature
- Missing signature
- Tampered body
- Duplicate webhooks (idempotency)
- Unknown events
- Missing/invalid data
- State transition edge cases
"""

import pytest
import json
import hmac
import hashlib
from fastapi import status
from uuid import uuid4

from app.db.models.user import User, UserRole
from app.db.models.purchase import Purchase, PurchaseStatus
from app.db.models.course import Course, CourseStatus
from app.db.models.creator import Creator
from app.core.config import settings


@pytest.fixture
def webhook_secret():
    """Get webhook secret for testing."""
    return settings.SAFEPAY_WEBHOOK_SECRET


def generate_signature(payload: dict, secret: str) -> str:
    """Generate HMAC-SHA512 signature for webhook payload."""
    # Use separators to ensure consistent formatting
    body_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    return hmac.new(
        secret.encode('utf-8'),
        body_bytes,
        hashlib.sha512
    ).hexdigest()


def send_webhook(client, payload: dict, secret: str):
    """Send webhook request with proper signature."""
    # Serialize payload with consistent formatting
    body_str = json.dumps(payload, separators=(',', ':'))
    body_bytes = body_str.encode('utf-8')

    # Generate signature
    signature = hmac.new(
        secret.encode('utf-8'),
        body_bytes,
        hashlib.sha512
    ).hexdigest()

    # Send request with raw bytes
    return client.post(
        "/webhooks/safepay",
        content=body_bytes,
        headers={
            "X-SFPY-SIGNATURE": signature,
            "Content-Type": "application/json"
        }
    )


@pytest.fixture
def test_user(client, db_session):
    """Create test user."""
    response = client.post(
        "/auth/register",
        json={
            "email": "webhook_user@test.com",
            "password": "password123",
            "full_name": "Webhook Test User"
        }
    )
    return response.json()


@pytest.fixture
def test_course(db_session):
    """Create test course with creator."""
    from decimal import Decimal
    from app.db.models.creator import Creator
    from app.core.security import get_password_hash

    # Create creator user
    user = User(
        email="creator@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Creator User",
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(user)
    db_session.flush()

    # Create creator profile
    creator = Creator(
        user_id=user.id,
        display_name="Test Creator",
        bio="Test bio",
        revenue_share_percent=Decimal("100.00")
    )
    db_session.add(creator)
    db_session.flush()

    # Create course
    course = Course(
        title="Test Course",
        slug="test-course",
        description="Test course for webhooks",
        price=Decimal("100.00"),
        status=CourseStatus.PUBLISHED,
        creator_id=creator.id
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)

    return course


@pytest.fixture
def pending_purchase(client, test_user, test_course, db_session):
    """Create a pending purchase with Safepay tracker."""
    from uuid import UUID
    from decimal import Decimal

    # Convert user ID string to UUID
    user_id = UUID(test_user["id"])

    # Get purchase from database
    purchase = db_session.query(Purchase).filter(
        Purchase.user_id == user_id
    ).first()

    if not purchase:
        # Create purchase directly in database for testing
        purchase = Purchase(
            user_id=user_id,
            course_id=test_course.id,
            amount=Decimal("100.00"),
            currency="PKR",
            status=PurchaseStatus.PENDING,
            payment_provider_tx_id="track_test_webhook_123"
        )
        db_session.add(purchase)
        db_session.commit()
        db_session.refresh(purchase)

    return purchase


# ============================================================================
# Valid Webhook Tests
# ============================================================================

def test_successful_payment_webhook(client, pending_purchase, webhook_secret):
    """Test valid payment.succeeded webhook."""
    purchase_id = str(pending_purchase.id)
    tracker_token = pending_purchase.payment_provider_tx_id

    payload = {
        "event": {
            "type": "payment.succeeded"
        },
        "data": {
            "tracker": tracker_token,
            "metadata": {
                "order_id": purchase_id
            },
            "payment_method": "card"
        }
    }

    response = send_webhook(client, payload, webhook_secret)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert data["purchase_id"] == purchase_id


def test_failed_payment_webhook(client, pending_purchase, webhook_secret):
    """Test valid payment.failed webhook."""
    purchase_id = str(pending_purchase.id)
    tracker_token = pending_purchase.payment_provider_tx_id

    payload = {
        "event": {
            "type": "payment.failed"
        },
        "data": {
            "tracker": tracker_token,
            "metadata": {
                "order_id": purchase_id
            }
        }
    }

    response = send_webhook(client, payload, webhook_secret)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert data["purchase_id"] == purchase_id


# ============================================================================
# Signature Validation Tests
# ============================================================================

def test_webhook_missing_signature(client, pending_purchase):
    """Test webhook without signature header."""
    payload = {
        "event": {"type": "payment.succeeded"},
        "data": {
            "tracker": pending_purchase.payment_provider_tx_id,
            "metadata": {"order_id": str(pending_purchase.id)}
        }
    }

    response = client.post("/webhooks/safepay", json=payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "signature" in response.json()["detail"].lower()


def test_webhook_invalid_signature(client, pending_purchase):
    """Test webhook with invalid signature."""
    payload = {
        "event": {"type": "payment.succeeded"},
        "data": {
            "tracker": pending_purchase.payment_provider_tx_id,
            "metadata": {"order_id": str(pending_purchase.id)}
        }
    }

    response = client.post(
        "/webhooks/safepay",
        json=payload,
        headers={"X-SFPY-SIGNATURE": "invalid_signature_123"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid webhook signature" in response.json()["detail"]


def test_webhook_tampered_body(client, pending_purchase, webhook_secret):
    """Test webhook where signature doesn't match body."""
    payload = {
        "event": {"type": "payment.succeeded"},
        "data": {
            "tracker": pending_purchase.payment_provider_tx_id,
            "metadata": {"order_id": str(pending_purchase.id)}
        }
    }

    # Generate signature for original payload
    signature = generate_signature(payload, webhook_secret)

    # Tamper with the payload
    payload["data"]["tracker"] = "tampered_tracker"

    response = client.post(
        "/webhooks/safepay",
        json=payload,
        headers={"X-SFPY-SIGNATURE": signature}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================================
# Idempotency Tests
# ============================================================================

def test_duplicate_success_webhook(client, pending_purchase, webhook_secret, db_session):
    """Test duplicate payment.succeeded webhooks (idempotency)."""
    purchase_id = str(pending_purchase.id)
    tracker_token = pending_purchase.payment_provider_tx_id

    payload = {
        "event": {"type": "payment.succeeded"},
        "data": {
            "tracker": tracker_token,
            "metadata": {"order_id": purchase_id},
            "payment_method": "card"
        }
    }

    # First webhook - should succeed
    response1 = send_webhook(client, payload, webhook_secret)
    assert response1.status_code == status.HTTP_200_OK

    # Second webhook - should be idempotent
    response2 = send_webhook(client, payload, webhook_secret)
    assert response2.status_code == status.HTTP_200_OK

    # Verify purchase is still completed (not double-processed)
    db_session.expire_all()
    purchase = db_session.query(Purchase).filter(
        Purchase.id == pending_purchase.id
    ).first()
    assert purchase.status == PurchaseStatus.COMPLETED


def test_duplicate_failure_webhook(client, pending_purchase, webhook_secret, db_session):
    """Test duplicate payment.failed webhooks (idempotency)."""
    purchase_id = str(pending_purchase.id)
    tracker_token = pending_purchase.payment_provider_tx_id

    payload = {
        "event": {"type": "payment.failed"},
        "data": {
            "tracker": tracker_token,
            "metadata": {"order_id": purchase_id}
        }
    }

    # First webhook
    response1 = send_webhook(client, payload, webhook_secret)
    assert response1.status_code == status.HTTP_200_OK

    # Second webhook - should be idempotent
    response2 = send_webhook(client, payload, webhook_secret)
    assert response2.status_code == status.HTTP_200_OK

    # Verify purchase is still failed (not double-processed)
    db_session.expire_all()
    purchase = db_session.query(Purchase).filter(
        Purchase.id == pending_purchase.id
    ).first()
    assert purchase.status == PurchaseStatus.FAILED


# ============================================================================
# Event Type Tests
# ============================================================================

def test_unknown_event_type(client, webhook_secret):
    """Test webhook with unknown event type."""
    payload = {
        "event": {"type": "payment.refunded"},
        "data": {
            "tracker": "track_unknown",
            "metadata": {"order_id": str(uuid4())}
        }
    }

    response = send_webhook(client, payload, webhook_secret)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ignored"


def test_webhook_missing_event_type(client, webhook_secret):
    """Test webhook missing event type."""
    payload = {
        "data": {
            "tracker": "track_test",
            "metadata": {"order_id": str(uuid4())}
        }
    }

    response = send_webhook(client, payload, webhook_secret)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "event type" in response.json()["detail"].lower()


# ============================================================================
# Data Validation Tests
# ============================================================================

def test_webhook_missing_tracker(client, pending_purchase, webhook_secret):
    """Test webhook missing tracker."""
    payload = {
        "event": {"type": "payment.succeeded"},
        "data": {
            "metadata": {"order_id": str(pending_purchase.id)}
        }
    }

    response = send_webhook(client, payload, webhook_secret)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "tracker" in response.json()["detail"].lower()


def test_webhook_missing_order_id(client, webhook_secret):
    """Test webhook missing order_id."""
    payload = {
        "event": {"type": "payment.succeeded"},
        "data": {
            "tracker": "track_test_missing_order",
            "metadata": {}
        }
    }

    response = send_webhook(client, payload, webhook_secret)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "order_id" in response.json()["detail"].lower()


def test_webhook_invalid_order_id_format(client, webhook_secret):
    """Test webhook with invalid order_id format."""
    payload = {
        "event": {"type": "payment.succeeded"},
        "data": {
            "tracker": "track_test_invalid_id",
            "metadata": {"order_id": "not-a-uuid"}
        }
    }

    response = send_webhook(client, payload, webhook_secret)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "order_id format" in response.json()["detail"].lower()


def test_webhook_invalid_json(client, webhook_secret):
    """Test webhook with invalid JSON."""
    invalid_json = b"not valid json"

    signature = hmac.new(
        webhook_secret.encode('utf-8'),
        invalid_json,
        hashlib.sha512
    ).hexdigest()

    response = client.post(
        "/webhooks/safepay",
        data=invalid_json,
        headers={
            "X-SFPY-SIGNATURE": signature,
            "Content-Type": "application/json"
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "JSON" in response.json()["detail"]


# ============================================================================
# Purchase State Tests
# ============================================================================

def test_webhook_nonexistent_purchase(client, webhook_secret):
    """Test webhook for non-existent purchase."""
    payload = {
        "event": {"type": "payment.succeeded"},
        "data": {
            "tracker": "track_nonexistent",
            "metadata": {"order_id": str(uuid4())}
        }
    }

    response = send_webhook(client, payload, webhook_secret)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_webhook_tracker_mismatch(client, pending_purchase, webhook_secret):
    """Test webhook with mismatched tracker token."""
    payload = {
        "event": {"type": "payment.succeeded"},
        "data": {
            "tracker": "track_wrong_token",
            "metadata": {"order_id": str(pending_purchase.id)}
        }
    }

    response = send_webhook(client, payload, webhook_secret)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "mismatch" in response.json()["detail"].lower()


def test_webhook_payment_method_present(client, pending_purchase, webhook_secret, db_session):
    """Test webhook with payment_method field."""
    purchase_id = str(pending_purchase.id)
    tracker_token = pending_purchase.payment_provider_tx_id

    payload = {
        "event": {"type": "payment.succeeded"},
        "data": {
            "tracker": tracker_token,
            "metadata": {"order_id": purchase_id},
            "payment_method": "wallet"
        }
    }

    response = send_webhook(client, payload, webhook_secret)

    assert response.status_code == status.HTTP_200_OK

    # Verify payment method was saved
    db_session.expire_all()
    purchase = db_session.query(Purchase).filter(
        Purchase.id == pending_purchase.id
    ).first()
    assert purchase.payment_method == "wallet"


def test_webhook_payment_method_null(client, pending_purchase, webhook_secret, db_session):
    """Test webhook with null/missing payment_method."""
    purchase_id = str(pending_purchase.id)
    tracker_token = pending_purchase.payment_provider_tx_id

    payload = {
        "event": {"type": "payment.succeeded"},
        "data": {
            "tracker": tracker_token,
            "metadata": {"order_id": purchase_id}
            # payment_method intentionally missing
        }
    }

    response = send_webhook(client, payload, webhook_secret)

    assert response.status_code == status.HTTP_200_OK

    # Verify purchase was completed even without payment_method
    db_session.expire_all()
    purchase = db_session.query(Purchase).filter(
        Purchase.id == pending_purchase.id
    ).first()
    assert purchase.status == PurchaseStatus.COMPLETED


# ============================================================================
# State Transition Edge Cases
# ============================================================================

def test_cannot_fail_completed_purchase(client, pending_purchase, webhook_secret, db_session):
    """Test that completed purchase cannot be failed."""
    purchase_id = str(pending_purchase.id)
    tracker_token = pending_purchase.payment_provider_tx_id

    # First complete the purchase
    success_payload = {
        "event": {"type": "payment.succeeded"},
        "data": {
            "tracker": tracker_token,
            "metadata": {"order_id": purchase_id}
        }
    }
    response1 = send_webhook(client, success_payload, webhook_secret)
    assert response1.status_code == status.HTTP_200_OK

    # Then try to fail it
    fail_payload = {
        "event": {"type": "payment.failed"},
        "data": {
            "tracker": tracker_token,
            "metadata": {"order_id": purchase_id}
        }
    }
    response2 = send_webhook(client, fail_payload, webhook_secret)

    assert response2.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cannot fail a completed purchase" in response2.json()["detail"]


def test_cannot_complete_failed_purchase(client, pending_purchase, webhook_secret, db_session):
    """Test that failed purchase cannot be completed."""
    purchase_id = str(pending_purchase.id)
    tracker_token = pending_purchase.payment_provider_tx_id

    # First fail the purchase
    fail_payload = {
        "event": {"type": "payment.failed"},
        "data": {
            "tracker": tracker_token,
            "metadata": {"order_id": purchase_id}
        }
    }
    response1 = send_webhook(client, fail_payload, webhook_secret)
    assert response1.status_code == status.HTTP_200_OK

    # Then try to complete it
    success_payload = {
        "event": {"type": "payment.succeeded"},
        "data": {
            "tracker": tracker_token,
            "metadata": {"order_id": purchase_id}
        }
    }
    response2 = send_webhook(client, success_payload, webhook_secret)

    assert response2.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cannot complete a failed purchase" in response2.json()["detail"]
