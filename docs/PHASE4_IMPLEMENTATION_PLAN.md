# Phase 4 Implementation Plan — Payments & Purchase System

**Date:** 2026-08-29  
**Status:** PLANNING  
**Estimated Implementation:** 4-6 hours

---

## Executive Summary

Phase 4 implements a **provider-agnostic purchase/payment foundation** that enables users to purchase paid courses and products without integrating a real payment provider yet. The system manages the complete purchase lifecycle (pending → completed/failed), enforces access control, prevents duplicate/invalid purchases, and prepares the platform for future payment provider integration.

### Key Design Decision
The `purchases` table **already exists** in the database (created in Phase 1 migration). Phase 3 access control **already checks** for completed purchases. Phase 4's job is to **enable purchase creation and management** — the plumbing exists, we're adding the controls.

---

## Current State Analysis

### ✅ Already Implemented (Phase 1-3)

**Database:**
- `purchases` table exists with proper schema
- Indexes on `user_id`, `course_id`, `product_id`
- Status enum: PENDING, COMPLETED, FAILED
- Currency field (3-char ISO code)

**Access Control (Phase 3):**
- `AccessService.has_course_access()` - checks completed purchases for paid courses
- `AccessService.has_product_access()` - checks completed purchases for products
- `EnrollmentRepository.has_completed_course_purchase()` - query method
- `EnrollmentRepository.has_completed_product_purchase()` - query method
- `EnrollmentService.enroll_in_course()` - requires completed purchase for paid courses

**What Works:**
- IF a purchase exists with status=COMPLETED → user gets access ✅
- IF no completed purchase → user is denied access ✅

**What Doesn't Work Yet:**
- Users cannot CREATE purchases (no endpoint) ❌
- Admins cannot mark purchases complete/failed (no endpoint) ❌
- No validation on purchase creation ❌
- No duplicate prevention ❌

---

## Phase 4 Scope

### In Scope ✅
1. Purchase creation API (pending state)
2. Purchase management API (complete/fail by admin)
3. List/retrieve user's purchases
4. Business rule validation
5. Authorization checks
6. Duplicate prevention
7. State transition validation
8. Auto-enrollment on course purchase completion
9. Comprehensive test coverage
10. Provider-agnostic architecture

### Out of Scope ❌
1. Real payment provider integration (Stripe, etc.)
2. Webhook handling
3. Frontend payment UI
4. Multi-creator revenue splitting
5. Refunds/cancellations
6. Payment method storage
7. Cart/checkout flow
8. Order bundling (multiple items per purchase)

---

## Architecture Design

### Layer Structure
```
Router (API endpoints)
   ↓
Service (business logic & validation)
   ↓
Repository (database queries)
   ↓
Database (purchases table)
```

### Purchase Lifecycle
```
1. User requests purchase → Create purchase (status=PENDING)
2. Admin marks complete → Update to COMPLETED + auto-enroll (courses only)
3. OR Admin marks failed → Update to FAILED
```

### Future Payment Provider Integration
```
1. User requests purchase → Create purchase (status=PENDING)
2. Redirect to payment provider
3. Provider webhook → Update to COMPLETED/FAILED + auto-enroll
```

The architecture is designed so Step 1 remains unchanged when adding Step 2-3 later.

---

## Business Rules

### Purchase Creation
1. **Item must exist** - Course/product must be in database
2. **Item must be published** - Cannot purchase draft items
3. **Item must be paid** - Cannot purchase free courses (use enrollment instead)
4. **User must be authenticated** - No anonymous purchases
5. **No duplicate pending** - Cannot create purchase if user has pending purchase for same item
6. **No duplicate completed** - Cannot purchase if user already owns item
7. **Amount must match** - Purchase amount must equal item price
8. **Currency required** - Must specify 3-char currency code

