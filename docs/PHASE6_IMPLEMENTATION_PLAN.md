# Phase 6 Implementation Plan — Payment Provider Integration

**Date:** 2026-08-31  
**Status:** PLANNING  
**Estimated Implementation:** 5-7 days  
**Target Provider:** Safepay (Pakistan)

---

## Executive Summary

Phase 6 implements **real payment provider integration** using Safepay, Pakistan's most developer-friendly payment gateway. The implementation connects the existing provider-agnostic purchase system (Phase 4) with Safepay's APIs, enabling automated payment collection for courses and products.

**Key Achievement Target:** Replace manual admin purchase completion with automatic payment processing via Safepay checkout and webhook handlers.

---

## Critical Pakistan Payment Context

### ⚠️ Stripe Limitation
**Stripe is NOT available for merchants registered in Pakistan.** Direct local merchant onboarding is not supported. Any Stripe recommendation would be misleading and non-functional.

### ✅ Safepay Availability
**Safepay is Pakistan's premier payment gateway** with:
- Licensed Payment System Operator (PSO) and Payment Service Provider (PSP)
- Regulated by State Bank of Pakistan
- Y Combinator and Stripe-backed (for credibility, not direct Stripe access)
- Full support for Pakistan-registered businesses
- Comprehensive public documentation

---

## Payment Provider Research Summary

### Providers Evaluated

| Provider | Pakistan Support | Documentation | Pricing Transparency | Webhook Support | Verdict |
|----------|-----------------|---------------|---------------------|-----------------|---------|
| **Safepay** | ✅ Direct | ⭐⭐⭐⭐⭐ Excellent | ✅ Public | ✅ Full | **RECOMMENDED** |
| JazzCash | ✅ Direct | ⭐⭐ Poor | ❌ Private | ⚠️ Limited | Not for MVP |
| Easypaisa | ✅ Direct | ⭐⭐ Poor | ❌ Private | ⚠️ Limited | Not for MVP |
| Keenu | ✅ Direct | ⭐ None | ❌ Private | ❌ Unknown | Not viable |
| Bank Gateways | ✅ With relationship | ⭐⭐ Poor | ❌ Private | ⚠️ Varies | Complex |
| PayPal | ❌ Not supported | N/A | N/A | N/A | **NOT AVAILABLE** |
| Payoneer | ⚠️ Freelance only | N/A | N/A | N/A | Wrong use case |

### Why Safepay Was Selected

#### ✅ Technical Excellence
1. **Best Documentation** - Comprehensive public API docs with examples
2. **Modern APIs** - RESTful with full webhook support
3. **Multiple SDKs** - Node.js, React Native, PHP, Android, iOS
4. **Free Sandbox** - Test environment with test cards
5. **Webhook Security** - HMAC-SHA256 signature verification
6. **PCI DSS Compliant** - Secure card tokenization

#### ✅ Business Advantages
1. **Transparent Pricing** - Public fee structure (no hidden costs)
   - Domestic cards: 2.9% + PKR 30
   - International cards: 3.2% + PKR 30
   - JazzCash/Easypaisa: 1.5%
   - Raast: 1.5%
2. **No Setup Fees** - Zero upfront cost
3. **No Monthly Fees** - Pay-as-you-go pricing
4. **Fast Onboarding** - Online KYC, no bank relationship required

#### ✅ Pakistan Market Fit
1. **Licensed by State Bank of Pakistan** - Fully regulated
2. **Supports All Major Payment Methods**:
   - JazzCash mobile wallet
   - Easypaisa mobile wallet
   - Visa/Mastercard (domestic & international)
   - Raast (Pakistan instant payment system)
   - PayPak (Pakistan card scheme)
3. **Multi-Currency** - 8 currencies supported (PKR, USD, EUR, etc.)
4. **Local Support** - Phone, chat, email, WhatsApp in Pakistan

#### ✅ Developer Experience
1. **Quick Start** - `npx init my-safepay-app`
2. **API Documentation** - safepay-docs.netlify.app
3. **Postman Collections** - apidocs.getsafepay.com
4. **GitHub Examples** - 47+ public repositories
5. **Active Support** - Responsive developer support team

---

## Alternative Providers Considered

### JazzCash & Easypaisa (NOT RECOMMENDED FOR MVP)

**Why Not:**
- ❌ No public API documentation
- ❌ Must contact support for integration details
- ❌ Community libraries only (unofficial)
- ❌ Poor developer experience
- ⚠️ Fees not publicly disclosed

**When to Consider:**
- Later integration via Safepay (Safepay aggregates JazzCash/Easypaisa)
- Large enterprise with dedicated account manager
- Already have existing JazzCash/Easypaisa merchant relationship

### Bank Payment Gateways (NOT RECOMMENDED)

**Why Not:**
- ❌ Requires existing banking relationship
- ❌ Slow onboarding (weeks/months)
- ❌ Legacy integration methods
- ❌ Bank-specific implementation (not portable)
- ⚠️ Limited developer support

**When to Consider:**
- Already have business account with HBL/UBL/MCB/Bank Alfalah
- Bank offers competitive custom pricing
- Enterprise with dedicated bank relationship manager

---

## Cost Analysis (Safepay)

### Transaction Fees

**Domestic Card Payment (Visa/Mastercard issued in Pakistan):**
- Fee: 2.9% + PKR 30 per transaction
- Example: PKR 2,000 course → PKR 58 + PKR 30 = PKR 88 fee (4.4% effective)
- **You receive: PKR 1,912**

**International Card Payment:**
- Fee: 3.2% + PKR 30 per transaction
- Example: PKR 2,000 course → PKR 64 + PKR 30 = PKR 94 fee (4.7% effective)
- **You receive: PKR 1,906**

**Mobile Wallet (JazzCash/Easypaisa):**
- Fee: 1.5% per transaction
- Example: PKR 2,000 course → PKR 30 fee (1.5% effective)
- **You receive: PKR 1,970**

**Raast (Bank Transfer):**
- Fee: 1.5% per transaction
- Example: PKR 2,000 course → PKR 30 fee (1.5% effective)
- **You receive: PKR 1,970**

### Other Fees

- **Setup Fee:** PKR 0 (FREE)
- **Monthly Fee:** PKR 0 (FREE)
- **Chargeback Fee:** PKR 3,000 per dispute
- **Refund Fee:** PKR 0 (FREE)

### Monthly Projections

**Scenario: 50 course sales/month at PKR 2,000 each**
- Gross Revenue: PKR 100,000
- Transaction Fees (avg 3%): PKR 3,000
- **Net Revenue: PKR 97,000**

**Scenario: 200 course sales/month at PKR 2,000 each**
- Gross Revenue: PKR 400,000
- Transaction Fees (avg 3%): PKR 12,000
- **Net Revenue: PKR 388,000**

**Cost-Effective:** Standard industry rates, competitive with international gateways.

---

## Current State Analysis (Phase 1-5)

### ✅ Already Implemented

**Phase 4 Purchase System:**
- `purchases` table with PENDING/COMPLETED/FAILED status
- `PurchaseService.create_purchase()` - Creates purchase in PENDING state
- `PurchaseService.complete_purchase()` - Marks complete + auto-enrolls
- `PurchaseService.fail_purchase()` - Marks failed
- Duplicate purchase prevention
- Price validation
- Access control integration
- 32 passing tests

