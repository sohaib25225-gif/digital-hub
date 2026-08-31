"""
Tests for Safepay API client (Phase 6 - Stage 3).

Based on Stage 0 verification results.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
import hmac
import hashlib
from fastapi import HTTPException

from app.services.safepay_client import SafepayClient


@pytest.fixture
def safepay_client():
    """Create Safepay client instance with test credentials."""
    with patch('app.services.safepay_client.settings') as mock_settings:
        mock_settings.SAFEPAY_PUBLIC_KEY = "test_public_key"
        mock_settings.SAFEPAY_SECRET_KEY = "test_secret_key"
        mock_settings.SAFEPAY_BASE_URL = "https://sandbox.api.getsafepay.com"
        mock_settings.SAFEPAY_WEBHOOK_SECRET = "test_webhook_secret"
        mock_settings.SAFEPAY_ENVIRONMENT = "sandbox"

        return SafepayClient()


@pytest.mark.asyncio
async def test_create_payment_session_success(safepay_client):
    """Test successful payment session creation with VERIFIED Stage 0 structure."""
    # VERIFIED: Actual Safepay API response structure from Stage 0
    mock_response = {
        "data": {
            "tracker": {
                "token": "track_test_123",
                "state": "TRACKER_STARTED",
                "intent": "CYBERSOURCE",
                "mode": "payment",
                "next_actions": {
                    "CYBERSOURCE": {"kind": "GENERATE_CAPTURE_CONTEXT"}
                }
            }
        }
    }

    with patch('app.services.safepay_client.httpx.AsyncClient') as mock_client_class:
        # Create a mock that properly handles async context manager
        mock_client_instance = AsyncMock()
        mock_response_obj = MagicMock()
        mock_response_obj.json = MagicMock(return_value=mock_response)
        mock_response_obj.raise_for_status = MagicMock()

        # Configure the post method to return the response
        mock_client_instance.post = AsyncMock(return_value=mock_response_obj)

        # Configure async context manager
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await safepay_client.create_payment_session(
            purchase_id=uuid4(),
            amount=99.99,
            currency="PKR"
        )

        # Verify tracker token extracted correctly
        assert result["tracker_token"] == "track_test_123"
        assert result["tracker_state"] == "TRACKER_STARTED"
        assert result["intent"] == "CYBERSOURCE"
        assert result["mode"] == "payment"

        # Verify request was made correctly
        call_args = mock_client_instance.post.call_args
        assert call_args[0][0] == "https://sandbox.api.getsafepay.com/order/payments/v3/"

        # VERIFIED: Request body structure from Stage 0
        request_body = call_args[1]['json']
        assert request_body["merchant_api_key"] == "test_public_key"
        assert request_body["intent"] == "CYBERSOURCE"
        assert request_body["mode"] == "payment"
        assert request_body["currency"] == "PKR"
        assert request_body["amount"] == 9999  # 99.99 PKR * 100 = 9999 paisa

        # VERIFIED: metadata.order_id structure (NOT metadata.data.order_id in request)
        assert "order_id" in request_body["metadata"]
        # VERIFIED: product_type should NOT be sent
        assert "product_type" not in request_body["metadata"]

        # VERIFIED: Authorization header
        assert "Authorization" in call_args[1]['headers']
        assert call_args[1]['headers']["Authorization"] == "Bearer test_secret_key"


@pytest.mark.asyncio
async def test_create_payment_session_amount_conversion(safepay_client):
    """Test amount conversion to paisa (VERIFIED in Stage 0)."""
    mock_response = {
        "data": {
            "tracker": {
                "token": "track_test_amount",
                "state": "TRACKER_STARTED"
            }
        }
    }

    with patch('app.services.safepay_client.httpx.AsyncClient') as mock_client_class:
        # Create a mock that properly handles async context manager
        mock_client_instance = AsyncMock()
        mock_response_obj = MagicMock()
        mock_response_obj.json = MagicMock(return_value=mock_response)
        mock_response_obj.raise_for_status = MagicMock()

        # Configure the post method to return the response
        mock_client_instance.post = AsyncMock(return_value=mock_response_obj)

        # Configure async context manager
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

        # Test different amounts
        test_cases = [
            (1000.00, 100000),  # 1000 PKR = 100000 paisa
            (50.50, 5050),      # 50.50 PKR = 5050 paisa
            (0.01, 1),          # 0.01 PKR = 1 paisa
        ]

        for pkr_amount, expected_paisa in test_cases:
            await safepay_client.create_payment_session(
                purchase_id=uuid4(),
                amount=pkr_amount,
                currency="PKR"
            )

            request_body = mock_client_instance.post.call_args[1]['json']
            assert request_body["amount"] == expected_paisa, \
                f"PKR {pkr_amount} should convert to {expected_paisa} paisa"


@pytest.mark.asyncio
async def test_create_payment_session_missing_tracker(safepay_client):
    """Test handling of response missing tracker token."""
    mock_response = {
        "data": {}  # Missing tracker
    }

    with patch('app.services.safepay_client.httpx.AsyncClient') as mock_client_class:
        # Create a mock that properly handles async context manager
        mock_client_instance = AsyncMock()
        mock_response_obj = MagicMock()
        mock_response_obj.json = MagicMock(return_value=mock_response)
        mock_response_obj.raise_for_status = MagicMock()

        # Configure the post method to return the response
        mock_client_instance.post = AsyncMock(return_value=mock_response_obj)

        # Configure async context manager
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await safepay_client.create_payment_session(
                purchase_id=uuid4(),
                amount=100.00,
                currency="PKR"
            )

        assert exc_info.value.status_code == 500
        assert "tracker token" in str(exc_info.value.detail).lower()


@pytest.mark.asyncio
async def test_create_payment_session_http_error(safepay_client):
    """Test handling of HTTP errors from Safepay."""
    import httpx

    with patch('app.services.safepay_client.httpx.AsyncClient') as mock_client_class:
        # Create a mock that properly handles async context manager
        mock_client_instance = AsyncMock()
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 500
        mock_response_obj.raise_for_status = MagicMock(side_effect=httpx.HTTPStatusError(
            message="Server Error",
            request=MagicMock(),
            response=mock_response_obj
        ))

        # Configure the post method to return the response
        mock_client_instance.post = AsyncMock(return_value=mock_response_obj)

        # Configure async context manager
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await safepay_client.create_payment_session(
                purchase_id=uuid4(),
                amount=100.00,
                currency="PKR"
            )

        # Should raise HTTPException with 502 Bad Gateway
        assert exc_info.value.status_code == 502


@pytest.mark.asyncio
async def test_create_payment_session_timeout(safepay_client):
    """Test handling of timeout errors."""
    import httpx

    with patch('app.services.safepay_client.httpx.AsyncClient') as mock_client_class:
        # Create a mock that properly handles async context manager
        mock_client_instance = AsyncMock()

        # Configure the post method to raise TimeoutException
        mock_client_instance.post = AsyncMock(side_effect=httpx.TimeoutException("Request timeout"))

        # Configure async context manager
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await safepay_client.create_payment_session(
                purchase_id=uuid4(),
                amount=100.00,
                currency="PKR"
            )

        # Should raise HTTPException with 504 Gateway Timeout
        assert exc_info.value.status_code == 504


def test_verify_webhook_signature_valid(safepay_client):
    """Test webhook signature verification with valid SHA512 signature (VERIFIED in Stage 0)."""
    body = b'{"test": "data"}'

    # VERIFIED: Safepay uses SHA512, not SHA256
    expected_signature = hmac.new(
        "test_webhook_secret".encode('utf-8'),
        body,
        hashlib.sha512  # ✅ SHA512 verified in Stage 0
    ).hexdigest()

    result = safepay_client.verify_webhook_signature(expected_signature, body)
    assert result is True


def test_verify_webhook_signature_invalid(safepay_client):
    """Test webhook signature verification with invalid signature."""
    body = b'{"test": "data"}'
    invalid_signature = "invalid_signature_abc123"

    result = safepay_client.verify_webhook_signature(invalid_signature, body)
    assert result is False


def test_verify_webhook_signature_sha256_fails(safepay_client):
    """Test that SHA256 signature is rejected (Safepay uses SHA512)."""
    body = b'{"test": "data"}'

    # Calculate signature using WRONG algorithm (SHA256)
    wrong_signature = hmac.new(
        "test_webhook_secret".encode('utf-8'),
        body,
        hashlib.sha256  # ❌ Wrong algorithm
    ).hexdigest()

    # Should fail verification (Safepay uses SHA512)
    result = safepay_client.verify_webhook_signature(wrong_signature, body)
    assert result is False


def test_verify_webhook_signature_empty_body(safepay_client):
    """Test webhook signature verification with empty body."""
    body = b''

    expected_signature = hmac.new(
        "test_webhook_secret".encode('utf-8'),
        body,
        hashlib.sha512
    ).hexdigest()

    result = safepay_client.verify_webhook_signature(expected_signature, body)
    assert result is True