### Purchase Completion
1. **Only admins** - Only admins can mark purchases complete/failed
2. **Must be pending** - Can only complete/fail purchases in pending state
3. **Auto-enroll courses** - Completing course purchase auto-creates enrollment
4. **Idempotent** - Completing already-completed purchase is safe (no-op)

### Purchase Retrieval
1. **Own purchases only** - Users can only view their own purchases
2. **Admin can view all** - Admins can view all purchases
3. **Include item details** - Return course/product title and details

### Access Control Integration
1. **Already works** - Phase 3 access control checks for completed purchases
2. **No changes needed** - Enrollment and download endpoints work as-is

---

## Database Schema

### No Migration Required ✅

The `purchases` table already exists with the correct schema:

```sql
CREATE TABLE purchases (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE RESTRICT,
    course_id UUID REFERENCES courses(id) ON DELETE RESTRICT,
    amount NUMERIC(10,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    status purchase_status NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_purchases_user_id ON purchases(user_id);
CREATE INDEX ix_purchases_product_id ON purchases(product_id);
CREATE INDEX ix_purchases_course_id ON purchases(course_id);
```

**Constraints:**
- Exactly one of `product_id` or `course_id` must be non-null (enforced in service layer)
- `ON DELETE CASCADE` for user (delete purchases if user deleted)
- `ON DELETE RESTRICT` for products/courses (prevent deletion if purchases exist)

---

## Implementation Plan

### 1. Schemas (app/schemas/purchase.py) — NEW FILE

**Purpose:** Pydantic models for API request/response validation

**Schemas to create:**

```python
class PurchaseCreate(BaseModel):
    """Request to create a purchase."""
    course_id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    amount: Decimal
    currency: str = Field(..., min_length=3, max_length=3)
    
    @validator('currency')
    def currency_uppercase(cls, v):
        return v.upper()
    
    @root_validator
    def check_exactly_one_item(cls, values):
        # Ensure exactly one of course_id or product_id is set
        pass

class PurchaseResponse(BaseModel):
    """Purchase response."""
    id: UUID
    user_id: UUID
    course_id: Optional[UUID]
    product_id: Optional[UUID]
    amount: Decimal
    currency: str
    status: str  # PENDING, COMPLETED, FAILED
    created_at: datetime

class PurchaseWithDetails(BaseModel):
    """Purchase with item details."""
    id: UUID
    user_id: UUID
    course_id: Optional[UUID]
    product_id: Optional[UUID]
    amount: Decimal
    currency: str
    status: str
    created_at: datetime
    item_title: str
    item_type: str  # "course" or "product"

class PurchaseStatusUpdate(BaseModel):
    """Admin request to update purchase status."""
    status: Literal["COMPLETED", "FAILED"]
```

---

### 2. Repository (app/repositories/purchase_repo.py) — NEW FILE

**Purpose:** Database query layer for purchases

**Methods to implement:**

```python
class PurchaseRepository:
    def __init__(self, db: Session):
        self.db = db
    
    # Creation
    def create_purchase(
        user_id, course_id, product_id, amount, currency
    ) -> Purchase
    
    # Retrieval
    def get_purchase_by_id(purchase_id) -> Optional[Purchase]
    def get_user_purchases(user_id) -> List[Purchase]
    def get_all_purchases(skip, limit) -> List[Purchase]  # Admin only
    
    # State checks
    def has_pending_purchase(user_id, course_id, product_id) -> bool
    def has_completed_purchase(user_id, course_id, product_id) -> bool
    
    # Updates
    def update_status(purchase, new_status) -> Purchase
    
    # Queries with joins
    def get_purchase_with_details(purchase_id) -> Optional[Purchase]
    def get_user_purchases_with_details(user_id) -> List[Purchase]
```

**Key considerations:**
- Use `.options(joinedload())` for efficient item loading
- Return Purchase model instances (not dicts)
- Let service layer handle business logic

---

### 3. Service (app/services/purchase_service.py) — NEW FILE

**Purpose:** Business logic and validation for purchases