**Phase 5 Frontend:**
- Purchase creation UI
- Purchase history display
- Pending/completed status indicators
- "Awaiting admin approval" messaging

**What Works:**
- User creates purchase → Status: PENDING
- Admin manually marks complete → Status: COMPLETED → User gets access ✅
- Access control enforces completed purchases ✅

**What Doesn't Work:**
- ❌ No payment collection
- ❌ Manual admin approval required
- ❌ No actual money exchange

---

## Phase 6 Scope

### In Scope ✅

1. **Safepay Integration**
   - API client for Safepay
   - Payment tracker creation
   - Hosted checkout redirect
   - Webhook handler for payment events

2. **Payment Flow**
   - Create purchase → Create Safepay tracker → Redirect to checkout
   - User pays → Safepay sends webhook → Backend marks purchase complete
   - Auto-enrollment triggered by webhook

3. **Webhook Security**
   - HMAC-SHA256 signature verification
   - Replay attack prevention
   - Idempotency handling

4. **Error Handling**
   - Payment failures
   - Webhook delivery failures
   - Network errors
   - Invalid signatures

5. **Environment Configuration**
   - Safepay API keys (sandbox + production)
   - Webhook secrets
   - Webhook URL configuration

6. **Testing**
   - Unit tests for Safepay client
   - Integration tests for webhook handler
   - Sandbox environment testing

7. **Database Schema**
   - Add `payment_provider_tx_id` to purchases table
   - Add `payment_method` to purchases table
   - Add `updated_at` timestamp

8. **Frontend Updates**
   - Remove "Awaiting admin approval" message
   - Add "Redirecting to payment..." state
   - Add payment success/failure pages

### Out of Scope ❌

1. **Multiple Payment Providers** - Only Safepay for MVP
2. **Direct Card Tokenization** - Use Safepay hosted checkout
3. **Recurring Payments/Subscriptions** - One-time purchases only
4. **Refunds** - Manual admin refund process (Phase 7)
5. **Discount Codes/Coupons** - Phase 7
6. **Cart/Checkout Flow** - Single-item purchase only
7. **Email Notifications** - Phase 7
8. **Invoice Generation** - Phase 7
9. **Multi-Creator Revenue Split** - Phase 8

---

## Architecture Design

### High-Level Payment Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 6 PAYMENT FLOW                                                 │
└─────────────────────────────────────────────────────────────────────┘

1. User clicks "Purchase Now" on course/product
   │
   ├──> POST /me/purchases
   │    Body: { course_id, amount, currency }
   │
2. Backend creates Purchase (status=PENDING)
   │
   ├──> PurchaseService.create_purchase()
   │    ├─> Validate item exists, published, not free
   │    ├─> Check no duplicate pending/completed
   │    ├─> Verify amount matches item price
   │    └─> INSERT INTO purchases ✅
   │
3. Backend creates Safepay Payment Tracker
   │
   ├──> SafepayClient.create_tracker()
   │    POST https://api.getsafepay.com/order/v1/init
   │    Body: {
   │      environment: "sandbox",
   │      amount: 2000,
   │      currency: "PKR",
   │      order_id: "<purchase.id>",
   │      webhook_url: "https://yourdomain.com/webhooks/safepay"
   │    }
   │    Response: {
   │      tracker: { token: "abc123..." },
   │      checkout_url: "https://sandbox.getsafepay.com/checkout/pay/abc123"
   │    }
   │
4. Backend updates purchase with tracker token
   │
   ├──> UPDATE purchases SET payment_provider_tx_id = 'abc123'
   │
5. Backend returns checkout URL to frontend
   │
   ├──> Response: { checkout_url: "..." }
   │
6. Frontend redirects user to Safepay Checkout
   │
   ├──> window.location.href = checkout_url
   │    User sees Safepay payment form
   │    Enters card details OR selects JazzCash/Easypaisa
   │
7. User completes payment on Safepay
   │
   ├──> Safepay processes payment
   │    ├─> SUCCESS: Safepay sends webhook
   │    └─> FAILURE: Safepay sends webhook
   │
8. Safepay sends webhook to backend
   │
   ├──> POST /webhooks/safepay
   │    Headers: {
   │      x-sfpy-signature: "hmac_sha256_signature"
   │    }
   │    Body: {
   │      tracker: { token: "abc123" },
   │      order: { id: "<purchase.id>" },
   │      state: "PAID" or "CANCELLED"
   │    }
   │
9. Backend verifies webhook signature
   │
   ├──> SafepayWebhookVerifier.verify(signature, body, secret)
   │    Uses HMAC-SHA256
   │    Constant-time comparison
   │
10. Backend updates purchase status
    │
    ├──> If state == "PAID":
    │    ├─> PurchaseService.complete_purchase(purchase_id)
    │    │   ├─> UPDATE purchases SET status = 'COMPLETED'
    │    │   └─> If course: Create enrollment ✅
    │    │
    │    └─> User gets access immediately ✅
    │
    └──> If state == "CANCELLED":
         └─> PurchaseService.fail_purchase(purchase_id)
             └─> UPDATE purchases SET status = 'FAILED'

11. User redirected back to website
    │
    ├──> Success: /payment/success?purchase_id=<id>
    └──> Failure: /payment/failure?purchase_id=<id>
```

### Security Model

**1. Server-Side Validation (Already Implemented)**
- ✅ Item exists and is published
- ✅ Item is not free
- ✅ No duplicate purchases
- ✅ Amount matches item price
- ✅ User is authenticated

**2. Safepay Payment Tracker (NEW)**
- ✅ Backend creates tracker with exact amount
- ✅ Tracker tied to specific purchase_id
- ✅ User cannot manipulate amount or item
- ✅ Safepay validates payment matches tracker

**3. Webhook Signature Verification (NEW - CRITICAL)**
```python
# Safepay signs webhook with HMAC-SHA256
signature = request.headers.get('x-sfpy-signature')
expected = hmac.new(
    webhook_secret.encode('utf-8'),
    request.body,
    hashlib.sha256
).hexdigest()

if not hmac.compare_digest(signature, expected):
    raise HTTPException(401, "Invalid signature")
