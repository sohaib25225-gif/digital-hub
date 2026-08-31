"""
Safepay API client for payment processing.

Based on Stage 0 verification results:
- API endpoint: /order/payments/v3/
- Authentication: Bearer token + public key in body
- Amount format: paisa (PKR × 100)
- Metadata structure: metadata.data.order_id
- Signature algorithm: HMAC-SHA512
- Tracker format: track_[UUID]

IMPORTANT: Checkout URL generation not yet verified - manual browser test required.
"""

import httpx
import hmac
import hashlib
from typing import Dict, Any
from fastapi import HTTPException, status
from uuid import UUID
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class SafepayClient:
    """Client for interacting with Safepay API v3."""

    def __init__(self):
        self.public_key = settings.SAFEPAY_PUBLIC_KEY
        self.secret_key = settings.SAFEPAY_SECRET_KEY
        self.base_url = settings.SAFEPAY_BASE_URL
        self.webhook_secret = settings.SAFEPAY_WEBHOOK_SECRET
        self.environment = settings.SAFEPAY_ENVIRONMENT

    async def create_payment_session(
        self,
        purchase_id: UUID,
        amount: float,
        currency: str
    ) -> Dict[str, Any]:
        """
        Create a Safepay payment session.

        VERIFIED Stage 0: Endpoint /order/payments/v3/ works correctly.

        Args:
            purchase_id: Internal purchase UUID
            amount: Payment amount in PKR (will convert to paisa)
            currency: Currency code (PKR, USD, etc.)

        Returns:
            Dict with tracker token and Safepay response data

        Raises:
            HTTPException: If Safepay API call fails
        """
        # VERIFIED: Endpoint is /order/payments/v3/
        url = f"{self.base_url}/order/payments/v3/"

        # Convert amount to paisa (VERIFIED in Stage 0: amount × 100)
        amount_paisa = int(amount * 100)

        # VERIFIED Stage 0: Request body structure
        # IMPORTANT: metadata.data.order_id is correct (NOT metadata.order_id)
        # IMPORTANT: DO NOT send product_type - it's rejected by Safepay API
        payload = {
            "merchant_api_key": self.public_key,  # REQUIRED
            "intent": "CYBERSOURCE",  # REQUIRED - card payments
            "mode": "payment",  # REQUIRED
            "currency": currency,  # REQUIRED
            "amount": amount_paisa,  # REQUIRED - in paisa
            "metadata": {
                "order_id": str(purchase_id)  # Store purchase UUID for correlation
            }
        }

        # VERIFIED: Secret key in Authorization header
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

                # VERIFIED: Response contains data.tracker.token
                tracker_data = data.get("data", {}).get("tracker", {})
                tracker_token = tracker_data.get("token")

                if not tracker_token:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Safepay response missing tracker token"
                    )

                # IMPORTANT: Stage 0 found NO checkout_url in response
                # Actual checkout URL generation method requires manual browser verification
                # DO NOT fabricate or guess the URL here

                return {
                    "tracker_token": tracker_token,
                    "tracker_state": tracker_data.get("state"),  # e.g., "TRACKER_STARTED"
                    "intent": tracker_data.get("intent"),
                    "mode": tracker_data.get("mode"),
                    "next_actions": tracker_data.get("next_actions", {}),
                    "full_response": data  # Preserve for debugging/future use
                }

        except HTTPException:
            # Re-raise HTTP exceptions that were already properly formatted
            raise
        except httpx.HTTPStatusError as e:
            # Log error but don't expose sensitive details
            logger.error(f"Safepay API error: {e.response.status_code}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Payment provider unavailable. Please try again later."
            )
        except httpx.TimeoutException:
            logger.error("Safepay API timeout")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Payment provider timeout. Please try again."
            )
        except KeyError as e:
            logger.error(f"Unexpected Safepay response structure: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected payment provider response"
            )
        except Exception as e:
            logger.error(f"Safepay client error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create payment session"
            )

    def verify_webhook_signature(
        self,
        signature: str,
        body: bytes
    ) -> bool:
        """
        Verify Safepay webhook signature using HMAC-SHA512.

        VERIFIED Stage 0: Algorithm is SHA512 (NOT SHA256)
        VERIFIED Stage 0: Header name is X-SFPY-SIGNATURE

        Args:
            signature: X-SFPY-SIGNATURE header value
            body: Raw request body bytes

        Returns:
            True if signature is valid, False otherwise
        """
        # VERIFIED: Safepay uses SHA512
        expected = hmac.new(
            self.webhook_secret.encode('utf-8'),
            body,
            hashlib.sha512  # ✅ SHA512 verified in Stage 0
        ).hexdigest()

        # Constant-time comparison to prevent timing attacks
        return hmac.compare_digest(signature, expected)