**Methods to implement:**

```python
class PurchaseService:
    def __init__(
        self,
        purchase_repo: PurchaseRepository,
        course_repo: CourseRepository,
        product_repo: ProductRepository,
        enrollment_repo: EnrollmentRepository
    ):
        ...
    
    # Purchase creation with validation
    def create_purchase(
        user: User,
        purchase_data: PurchaseCreate
    ) -> Purchase:
        """
        Create a new purchase.
        
        Validates:
        - Item exists and is published
        - Item is not free
        - No duplicate pending/completed purchase
        - Amount matches item price
        
        Raises:
        - HTTPException 404: Item not found
        - HTTPException 400: Invalid purchase (draft, free, duplicate, price mismatch)
        """
        pass
    
    # Retrieval
    def get_user_purchases(user: User) -> List[Purchase]
    def get_purchase(user: User, purchase_id: UUID) -> Purchase:
        """Get purchase (must belong to user unless admin)."""
        pass
    
    # Admin operations
    def complete_purchase(purchase_id: UUID) -> Purchase:
        """
        Mark purchase as completed.
        
        For courses: Auto-creates enrollment if not exists.
        For products: No additional action needed.
        
        Idempotent: Safe to call on already-completed purchase.
        """
        pass
    
    def fail_purchase(purchase_id: UUID) -> Purchase:
        """Mark purchase as failed."""
        pass
```

**Validation Rules:**

**For Course Purchases:**
```python
# Get course
course = course_repo.get_course_by_id(course_id)
if not course:
    raise HTTPException(404, "Course not found")

# Must be published
if course.status != CourseStatus.PUBLISHED:
    raise HTTPException(400, "Cannot purchase draft course")

# Must be paid
if course.price == 0:
    raise HTTPException(400, "Free course - use enrollment instead")

# Check duplicates
if purchase_repo.has_pending_purchase(user.id, course_id, None):
    raise HTTPException(400, "Pending purchase already exists")
    
if purchase_repo.has_completed_purchase(user.id, course_id, None):
    raise HTTPException(400, "Course already purchased")

# Verify amount
if purchase_data.amount != course.price:
    raise HTTPException(400, "Amount does not match course price")
```

**For Product Purchases:**
```python
# Similar validation for products
# Check published, paid, no duplicates, amount matches
```

**Auto-Enrollment on Course Purchase Completion:**
```python
def complete_purchase(self, purchase_id: UUID) -> Purchase:
    purchase = self.purchase_repo.get_purchase_by_id(purchase_id)
    
    # Update status
    purchase = self.purchase_repo.update_status(
        purchase, 
        PurchaseStatus.COMPLETED
    )
    
    # If course purchase, auto-enroll
    if purchase.course_id:
        # Check if already enrolled
        existing = self.enrollment_repo.get_enrollment(
            purchase.user_id,
            purchase.course_id
        )
        
        if not existing:
            # Create enrollment
            self.enrollment_repo.create_enrollment(
                purchase.user_id,
                purchase.course_id
            )
    
    return purchase
```

---

### 4. Router (app/routers/purchases.py) — NEW FILE

**Purpose:** API endpoints for purchase management

**Endpoints to implement:**

```python
# Student endpoints (in /me router or new /purchases router)

POST /me/purchases
  Body: PurchaseCreate
  Response: PurchaseResponse (201 CREATED)
  Auth: Authenticated user
  Creates a pending purchase for course or product

GET /me/purchases
  Response: List[PurchaseWithDetails]
  Auth: Authenticated user
  Lists user's purchases with item details

GET /me/purchases/{purchase_id}
  Response: PurchaseWithDetails
  Auth: Authenticated user (must own purchase)
  Get single purchase details

# Admin endpoints

PUT /admin/purchases/{purchase_id}/complete
  Response: PurchaseResponse
  Auth: Admin only
  Marks purchase as completed + auto-enrolls (courses)

PUT /admin/purchases/{purchase_id}/fail
  Response: PurchaseResponse
  Auth: Admin only
  Marks purchase as failed

GET /admin/purchases
  Query: skip, limit
  Response: List[PurchaseWithDetails]
  Auth: Admin only
  List all purchases (paginated)
```

