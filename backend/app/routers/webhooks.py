"""
Webhook endpoints for payment provider integrations (Phase 6).

VERIFIED Safepay webhook specifications:
- Header: X-SFPY-SIGNATURE
- Algorithm: HMAC-SHA512
- Success event: payment.succeeded, state: TRACKER_ENDED
- Failure event: payment.failed, state: TRACKER_ENROLLED
- Tracker path: data.tracker
- Order ID path: data.metadata.data.order_id
"""

from typing import Annotated
from fastapi import APIRouter, Request, Header, HTTPException, Depends, status
from sqlalchemy.orm import Session
import json
import logging

from app.db.session import get_db
from app.core.dependencies import get_safepay_client
from app.services.safepay_client import SafepayClient
from app.repositories.purchase_repo import PurchaseRepository
from app.repositories.course_repo import CourseRepository
from app.repositories.product_repo import ProductRepository
from app.repositories.enrollment_repo import EnrollmentRepository
from app.services.purchase_service import PurchaseService

router = APIRouter()
logger = logging.getLogger(__name__)


def get_purchase_service(
    db: Annotated[Session, Depends(get_db)],
    safepay_client: Annotated[SafepayClient, Depends(get_safepay_client)]
) -> PurchaseService:
    """Dependency to get purchase service instance."""
    purchase_repo = PurchaseRepository(db)
    course_repo = CourseRepository(db)
    product_repo = ProductRepository(db)
    enrollment_repo = EnrollmentRepository(db)
    return PurchaseService(
        purchase_repo,
        course_repo,
        product_repo,
        enrollment_repo,
        safepay_client
    )


@router.post("/safepay")
async def safepay_webhook(
    request: Request,
    x_sfpy_signature: Annotated[str | None, Header()] = None,
    safepay_client: SafepayClient = Depends(get_safepay_client),
    service: PurchaseService = Depends(get_purchase_service)
):
    """
    Handle Safepay webhook events.

    VERIFIED webhook structure:
    - Header: X-SFPY-SIGNATURE (HMAC-SHA512)
    - Event types: payment.succeeded, payment.failed
    - Tracker: data.tracker
    - Order ID: data.metadata.data.order_id

    Security:
    - Signature verification against RAW body
    - Idempotent processing
    - Invalid signatures rejected

    Returns:
        200: Webhook processed successfully
        400: Invalid webhook data
        401: Invalid signature
    """
    # Get raw body for signature verification
    raw_body = await request.body()

    # Verify signature
    if not x_sfpy_signature:
        logger.warning("Safepay webhook received without signature")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing webhook signature"
        )

    if not safepay_client.verify_webhook_signature(x_sfpy_signature, raw_body):
        logger.warning("Safepay webhook signature verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )

    # Parse webhook payload
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        logger.error("Failed to parse Safepay webhook payload")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )

    # Extract event type
    event_type = payload.get("event", {}).get("type")

    if not event_type:
        logger.warning("Safepay webhook missing event type")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing event type"
        )

    # Only process payment events
    if event_type not in ["payment.succeeded", "payment.failed"]:
        logger.info(f"Ignoring non-payment Safepay event: {event_type}")
        return {"status": "ignored", "event": event_type}

    # Extract data
    data = payload.get("data", {})

    # Extract tracker token (VERIFIED path: data.tracker)
    tracker = data.get("tracker")
    if not tracker:
        logger.error("Safepay webhook missing tracker")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing tracker in webhook data"
        )

    tracker_token = tracker if isinstance(tracker, str) else tracker.get("token")
    if not tracker_token:
        logger.error("Safepay webhook tracker missing token")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing tracker token"
        )

    # Extract order ID (VERIFIED path: data.metadata.data.order_id)
    metadata = data.get("metadata", {})
    order_id_str = metadata.get("order_id")

    if not order_id_str:
        logger.error("Safepay webhook missing order_id in metadata")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing order_id in metadata"
        )

    # Validate order ID format
    try:
        from uuid import UUID
        purchase_id = UUID(order_id_str)
    except (ValueError, AttributeError):
        logger.error(f"Invalid order_id format: {order_id_str}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order_id format"
        )

    # Extract payment method if present
    payment_method = data.get("payment_method")

    # Process the webhook based on event type
    try:
        if event_type == "payment.succeeded":
            result = service.process_successful_payment(
                purchase_id=purchase_id,
                tracker_token=tracker_token,
                payment_method=payment_method
            )
            logger.info(f"Successfully processed payment for purchase {purchase_id}")
            return {"status": "success", "purchase_id": str(purchase_id)}

        elif event_type == "payment.failed":
            result = service.process_failed_payment(
                purchase_id=purchase_id,
                tracker_token=tracker_token
            )
            logger.info(f"Processed failed payment for purchase {purchase_id}")
            return {"status": "success", "purchase_id": str(purchase_id)}

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing Safepay webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook"
        )