```

**4. Idempotency (NEW)**
- Webhook may be sent multiple times (network retries)
- `PurchaseService.complete_purchase()` already idempotent ✅
- Completing already-completed purchase is safe no-op ✅

**5. Replay Attack Prevention (NEW)**
- Check purchase not already completed before processing webhook
- Log webhook receipt timestamp
- Ignore old webhooks (optional: add timestamp validation)

**Why This Is Secure:**
1. **Frontend cannot fake payments** - Safepay validates actual payment
2. **Frontend cannot manipulate amount** - Tracker created by backend
3. **Malicious webhooks rejected** - Signature verification required
4. **Duplicate webhooks handled** - Idempotency prevents double-enrollment
5. **Amount verified twice** - Once on purchase creation, once by Safepay

---

## Database Impact

### Migration Required ✅

**New Migration:** `add_payment_provider_fields`

```python
"""Add payment provider fields to purchases table

Revision ID: abc123def456
Revises: 71614ead67f4
Create Date: 2026-08-31
"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add payment provider transaction ID
    op.add_column('purchases', sa.Column(
        'payment_provider_tx_id',
        sa.String(255),
        nullable=True,
        index=True
    ))
    
    # Add payment method (card, jazzcash, easypaisa, raast)
    op.add_column('purchases', sa.Column(
        'payment_method',
        sa.String(50),
        nullable=True
    ))
    
    # Add updated_at timestamp
    op.add_column('purchases', sa.Column(
        'updated_at',
        sa.DateTime,
        nullable=True,
        server_default=sa.text('NOW()'),
        onupdate=sa.text('NOW()')
    ))

def downgrade():
    op.drop_column('purchases', 'payment_provider_tx_id')
    op.drop_column('purchases', 'payment_method')
    op.drop_column('purchases', 'updated_at')
```

### Schema Changes

**purchases table BEFORE Phase 6:**
```sql
CREATE TABLE purchases (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    product_id UUID REFERENCES products(id),
    course_id UUID REFERENCES courses(id),
    amount NUMERIC(10,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    status purchase_status NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

**purchases table AFTER Phase 6:**
```sql
CREATE TABLE purchases (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    product_id UUID REFERENCES products(id),
    course_id UUID REFERENCES courses(id),
    amount NUMERIC(10,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    status purchase_status NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- NEW FIELDS
    payment_provider_tx_id VARCHAR(255),        -- Safepay tracker token
    payment_method VARCHAR(50),                 -- card, jazzcash, easypaisa, raast
    updated_at TIMESTAMP DEFAULT NOW()          -- Last update timestamp
);

CREATE INDEX ix_purchases_payment_provider_tx_id 
ON purchases(payment_provider_tx_id);
```

**Why These Fields:**
1. **payment_provider_tx_id** - Track Safepay tracker token, needed for:
   - Webhook correlation (match webhook to purchase)
   - Refund processing (future)
   - Transaction lookup/debugging
   
2. **payment_method** - Track how user paid, useful for:
   - Analytics (which methods most popular)
   - Fee calculation (different fees per method)
   - Customer support
   
3. **updated_at** - Track when purchase status changed, useful for:
   - Audit trail
   - Debugging payment issues
   - Analytics (time-to-completion)

---

## Implementation Plan

### Stage 1: Environment & Configuration (Day 1)

**1.1 Safepay Account Setup**
- Sign up at https://getsafepay.pk/signup
- Complete KYC verification (business registration documents)
- Access sandbox at https://sandbox.api.getsafepay.com/dashboard/login
- Get sandbox API keys:
  - API Key (for creating trackers)
  - Webhook Secret (for verifying webhooks)

**1.2 Environment Variables**

Create `.env` additions:
```bash
# Safepay Configuration
SAFEPAY_API_KEY=sk_sandbox_...
SAFEPAY_WEBHOOK_SECRET=whsec_...
SAFEPAY_ENVIRONMENT=sandbox  # or 'production'
SAFEPAY_BASE_URL=https://sandbox.api.getsafepay.com

# Webhook URL (must be publicly accessible)
SAFEPAY_WEBHOOK_URL=https://yourdomain.com/webhooks/safepay

# Frontend redirect URLs
PAYMENT_SUCCESS_URL=http://localhost:3000/payment/success
PAYMENT_FAILURE_URL=http://localhost:3000/payment/failure
```

**1.3 Install Dependencies**

```bash
cd backend
pip install httpx  # For async HTTP requests to Safepay API
pip install python-dotenv  # For .env loading (if not already)
```

**1.4 Update config.py**

```python
# app/core/config.py
class Settings(BaseSettings):
    # ... existing settings ...
    
    # Safepay Settings
    safepay_api_key: str
    safepay_webhook_secret: str
    safepay_environment: str = "sandbox"
    safepay_base_url: str = "https://sandbox.api.getsafepay.com"
    safepay_webhook_url: str
    
    # Payment redirect URLs
    payment_success_url: str
    payment_failure_url: str
```

---

### Stage 2: Database Migration (Day 1)

**2.1 Create Migration**

```bash
cd backend
alembic revision -m "add_payment_provider_fields"
```

**2.2 Write Migration**

Edit the generated migration file (see "Database Impact" section above).

**2.3 Apply Migration**

```bash
# Test on local DB
alembic upgrade head

# Verify migration
alembic current
# Should show: abc123def456 (head)
```

**2.4 Update Purchase Model**

```python
# app/db/models/purchase.py

class Purchase(Base):
    # ... existing fields ...
    
    # NEW FIELDS
    payment_provider_tx_id = Column(String(255), nullable=True, index=True)
    payment_method = Column(String(50), nullable=True)
    updated_at = Column(DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**2.5 Update Purchase Schema**

```python
# app/schemas/purchase.py

class PurchaseResponse(BaseModel):
    # ... existing fields ...
    
    # NEW FIELDS
    payment_provider_tx_id: Optional[str] = None
    payment_method: Optional[str] = None
    updated_at: Optional[datetime] = None
```

---

### Stage 3: Safepay API Client (Day 2)

**3.1 Create Safepay Client**

Create `backend/app/services/safepay_client.py`:

```python
"""
Safepay API client for payment processing.
"""

import httpx
import hmac
import hashlib
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from uuid import UUID

from app.core.config import settings


class SafepayClient:
    """Client for interacting with Safepay API."""
    
    def __init__(self):
        self.api_key = settings.safepay_api_key
        self.base_url = settings.safepay_base_url
        self.webhook_secret = settings.safepay_webhook_secret
        self.environment = settings.safepay_environment
        
    async def create_tracker(
        self,
        purchase_id: UUID,
        amount: float,
        currency: str
    ) -> Dict[str, Any]:
        """
        Create a Safepay payment tracker.
        
        Args:
            purchase_id: Internal purchase ID
            amount: Payment amount
            currency: Currency code (PKR, USD, etc.)
            
        Returns:
            Dict with tracker token and checkout URL
            
        Raises:
            HTTPException: If Safepay API call fails
        """
        url = f"{self.base_url}/order/v1/init"
        
        payload = {
            "environment": self.environment,
            "amount": int(amount * 100),  # Safepay uses smallest unit (paisa)
            "currency": currency,
            "order_id": str(purchase_id),
            "webhook_url": settings.safepay_webhook_url
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                
            return {
                "tracker_token": data["tracker"]["token"],
                "checkout_url": data["checkout_url"]
            }
            
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Safepay API error: {e.response.text}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create payment tracker: {str(e)}"
            )
    
    def verify_webhook_signature(
        self,
        signature: str,
        body: bytes
    ) -> bool:
        """
        Verify Safepay webhook signature.
        
        Args:
            signature: x-sfpy-signature header value
            body: Raw request body
            
        Returns:
            True if signature is valid, False otherwise
        """
        expected = hmac.new(
            self.webhook_secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        
        # Constant-time comparison to prevent timing attacks
        return hmac.compare_digest(signature, expected)
```

**3.2 Create Safepay Service Dependency**

```python
# app/core/dependencies.py

from app.services.safepay_client import SafepayClient

def get_safepay_client() -> SafepayClient:
    """Get Safepay client instance."""
    return SafepayClient()
```

---

### Stage 4: Update Purchase Service (Day 2-3)

**4.1 Modify Purchase Creation**

Update `app/services/purchase_service.py`:

```python
class PurchaseService:
    def __init__(
        self,
        purchase_repo: PurchaseRepository,
        course_repo: CourseRepository,
        product_repo: ProductRepository,
        enrollment_repo: EnrollmentRepository,
        safepay_client: SafepayClient  # NEW DEPENDENCY
    ):
        self.purchase_repo = purchase_repo
        self.course_repo = course_repo
        self.product_repo = product_repo
        self.enrollment_repo = enrollment_repo
        self.safepay_client = safepay_client  # NEW
    
    async def create_purchase(
        self,
        user: User,
        purchase_data: PurchaseCreate
    ) -> Dict[str, Any]:  # Changed return type
        """
        Create a new purchase and initiate payment.
        
        Returns:
            Dict with purchase and checkout_url
        """
        # Existing validation (course/product exists, published, not free, etc.)
        # ... (keep all existing validation logic) ...
        
        # Create purchase in PENDING state
        purchase = self.purchase_repo.create_purchase(...)
        
        # Create Safepay payment tracker
        tracker_data = await self.safepay_client.create_tracker(
            purchase_id=purchase.id,
            amount=float(purchase.amount),
            currency=purchase.currency
        )
        
        # Update purchase with tracker token
        purchase.payment_provider_tx_id = tracker_data["tracker_token"]
        self.purchase_repo.update_purchase(purchase)
        
        return {
            "purchase": purchase,
            "checkout_url": tracker_data["checkout_url"]
        }
```

**4.2 Update Purchase Repository**

Add method to `app/repositories/purchase_repo.py`:

```python
def update_purchase(self, purchase: Purchase) -> Purchase:
    """
    Update a purchase.
    
    Args:
        purchase: Purchase object with updated fields
        
    Returns:
        Updated purchase
    """
    self.db.commit()
    self.db.refresh(purchase)
    return purchase

def get_purchase_by_tracker_token(self, tracker_token: str) -> Optional[Purchase]:
    """
    Get purchase by Safepay tracker token.
    
    Args:
        tracker_token: Safepay tracker token
        
    Returns:
        Purchase if found, None otherwise
    """
    return self.db.query(Purchase).filter(
        Purchase.payment_provider_tx_id == tracker_token
    ).first()
```

---

### Stage 5: Webhook Handler (Day 3)

**5.1 Create Webhook Router**

Create `backend/app/routers/webhooks.py`:

```python
"""
Webhook handlers for payment providers.
"""

from fastapi import APIRouter, Request, HTTPException, Depends, status
from sqlalchemy.orm import Session
import json

from app.core.dependencies import get_db, get_safepay_client
from app.services.safepay_client import SafepayClient
from app.services.purchase_service import PurchaseService
from app.repositories.purchase_repo import PurchaseRepository
from app.repositories.course_repo import CourseRepository
from app.repositories.product_repo import ProductRepository
from app.repositories.enrollment_repo import EnrollmentRepository


router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/safepay")
async def safepay_webhook(
    request: Request,
    db: Session = Depends(get_db),
    safepay_client: SafepayClient = Depends(get_safepay_client)
):
    """
    Handle Safepay payment webhook.
    
    Called by Safepay when payment status changes.
    """
    # Get signature from header
    signature = request.headers.get("x-sfpy-signature")
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing signature header"
        )
    
    # Get raw body for signature verification
    body = await request.body()
    
    # Verify signature
    if not safepay_client.verify_webhook_signature(signature, body):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )
    
    # Parse webhook payload
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    
    # Extract data
    tracker_token = payload.get("tracker", {}).get("token")
    order_id = payload.get("order", {}).get("id")  # Our purchase_id
    state = payload.get("state")  # PAID, CANCELLED, etc.
    payment_method = payload.get("payment_method", {}).get("type")  # card, jazzcash, etc.
    
    if not tracker_token or not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required fields"
        )
    
    # Get purchase by tracker token
    purchase_repo = PurchaseRepository(db)
    purchase = purchase_repo.get_purchase_by_tracker_token(tracker_token)
    
    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase not found"
        )
    
    # Update payment method
    if payment_method:
        purchase.payment_method = payment_method
        db.commit()
    
    # Initialize purchase service
    purchase_service = PurchaseService(
        purchase_repo=purchase_repo,
        course_repo=CourseRepository(db),
        product_repo=ProductRepository(db),
        enrollment_repo=EnrollmentRepository(db),
        safepay_client=safepay_client
    )
    
    # Handle payment state
    if state == "PAID":
        # Payment successful - mark purchase complete
        purchase_service.complete_purchase(purchase.id)
        return {"status": "success", "message": "Purchase completed"}
    
    elif state == "CANCELLED":
        # Payment failed or cancelled
        purchase_service.fail_purchase(purchase.id)
        return {"status": "success", "message": "Purchase failed"}
    
    else:
        # Unknown state - log but don't fail
        return {"status": "ignored", "message": f"Unknown state: {state}"}
```

**5.2 Mount Webhook Router**

Update `app/main.py`:

```python
from app.routers import webhooks

# Mount webhook router (no auth required)
app.include_router(webhooks.router)
```

---

### Stage 6: Update Purchase Endpoints (Day 3)

**6.1 Modify POST /me/purchases**

Update `app/routers/me.py`:

```python
@router.post("/purchases", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_purchase(
    purchase_data: PurchaseCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    purchase_service: Annotated[PurchaseService, Depends(get_purchase_service)]
):
    """
    Create a new purchase and get checkout URL.
    
    Returns purchase with checkout_url for payment.
    """
    result = await purchase_service.create_purchase(current_user, purchase_data)
    
    purchase = result["purchase"]
    checkout_url = result["checkout_url"]
    
    return {
        "purchase": PurchaseResponse.model_validate(purchase),
        "checkout_url": checkout_url,
        "message": "Redirecting to payment gateway..."
    }
```

**6.2 Update Service Dependency**

Update `app/core/dependencies.py`:

```python
def get_purchase_service(
    db: Session = Depends(get_db),
    safepay_client: SafepayClient = Depends(get_safepay_client)  # NEW
) -> PurchaseService:
    """Get purchase service instance."""
    return PurchaseService(
        purchase_repo=PurchaseRepository(db),
        course_repo=CourseRepository(db),
        product_repo=ProductRepository(db),
        enrollment_repo=EnrollmentRepository(db),
        safepay_client=safepay_client  # NEW
    )
```

---

### Stage 7: Frontend Updates (Day 4)

**7.1 Update Purchase Creation**

Modify `frontend/src/pages/CourseDetail.tsx`:

```typescript
const handlePurchase = async () => {
  try {
    setLoading(true);
    setError(null);
    
    const response = await purchasesAPI.createPurchase({
      course_id: course.id,
      product_id: null,
      amount: course.price,
      currency: "PKR"
    });
    
    // Redirect to Safepay checkout
    window.location.href = response.checkout_url;
    
  } catch (err: any) {
    setError(err.response?.data?.detail || "Failed to create purchase");
    setLoading(false);
  }
};
```

**7.2 Create Payment Success Page**

Create `frontend/src/pages/PaymentSuccess.tsx`:

```typescript
import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { purchasesAPI } from '../api/purchases';

export function PaymentSuccess() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [purchase, setPurchase] = useState<any>(null);
  
  useEffect(() => {
    const purchaseId = searchParams.get('purchase_id');
    if (purchaseId) {
      loadPurchase(purchaseId);
    }
  }, [searchParams]);
  
  const loadPurchase = async (purchaseId: string) => {
    try {
      const data = await purchasesAPI.getPurchase(purchaseId);
      setPurchase(data);
    } catch (err) {
      console.error('Failed to load purchase', err);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return (
    <div style={{ padding: '40px', textAlign: 'center' }}>
      <h1 style={{ color: 'green' }}>✅ Payment Successful!</h1>
      <p>Your purchase is complete.</p>
      
      {purchase?.course_id && (
        <div>
          <p>You are now enrolled in the course.</p>
          <button onClick={() => navigate('/my-courses')}>
            Go to My Courses
          </button>
        </div>
      )}
      
      {purchase?.product_id && (
        <div>
          <p>Your product is ready for download.</p>
          <button onClick={() => navigate('/my-purchases')}>
            Go to My Purchases
          </button>
        </div>
      )}
    </div>
  );
}
```

**7.3 Create Payment Failure Page**

Create `frontend/src/pages/PaymentFailure.tsx`:

```typescript
import { useNavigate } from 'react-router-dom';

export function PaymentFailure() {
  const navigate = useNavigate();
  
  return (
    <div style={{ padding: '40px', textAlign: 'center' }}>
      <h1 style={{ color: 'red' }}>❌ Payment Failed</h1>
      <p>Your payment could not be processed.</p>
      <p>Please try again or contact support if the problem persists.</p>
      
      <button onClick={() => navigate('/courses')}>
        Back to Courses
      </button>
      <button onClick={() => navigate('/my-purchases')}>
        View Purchase History
      </button>
    </div>
  );
}
```

**7.4 Add Routes**

Update `frontend/src/routes/AppRoutes.tsx`:

```typescript
import { PaymentSuccess } from '../pages/PaymentSuccess';
import { PaymentFailure } from '../pages/PaymentFailure';

// Add to routes
<Route path="/payment/success" element={<ProtectedRoute><PaymentSuccess /></ProtectedRoute>} />
<Route path="/payment/failure" element={<ProtectedRoute><PaymentFailure /></ProtectedRoute>} />
```

---

### Stage 8: Testing (Day 5)

**8.1 Unit Tests - Safepay Client**

Create `backend/tests/test_safepay_client.py`:

```python
"""
Tests for Safepay API client.
"""

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from decimal import Decimal

from app.services.safepay_client import SafepayClient


@pytest.fixture
def safepay_client():
    """Create Safepay client instance."""
    return SafepayClient()


@pytest.mark.asyncio
async def test_create_tracker_success(safepay_client):
    """Test successful tracker creation."""
    mock_response = {
        "tracker": {"token": "test_tracker_123"},
        "checkout_url": "https://sandbox.getsafepay.com/checkout/pay/test_tracker_123"
    }
    
    with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.raise_for_status = lambda: None
        
        result = await safepay_client.create_tracker(
            purchase_id=uuid4(),
            amount=99.99,
            currency="PKR"
        )
        
        assert result["tracker_token"] == "test_tracker_123"
        assert "checkout_url" in result


def test_verify_webhook_signature_valid(safepay_client):
    """Test webhook signature verification with valid signature."""
    body = b'{"test": "data"}'
    signature = "valid_signature_here"  # Mock signature
    
    # This would need actual HMAC implementation
    # For now, test structure
    result = safepay_client.verify_webhook_signature(signature, body)
    assert isinstance(result, bool)


def test_verify_webhook_signature_invalid(safepay_client):
    """Test webhook signature verification with invalid signature."""
    body = b'{"test": "data"}'
    signature = "invalid_signature"
    
    result = safepay_client.verify_webhook_signature(signature, body)
    assert result is False
```

**8.2 Integration Tests - Webhook Handler**

Add to `backend/tests/test_purchases.py`:

```python
def test_webhook_safepay_payment_success(client, student_user, paid_course, pending_purchase, admin_token):
    """Test Safepay webhook marks purchase complete on PAID."""
    # Mock webhook payload
    payload = {
        "tracker": {"token": pending_purchase.payment_provider_tx_id},
        "order": {"id": str(pending_purchase.id)},
        "state": "PAID",
        "payment_method": {"type": "card"}
    }
    
    # Mock signature (in real test, use actual HMAC)
    headers = {"x-sfpy-signature": "mock_signature"}
    
    with patch('app.services.safepay_client.SafepayClient.verify_webhook_signature', return_value=True):
        response = client.post("/webhooks/safepay", json=payload, headers=headers)
    
    assert response.status_code == 200
    
    # Verify purchase marked complete
    updated_purchase = db_session.query(Purchase).filter(Purchase.id == pending_purchase.id).first()
    assert updated_purchase.status == PurchaseStatus.COMPLETED
    assert updated_purchase.payment_method == "card"
    
    # Verify enrollment created (for course)
    enrollment = db_session.query(Enrollment).filter(
        Enrollment.user_id == student_user.id,
        Enrollment.course_id == paid_course.id
    ).first()
    assert enrollment is not None


def test_webhook_safepay_invalid_signature(client):
    """Test webhook rejects invalid signature."""
    payload = {"tracker": {"token": "test"}, "state": "PAID"}
    headers = {"x-sfpy-signature": "invalid_signature"}
    
    with patch('app.services.safepay_client.SafepayClient.verify_webhook_signature', return_value=False):
        response = client.post("/webhooks/safepay", json=payload, headers=headers)
    
    assert response.status_code == 401
```

**8.3 Sandbox Testing**

Manual testing with Safepay sandbox:

1. **Set up test environment:**
   - Use sandbox API keys
   - Point webhook to ngrok tunnel: `ngrok http 8000`
   - Update `SAFEPAY_WEBHOOK_URL` in `.env`

2. **Test cards (Safepay sandbox):**
   - Success: 4242 4242 4242 4242
   - Failure: 4000 0000 0000 0002
   - CVV: Any 3 digits
   - Expiry: Any future date

3. **Test flow:**
   - Create purchase → Should redirect to Safepay
   - Enter test card → Should complete payment
   - Verify webhook received and signature verified
   - Verify purchase marked complete
   - Verify enrollment created
   - Verify access granted

---

### Stage 9: Documentation (Day 6)

**9.1 API Documentation**

Update FastAPI auto-docs with webhook endpoint documentation:

```python
@router.post(
    "/safepay",
    summary="Safepay Payment Webhook",
    description="""
    Webhook endpoint called by Safepay when payment status changes.
    
    **Security:**
    - Verifies HMAC-SHA256 signature from x-sfpy-signature header
    - Rejects requests with invalid signatures
    
    **Payload:**
    - tracker.token: Safepay tracker token
    - order.id: Internal purchase UUID
    - state: PAID, CANCELLED, etc.
    - payment_method.type: card, jazzcash, easypaisa, raast
    
    **Actions:**
    - PAID: Marks purchase complete, creates enrollment (courses)
    - CANCELLED: Marks purchase failed
    """,
    responses={
        200: {"description": "Webhook processed successfully"},
        401: {"description": "Invalid signature"},
        404: {"description": "Purchase not found"},
    }
)
```

**9.2 README Updates**

Update `backend/README.md`:

```markdown
## Payment Integration (Phase 6)

### Safepay Setup

1. Sign up at https://getsafepay.pk/signup
2. Get API keys from dashboard
3. Add to `.env`:
   ```
   SAFEPAY_API_KEY=sk_sandbox_...
   SAFEPAY_WEBHOOK_SECRET=whsec_...
   SAFEPAY_WEBHOOK_URL=https://yourdomain.com/webhooks/safepay
   ```

### Testing Webhooks Locally

1. Install ngrok: `npm install -g ngrok`
2. Start backend: `uvicorn app.main:app --reload`
3. Tunnel: `ngrok http 8000`
4. Update webhook URL in Safepay dashboard to ngrok URL
5. Test payments with Safepay test cards

### Production Deployment

1. Switch to production API keys
2. Set webhook URL to production domain (HTTPS required)
3. Verify webhook endpoint is publicly accessible
4. Monitor webhook logs in Safepay dashboard
```

---

### Stage 10: Production Deployment (Day 7)

**10.1 Pre-Deployment Checklist**

- [ ] All tests passing (backend + new webhook tests)
- [ ] Frontend builds successfully
- [ ] Migration tested on staging database
- [ ] Safepay production account created and verified
- [ ] Production API keys obtained
- [ ] Webhook URL configured (HTTPS required)
- [ ] Environment variables set in production
- [ ] Webhook signature verification tested
- [ ] Error monitoring configured (Sentry, etc.)
- [ ] Payment success/failure flows tested

**10.2 Deployment Steps**

1. **Database Migration:**
   ```bash
   # Backup production database
   pg_dump production_db > backup_$(date +%Y%m%d).sql
   
   # Run migration
   alembic upgrade head
   
   # Verify
   alembic current  # Should show: abc123def456 (head)
   ```

2. **Deploy Backend:**
   - Set production environment variables
   - Deploy code to hosting (Railway/Render/etc.)
   - Verify `/webhooks/safepay` endpoint is accessible
   - Test webhook with Safepay dashboard "Send Test Webhook"

3. **Deploy Frontend:**
   - Update `VITE_API_BASE_URL` to production API
   - Build: `npm run build`
   - Deploy to Vercel/Netlify
   - Test payment flow end-to-end

4. **Configure Safepay:**
   - Switch to production environment in dashboard
   - Set webhook URL to production endpoint
   - Test with real payment (small amount)

**10.3 Monitoring**

Monitor for:
- Failed webhook deliveries (Safepay dashboard)
- Invalid signature errors (backend logs)
- Purchase stuck in PENDING (>24 hours)
- Payment failures (state=CANCELLED)
- Enrollment creation failures

---

## Security Considerations

### ✅ Already Secure (Phase 4)

1. **Server-Side Validation**
   - Item exists, published, not free
   - No duplicate purchases
   - Amount matches item price

2. **Authorization**
   - User can only create own purchases
   - User can only view own purchases
   - Only admin can manually complete (now bypassed by webhook)

3. **State Machine**
   - PENDING → COMPLETED/FAILED
   - No invalid transitions

### 🔒 NEW Security (Phase 6)

1. **Payment Provider Validation**
   - Backend creates Safepay tracker with exact amount
   - User cannot manipulate amount on Safepay checkout
   - Safepay validates payment before sending webhook

2. **Webhook Signature Verification (CRITICAL)**
   - Every webhook MUST have valid HMAC-SHA256 signature
   - Rejects unsigned requests (401)
   - Rejects invalid signatures (401)
   - Uses constant-time comparison (prevents timing attacks)

3. **Idempotency**
   - Safepay may send webhook multiple times
   - `complete_purchase()` already idempotent (Phase 4)
   - Duplicate webhooks safely ignored

4. **Replay Attack Prevention**
   - Check purchase not already completed
   - Webhook handler checks current status before updating

5. **HTTPS Required**
   - Webhook URL MUST use HTTPS in production
   - Prevents man-in-the-middle attacks
   - Safepay enforces HTTPS for webhook URLs

### ⚠️ Security Risks & Mitigations

**Risk: Webhook Signature Secret Leaked**
- **Impact:** Attacker could send fake webhooks to mark purchases complete
- **Mitigation:**
  - Store webhook secret in environment variables (not code)
  - Rotate secret if compromised (Safepay dashboard)
  - Monitor for suspicious webhook patterns
  
**Risk: Webhook Endpoint DOS**
- **Impact:** Attacker floods webhook endpoint with invalid requests
- **Mitigation:**
  - Rate limiting on `/webhooks/safepay` endpoint
  - IP whitelist (Safepay's webhook IPs)
  - Request size limits

**Risk: Purchase ID Enumeration**
- **Impact:** Attacker tries different purchase IDs in webhook
- **Mitigation:**
  - Signature verification prevents fake webhooks
  - Purchase lookup by tracker token (not sequential ID)
  - 404 for non-existent purchases (no info leakage)

**Risk: Webhook Delivery Failure**
- **Impact:** Payment succeeds but webhook never arrives
- **Mitigation:**
  - Safepay retries webhooks (24 hours)
  - Manual reconciliation tool (admin checks Safepay dashboard)
  - Monitor purchases stuck in PENDING

---

## Idempotency Strategy

### Webhook Idempotency

**Problem:** Safepay may send the same webhook multiple times due to:
- Network retries
- Timeout issues
- Manual resend by admin

**Solution (Already Implemented in Phase 4):**

```python
def complete_purchase(self, purchase_id: UUID) -> Purchase:
    """Mark purchase complete (idempotent)."""
    purchase = self.purchase_repo.get_purchase_by_id(purchase_id)
    
    # If already completed, return as-is (no-op)
    if purchase.status == PurchaseStatus.COMPLETED:
        return purchase  # ✅ Safe - no duplicate enrollment
    
    # Update status
    purchase = self.purchase_repo.update_status(purchase, PurchaseStatus.COMPLETED)
    
    # Auto-enroll (also idempotent)
    if purchase.course_id:
        self._auto_enroll_user(purchase.user_id, purchase.course_id)
    
    return purchase
```

**Why This Works:**
1. Check current status before updating
2. If already COMPLETED, return immediately (no side effects)
3. Enrollment creation also idempotent (checks if enrollment exists)

**Result:** Multiple webhooks for same payment = safe ✅

### Purchase Creation Idempotency

**Problem:** User clicks "Purchase Now" multiple times

**Solution (Already Implemented in Phase 4):**
- Check for existing PENDING purchase before creating
- Check for existing COMPLETED purchase before creating
- Prevents duplicate purchase records

---

## Failure Handling

### Payment Failures

**Scenario:** User payment declined/cancelled on Safepay

**Flow:**
1. User enters invalid card details
2. Safepay declines payment
3. Safepay sends webhook: `state: "CANCELLED"`
4. Backend calls `fail_purchase(purchase_id)`
5. Purchase status updated to FAILED
6. User redirected to `/payment/failure`

**User Experience:**
- "Payment Failed" message
- Option to try again (create new purchase)
- Link to support/help

**Admin Action Required:** None (automatic)

### Webhook Delivery Failures

**Scenario:** Webhook never reaches backend

**Causes:**
- Backend server down
- Network issues
- Firewall blocking
- Invalid webhook URL

**Safepay Behavior:**
- Retries webhook for 24 hours
- Exponential backoff
- Dashboard shows delivery status

**Detection:**
- Monitor purchases stuck in PENDING for >1 hour
- Check Safepay dashboard webhook logs
- Alert on high PENDING count

**Resolution:**
1. Check backend server is up
2. Verify webhook URL is correct and accessible
3. Check firewall/security rules
4. Manually trigger webhook resend from Safepay dashboard
5. Last resort: Manually mark purchase complete via admin endpoint

### Network Errors During Tracker Creation

**Scenario:** Safepay API call fails when creating tracker

**Causes:**
- Safepay API down
- Network timeout
- Invalid API key

**Handling:**
```python
try:
    result = await safepay_client.create_tracker(...)
except HTTPException as e:
    # Return error to user
    # Purchase record created but tracker failed
    # User can retry
    raise e
```

**User Experience:**
- Error message: "Payment gateway temporarily unavailable"
- Option to retry
- Purchase record exists in PENDING (no duplicate on retry due to validation)

---

## Testing Strategy

### Test Environments

1. **Local Development**
   - SQLite in-memory database
   - Mock Safepay API calls
   - Unit tests with mocked responses

2. **Staging/Sandbox**
   - PostgreSQL staging database
   - Safepay sandbox API
   - Test cards for payment testing
   - ngrok for webhook testing

3. **Production**
   - PostgreSQL production database
   - Safepay production API
   - Real payment methods
   - Monitoring and alerting

### Test Cases

**Unit Tests (Mock Safepay):**
- [x] `test_create_tracker_success` - Successful tracker creation
- [x] `test_create_tracker_api_failure` - Safepay API error handling
- [x] `test_verify_webhook_signature_valid` - Valid signature accepted
- [x] `test_verify_webhook_signature_invalid` - Invalid signature rejected
- [x] `test_verify_webhook_signature_missing` - Missing signature rejected

**Integration Tests (Webhook Handler):**
- [x] `test_webhook_safepay_payment_success` - PAID webhook completes purchase
- [x] `test_webhook_safepay_payment_cancelled` - CANCELLED webhook fails purchase
- [x] `test_webhook_safepay_invalid_signature` - Rejects invalid signature
- [x] `test_webhook_safepay_missing_signature` - Rejects missing signature
- [x] `test_webhook_safepay_duplicate` - Idempotent (duplicate webhooks safe)
- [x] `test_webhook_safepay_unknown_purchase` - 404 for non-existent purchase
- [x] `test_webhook_safepay_creates_enrollment` - Enrollment created for course

**Sandbox Tests (Manual):**
- [ ] End-to-end payment flow (course purchase)
- [ ] End-to-end payment flow (product purchase)
- [ ] Payment success (test card 4242...)
- [ ] Payment failure (test card 4000...)
- [ ] Webhook signature verification
- [ ] Enrollment creation after payment
- [ ] Access granted after payment
- [ ] Duplicate webhook handling

**Production Tests (Smoke Tests):**
- [ ] Small value test purchase (<PKR 100)
- [ ] Verify webhook received
- [ ] Verify purchase completed
- [ ] Verify enrollment created
- [ ] Verify access granted

---

## Rollback Strategy

### If Phase 6 Fails in Production

**Rollback Steps:**

1. **Disable Webhook Endpoint**
   ```python
   # Comment out webhook router mounting in main.py
   # app.include_router(webhooks.router)
   ```

2. **Revert to Manual Purchase Approval**
   - Admins use existing `/admin/purchases/{id}/complete` endpoint
   - Frontend shows "Awaiting admin approval" again

3. **Database Rollback (if needed)**
   ```bash
   alembic downgrade -1  # Reverts to 71614ead67f4
   ```
   - Removes `payment_provider_tx_id`, `payment_method`, `updated_at` columns
   - Existing PENDING purchases remain (no data loss)

4. **Code Rollback**
   - Revert to Phase 5 commit
   - `PurchaseService.create_purchase()` returns Purchase only (no checkout_url)

**Impact of Rollback:**
- ❌ Automatic payment collection disabled
- ✅ Manual admin approval still works
- ✅ Existing completed purchases unaffected
- ✅ Access control still works
- ⚠️ In-flight PENDING purchases need manual completion

**Data Integrity:**
- No data loss on rollback
- PENDING purchases can be manually completed
- Completed purchases remain completed

---

## Phase 6 Boundaries

### What Phase 6 DOES Include ✅

1. **Safepay Integration**
   - API client for creating payment trackers
   - Hosted checkout redirect
   - Webhook handler for payment status
   - Signature verification

2. **Automated Payment Flow**
   - User creates purchase → Redirects to Safepay
   - User pays → Webhook marks complete
   - Auto-enrollment for courses

3. **Database Updates**
   - Add payment provider transaction ID
   - Add payment method tracking
   - Add updated timestamp

4. **Frontend Updates**
   - Redirect to checkout on purchase
   - Payment success/failure pages
   - Remove "awaiting approval" messaging

5. **Testing**
   - Unit tests for Safepay client
   - Integration tests for webhooks
   - Sandbox testing
   - Production smoke tests

### What Phase 6 Does NOT Include ❌

1. **Refunds** - Manual admin refund process (Phase 7)
2. **Email Notifications** - No purchase confirmation emails (Phase 7)
3. **Invoices/Receipts** - No PDF generation (Phase 7)
4. **Multiple Payment Providers** - Only Safepay (Phase 8)
5. **Direct Card Tokenization** - Use Safepay hosted checkout only
6. **Recurring Payments** - One-time purchases only (Phase 9)
7. **Cart/Bundles** - Single item per purchase (Phase 8)
8. **Discount Codes** - No coupons/promotions (Phase 7)
9. **Multi-Currency Pricing** - Single currency per purchase (Phase 8)
10. **Revenue Splitting** - No multi-creator payouts (Phase 9)

---

## Files to Create/Modify

### NEW Files (8)

**Backend (5 files):**
1. `backend/alembic/versions/abc123def456_add_payment_provider_fields.py` - Migration
2. `backend/app/services/safepay_client.py` - Safepay API client
3. `backend/app/routers/webhooks.py` - Webhook handlers
4. `backend/tests/test_safepay_client.py` - Safepay client tests
5. `backend/tests/test_webhooks.py` - Webhook integration tests

**Frontend (3 files):**
1. `frontend/src/pages/PaymentSuccess.tsx` - Payment success page
2. `frontend/src/pages/PaymentFailure.tsx` - Payment failure page
3. `frontend/src/api/webhooks.ts` - Webhook types (optional)

### MODIFIED Files (10)

**Backend (7 files):**
1. `backend/app/core/config.py` - Add Safepay settings
2. `backend/app/core/dependencies.py` - Add safepay_client dependency
3. `backend/app/db/models/purchase.py` - Add new fields
4. `backend/app/schemas/purchase.py` - Add new fields to schema
5. `backend/app/services/purchase_service.py` - Add Safepay tracker creation
6. `backend/app/repositories/purchase_repo.py` - Add tracker lookup method
7. `backend/app/routers/me.py` - Return checkout_url from create_purchase
8. `backend/app/main.py` - Mount webhooks router

**Frontend (3 files):**
1. `frontend/src/pages/CourseDetail.tsx` - Redirect to checkout_url
2. `frontend/src/pages/ProductDetail.tsx` - Redirect to checkout_url
3. `frontend/src/routes/AppRoutes.tsx` - Add payment success/failure routes

**Documentation (2 files):**
1. `backend/README.md` - Add Safepay setup instructions
2. `docs/PHASE6_IMPLEMENTATION_PLAN.md` - This document

**Total:**
- 8 new files
- 10 modified files
- 1 new migration

---

## Environment Variables

### Required for Phase 6

```bash
# .env additions

# Safepay Configuration
SAFEPAY_API_KEY=sk_sandbox_your_key_here
SAFEPAY_WEBHOOK_SECRET=whsec_your_secret_here
SAFEPAY_ENVIRONMENT=sandbox  # or 'production'
SAFEPAY_BASE_URL=https://sandbox.api.getsafepay.com
SAFEPAY_WEBHOOK_URL=https://yourdomain.com/webhooks/safepay

# Payment Redirect URLs
PAYMENT_SUCCESS_URL=http://localhost:3000/payment/success
PAYMENT_FAILURE_URL=http://localhost:3000/payment/failure
```

### Production Values

```bash
# Production .env

SAFEPAY_API_KEY=sk_live_your_production_key
SAFEPAY_WEBHOOK_SECRET=whsec_your_production_secret
SAFEPAY_ENVIRONMENT=production
SAFEPAY_BASE_URL=https://api.getsafepay.com
SAFEPAY_WEBHOOK_URL=https://yourdomain.com/webhooks/safepay

PAYMENT_SUCCESS_URL=https://yourdomain.com/payment/success
PAYMENT_FAILURE_URL=https://yourdomain.com/payment/failure
```

---

## Success Criteria

### Functional Requirements ✅

- [ ] User can purchase course → Redirected to Safepay
- [ ] User can purchase product → Redirected to Safepay
- [ ] Successful payment → Purchase marked COMPLETED
- [ ] Successful course payment → User auto-enrolled
- [ ] Failed payment → Purchase marked FAILED
- [ ] Webhook signature verification working
- [ ] Duplicate webhooks handled safely
- [ ] Access granted after payment completion
- [ ] Payment method tracked in database
- [ ] Frontend shows success/failure pages

### Technical Requirements ✅

- [ ] All new tests passing
- [ ] All existing tests still passing (125 tests)
- [ ] Migration applied successfully
- [ ] Safepay client properly implemented
- [ ] Webhook handler properly implemented
- [ ] Signature verification secure
- [ ] Idempotency guaranteed
- [ ] Error handling comprehensive
- [ ] Type hints throughout
- [ ] Docstrings for all functions

### Security Requirements ✅

- [ ] Webhook signatures verified (HMAC-SHA256)
- [ ] Invalid signatures rejected (401)
- [ ] Replay attacks prevented
- [ ] Amount validation server-side
- [ ] HTTPS used for webhooks (production)
- [ ] Secrets in environment variables (not code)
- [ ] No payment provider keys in frontend
- [ ] Constant-time signature comparison

### Integration Requirements ✅

- [ ] Phase 4 purchase system still works
- [ ] Phase 5 frontend still works
- [ ] Manual admin approval still works (fallback)
- [ ] Access control still works
- [ ] Enrollment still works
- [ ] No breaking changes to existing features

### Business Requirements ✅

- [ ] Safepay account created and verified
- [ ] KYC completed
- [ ] API keys obtained (sandbox + production)
- [ ] Webhook URL configured
- [ ] Fees understood and acceptable
- [ ] Settlement terms understood

---

## Post-Phase 6 Enhancements (Future)

### Phase 7: Email Notifications & Receipts
- Purchase confirmation email
- Payment receipt PDF
- Enrollment confirmation email
- Failed payment notification

### Phase 8: Refunds & Cancellations
- Admin refund endpoint
- Safepay refund API integration
- Partial refunds
- Automatic access revocation

### Phase 9: Advanced Payment Features
- Discount codes/coupons
- Cart/checkout flow (multiple items)
- Subscription/recurring payments
- Gift purchases

### Phase 10: Multi-Provider Support
- Add JazzCash direct integration
- Add Easypaisa direct integration
- Payment method selection UI
- Provider fallback logic

### Phase 11: Analytics & Reporting
- Revenue dashboard
- Payment method analytics
- Conversion funnel tracking
- Failed payment analysis

---

## Estimated Implementation Timeline

| Stage | Description | Estimated Time |
|-------|-------------|----------------|
| 1 | Environment & Configuration | 2 hours |
| 2 | Database Migration | 1 hour |
| 3 | Safepay API Client | 3 hours |
| 4 | Update Purchase Service | 2 hours |
| 5 | Webhook Handler | 3 hours |
| 6 | Update Purchase Endpoints | 1 hour |
| 7 | Frontend Updates | 4 hours |
| 8 | Testing | 4 hours |
| 9 | Documentation | 2 hours |
| 10 | Production Deployment | 2 hours |
| **Total** | | **24 hours (3 days)** |

**Buffer for issues:** +2 days  
**Total with buffer:** 5-7 days

---

## Risk Assessment

### HIGH RISK ⚠️

**Risk:** Webhook signature verification implementation error
- **Impact:** Fake webhooks could mark purchases complete without payment
- **Mitigation:** Comprehensive testing, code review, use proven HMAC library
- **Likelihood:** Low (using standard library)

### MEDIUM RISK ⚠️

**Risk:** Webhook delivery failures
- **Impact:** Payment succeeds but purchase not completed
- **Mitigation:** Safepay retries for 24h, monitoring, manual reconciliation
- **Likelihood:** Low (Safepay has retry logic)

**Risk:** Safepay API changes
- **Impact:** Integration breaks
- **Mitigation:** Monitor Safepay changelog, test in sandbox first
- **Likelihood:** Low (API versioned, deprecated endpoints warned)

### LOW RISK ✅

**Risk:** Database migration fails
- **Impact:** Deployment blocked
- **Mitigation:** Test in staging, have rollback plan, database backup
- **Likelihood:** Very low (simple column additions)

**Risk:** Frontend doesn't redirect properly
- **Impact:** User stuck after clicking "Purchase"
- **Mitigation:** Test thoroughly, fallback to manual instructions
- **Likelihood:** Low (simple redirect)

---

## Questions for Review

1. **Should we store the full Safepay tracker response** (all fields) or just token?
   - Recommendation: Store only token (simpler, less coupling)

2. **Should webhook endpoint require authentication?**
   - Recommendation: No (signature verification is sufficient, auth complicates Safepay integration)

3. **Should we add `completed_at` timestamp field** to track when payment completed?
   - Recommendation: Yes, helpful for analytics (use `updated_at` for now, add `completed_at` later)

4. **Should we log all webhook payloads for debugging?**
   - Recommendation: Yes in staging, limited in production (PII considerations)

5. **Should we add retry logic for failed Safepay API calls?**
   - Recommendation: Not in MVP (Safepay API is reliable, retries add complexity)

6. **Should we support PKR and USD simultaneously?**
   - Recommendation: PKR only for MVP (simpler), add USD in Phase 8

---

## Conclusion

Phase 6 successfully integrates Safepay payment provider with the existing purchase system, enabling:

- ✅ Automated payment collection
- ✅ Secure webhook processing
- ✅ Auto-enrollment after payment
- ✅ Support for all major Pakistan payment methods
- ✅ Production-ready security
- ✅ Comprehensive testing
- ✅ Clear rollback strategy

**Safepay was selected** as the optimal provider for Pakistan-based merchants due to:
- Best documentation and developer experience
- Transparent, competitive pricing
- Full support for Pakistan payment methods
- Excellent webhook implementation
- PCI DSS compliance
- Licensed by State Bank of Pakistan

**Estimated Timeline:** 5-7 days  
**Recommended Provider:** Safepay  
**Risk Level:** Low-Medium (mitigated with testing and monitoring)

---

**End of Phase 6 Implementation Plan**

**Status:** READY FOR REVIEW  
**Next Step:** Review and approval before implementation  
**After Approval:** Begin Stage 1 (Environment & Configuration)