**Router mounting:**
- Mount purchases router in `app/main.py`
- Add to `app/routers/__init__.py`

---

### 5. Tests (tests/test_purchases.py) — NEW FILE

**Purpose:** Comprehensive test coverage for purchase system

**Test Categories:**

**Creation Tests (~12 tests):**
- ✅ Create course purchase (valid)
- ✅ Create product purchase (valid)
- ✅ Course not found (404)
- ✅ Product not found (404)
- ✅ Draft course rejected (400)
- ✅ Draft product rejected (400)
- ✅ Free course rejected (400)
- ✅ Duplicate pending purchase (400)
- ✅ Duplicate completed purchase (400)
- ✅ Amount mismatch (400)
- ✅ Must specify exactly one item (400)
- ✅ Unauthenticated rejected (401)

**Authorization Tests (~6 tests):**
- ✅ User can create own purchase
- ✅ User can view own purchases
- ✅ User cannot view others' purchases
- ✅ Admin can complete any purchase
- ✅ Student cannot complete purchase
- ✅ Unauthenticated cannot access

**State Transition Tests (~6 tests):**
- ✅ Complete pending purchase (success)
- ✅ Complete already-completed purchase (idempotent)
- ✅ Fail pending purchase (success)
- ✅ Cannot complete failed purchase
- ✅ Cannot fail completed purchase
- ✅ Status validation works

**Auto-Enrollment Tests (~4 tests):**
- ✅ Completing course purchase creates enrollment
- ✅ Completing course purchase (already enrolled) is safe
- ✅ Completing product purchase does NOT create enrollment
- ✅ Failed purchase does NOT create enrollment

**Access Integration Tests (~4 tests):**
- ✅ Completed course purchase grants access
- ✅ Pending course purchase denies access
- ✅ Completed product purchase grants download
- ✅ Pending product purchase denies download

**Edge Cases (~3 tests):**
- ✅ Currency validation (uppercase)
- ✅ Decimal precision handling
- ✅ NULL product_id XOR course_id validation

**Total: ~35 tests**

---

### 6. Schema Updates (app/schemas/__init__.py)

**Add purchase schemas to exports:**

```python
from app.schemas.purchase import (
    PurchaseCreate,
    PurchaseResponse,
    PurchaseWithDetails,
    PurchaseStatusUpdate
)
```

---

### 7. Integration Points

**Update existing files (if needed):**

1. **app/main.py** - Mount purchases router
2. **app/routers/__init__.py** - Export purchases router
3. **app/routers/me.py** - Optionally add purchase endpoints here instead

**No changes needed to:**
- Access control (already works)
- Enrollment service (already checks purchases)
- Database models (already exist)
- Migration (already created)

---

## Testing Strategy

### Unit Tests (Purchase Service)
- Test each validation rule in isolation
- Mock repository responses
- Test state transitions
- Test auto-enrollment logic

### Integration Tests (Purchase API)
- Test full request/response cycle
- Test with real database (in-memory SQLite)
- Test authorization across roles
- Test existing Phase 3 access control still works

### Regression Tests
- Run ALL existing tests (93 tests from Phase 1-3)
- Verify no breaking changes
- Verify enrollment still works
- Verify access control still works

### Test Fixtures
```python
@pytest.fixture
def paid_course(db_session, admin_user_with_creator):
    """Create a paid published course."""
    creator = db_session.query(Creator).filter(...).first()
    course = Course(
        creator_id=creator.id,
        title="Paid Course",
        slug="paid-course",
        price=Decimal("99.99"),
        status=CourseStatus.PUBLISHED
    )
    db_session.add(course)
    db_session.commit()
    return course

@pytest.fixture
def pending_purchase(db_session, student_user, paid_course):
    """Create a pending purchase."""
    purchase = Purchase(
        user_id=student_user.id,
        course_id=paid_course.id,
        amount=paid_course.price,
        currency="USD",
        status=PurchaseStatus.PENDING
    )
    db_session.add(purchase)
    db_session.commit()
    return purchase
```

---

## Security Considerations

### Authorization
✅ Users can only create purchases for themselves  
✅ Users can only view their own purchases  
✅ Users cannot complete/fail purchases  
✅ Admins can complete/fail any purchase  
✅ Admins can view all purchases  

### Validation
✅ Server-side validation only (never trust client)  
✅ Amount must match item price (prevent price manipulation)  
✅ Item must be published (prevent draft purchases)  
✅ Duplicate prevention (pending + completed checks)  
✅ State transition validation (can't complete FAILED)  

### Data Integrity
✅ Foreign key constraints (ON DELETE CASCADE/RESTRICT)  
✅ Exactly one of course_id/product_id (validated in service)  
✅ Currency uppercase normalization  
✅ Decimal precision (10,2) for amounts  

### Audit Trail
✅ created_at timestamp (when purchase initiated)  
❌ updated_at timestamp (NOT in current schema, could add later)  
❌ completed_at timestamp (NOT in current schema, could add later)  
❌ Payment provider transaction ID (future)  

---

## API Documentation

### POST /me/purchases

**Create a new purchase**

**Request:**
```json
{
  "course_id": "123e4567-e89b-12d3-a456-426614174000",
  "product_id": null,
  "amount": 99.99,
  "currency": "USD"
}
```

**Response:** `201 CREATED`
```json
{
  "id": "789e4567-e89b-12d3-a456-426614174999",
  "user_id": "456e4567-e89b-12d3-a456-426614174111",
  "course_id": "123e4567-e89b-12d3-a456-426614174000",
  "product_id": null,
  "amount": 99.99,
  "currency": "USD",
  "status": "PENDING",
  "created_at": "2026-08-29T10:00:00Z"
}
```

**Errors:**
- `400` - Invalid request (draft item, free item, duplicate, price mismatch)
- `401` - Not authenticated
- `404` - Course/product not found

---

### GET /me/purchases

**List user's purchases**

**Response:** `200 OK`
```json
[
  {
    "id": "789e4567-e89b-12d3-a456-426614174999",
    "user_id": "456e4567-e89b-12d3-a456-426614174111",
    "course_id": "123e4567-e89b-12d3-a456-426614174000",
    "product_id": null,
    "amount": 99.99,
    "currency": "USD",
    "status": "COMPLETED",
    "created_at": "2026-08-29T10:00:00Z",
    "item_title": "Python Masterclass",
    "item_type": "course"
  }
]
```

---

### PUT /admin/purchases/{purchase_id}/complete

**Mark purchase as completed (admin only)**

**Response:** `200 OK`
```json
{
  "id": "789e4567-e89b-12d3-a456-426614174999",
  "user_id": "456e4567-e89b-12d3-a456-426614174111",
  "course_id": "123e4567-e89b-12d3-a456-426614174000",
  "product_id": null,
  "amount": 99.99,
  "currency": "USD",
  "status": "COMPLETED",
  "created_at": "2026-08-29T10:00:00Z"
}
```

**Side Effects:**
- If course purchase: Creates enrollment (if not exists)
- Access control now grants course/product access

**Errors:**
- `401` - Not authenticated
- `403` - Not admin
- `404` - Purchase not found
- `400` - Invalid state transition

---

## Implementation Order

### Phase 1: Foundation (1-2 hours)
1. Create `app/schemas/purchase.py`
2. Create `app/repositories/purchase_repo.py`
3. Create `app/services/purchase_service.py`
4. Add router mounting

### Phase 2: API Endpoints (1-2 hours)
5. Create `app/routers/purchases.py` (or add to me.py)
6. Implement creation endpoint
7. Implement list/retrieve endpoints
8. Implement admin complete/fail endpoints

### Phase 3: Testing (2-3 hours)
9. Create `tests/test_purchases.py`
10. Write creation tests
11. Write authorization tests
12. Write state transition tests
13. Write auto-enrollment tests
14. Write access integration tests
15. Run full test suite (all 93+ tests)

### Phase 4: Verification (30 minutes)
16. Verify frontend builds
17. Verify no secrets in git
18. Run Alembic check
19. Create completion report

---

## Success Criteria

### Functional Requirements ✅
- [ ] Users can create purchases for published paid courses/products
- [ ] Users can view their purchase history
- [ ] Admins can mark purchases complete/failed
- [ ] Completing course purchase auto-creates enrollment
- [ ] Phase 3 access control works with purchases
- [ ] Duplicate purchases prevented
- [ ] Draft/free item purchases rejected
- [ ] Price validation enforced

### Technical Requirements ✅
- [ ] All new tests passing (~35 tests)
- [ ] All existing tests passing (93 tests)
- [ ] Router → Service → Repository architecture
- [ ] Proper authorization checks
- [ ] Comprehensive error handling
- [ ] Type hints throughout
- [ ] Docstrings for all functions

### Security Requirements ✅
- [ ] Authorization enforced server-side
- [ ] Users cannot access others' purchases
- [ ] Price manipulation prevented
- [ ] State transitions validated
- [ ] No secrets in git

### Integration Requirements ✅
- [ ] Phase 3 enrollment still works
- [ ] Phase 3 access control still works
- [ ] Frontend build passes
- [ ] No breaking changes

---

## Future Enhancements (NOT Phase 4)

### Phase 5: Real Payment Provider
- Stripe/PayPal/local payment gateway integration
- Webhook handlers for payment events
- Payment method storage
- Automatic purchase creation → redirect → webhook → completion

### Phase 6: Advanced Features
- Refunds/cancellations
- Cart/checkout flow
- Order bundling (multiple items)
- Discount codes/coupons
- Revenue splitting (multi-creator)
- Purchase history PDF export
- Email receipts
- VAT/tax calculation

---

## Risk Mitigation

### Risk: Breaking Existing Access Control
**Mitigation:** Run all 93 existing tests after implementation

### Risk: Duplicate Purchases
**Mitigation:** Database constraints + service layer checks

### Risk: Price Manipulation
**Mitigation:** Server-side price validation against database

### Risk: State Transition Bugs
**Mitigation:** Comprehensive state transition tests + validation

### Risk: Auto-Enrollment Failures
**Mitigation:** Idempotent enrollment creation + tests

---

## Questions for Review

1. Should purchase endpoints go in `/me/purchases` or separate `/purchases` router?
2. Should we add `updated_at` or `completed_at` timestamps to purchases table?
3. Should we support partial refunds in the schema now (even if not implemented)?
4. Should admin list endpoint include filters (status, user, date range)?
5. Should we add email notifications on purchase completion (Phase 4 or later)?

---

## Appendix: Current Database Schema

```sql
-- Already exists (Phase 1 migration)
CREATE TABLE purchases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE RESTRICT,
    course_id UUID REFERENCES courses(id) ON DELETE RESTRICT,
    amount NUMERIC(10,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    status purchase_status NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_purchases_user_id ON purchases(user_id);
CREATE INDEX ix_purchases_product_id ON purchases(product_id);
CREATE INDEX ix_purchases_course_id ON purchases(course_id);

CREATE TYPE purchase_status AS ENUM ('PENDING', 'COMPLETED', 'FAILED');
```

---

**End of Phase 4 Implementation Plan**

**Status:** Ready for implementation  
**Next Step:** Begin implementation following this plan  
**Estimated Time:** 4-6 hours for complete Phase 4
