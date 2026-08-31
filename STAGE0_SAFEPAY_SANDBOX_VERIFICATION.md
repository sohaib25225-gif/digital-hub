# Stage 0: Safepay Sandbox Verification

**Date:** 2026-08-31  
**Status:** READY FOR EXECUTION  
**Purpose:** Verify uncertain Safepay API details BEFORE implementing Phase 6  
**Estimated Time:** 0.5-1 day

---

## Overview

This document provides step-by-step instructions for **Stage 0: Sandbox Verification** of the Safepay payment API. Stage 0 MUST be completed before implementing Phase 6 production code.

**Why Stage 0 is Critical:**
- Confirms exact checkout URL generation method
- Verifies actual webhook payload structure
- Tests signature verification algorithm (SHA512)
- Confirms payment method availability in webhook
- Identifies any missing API steps
- Prevents implementing wrong assumptions

---

## Prerequisites

### Required Accounts & Access
- [ ] Safepay sandbox account created
- [ ] Sandbox credentials obtained (see Section 1 below)
- [ ] Tools installed: curl or Postman
- [ ] (Optional) ngrok for local webhook testing

### Knowledge Required
- Basic HTTP/REST API testing
- JSON structure understanding
- Base64/HMAC signature verification concepts
- Pakistan Rupee (PKR) currency format (1 PKR = 100 paisa)

---

## Section 1: Obtaining Safepay Sandbox Credentials

### Step 1.1: Sign Up for Safepay Sandbox

1. **Visit:** https://getsafepay.pk/signup
2. **Fill form:**
   - Business name: `Digital Hub Test` (or your test business name)
   - Email: Your email address
   - Phone: Your Pakistan phone number
3. **Verify email**
4. **Complete basic KYC** (sandbox usually has lighter requirements)

### Step 1.2: Access Sandbox Dashboard

1. **Login:** https://sandbox.api.getsafepay.com/dashboard/login
2. Navigate to **Developers** section
3. You should see **API Keys** tab

### Step 1.3: Obtain Required Credentials

You need THREE credentials:

**1. Public API Key (Client-Side)**
   - Format: `pk_sandbox_[40-char-alphanumeric]`
   - Example: `pk_sandbox_abc123def456ghi789jkl012mno345pqrst`
   - Location: Dashboard → Developers → API Keys
   - Usage: Sent in request body as `merchant_api_key`

**2. Secret API Key (Server-Side)**
   - Format: `sk_sandbox_[40-char-alphanumeric]`
   - Example: `sk_sandbox_xyz789uvw456rst123opq987lmn654kjihg`
   - Location: Dashboard → Developers → API Keys
   - Usage: Sent in Authorization header
   - ⚠️ **NEVER expose this in frontend or commit to Git**

**3. Webhook Secret (Server-Side)**
   - Format: `whsec_[32-char-alphanumeric]`
   - Example: `whsec_abc123def456ghi789jkl012mno34`
   - Location: Dashboard → Developers → Endpoints → View Shared Secret
   - Usage: Verify webhook signature with HMAC-SHA512
   - ⚠️ **NEVER expose this in frontend or commit to Git**

### Step 1.4: Store Credentials Securely

**For Stage 0 Testing:**
Create a temporary file (NOT committed to Git):

```bash
# backend/STAGE0_CREDENTIALS.txt (add to .gitignore)

SAFEPAY_PUBLIC_KEY=pk_sandbox_YOUR_KEY_HERE
SAFEPAY_SECRET_KEY=sk_sandbox_YOUR_KEY_HERE
SAFEPAY_WEBHOOK_SECRET=whsec_YOUR_SECRET_HERE
```

⚠️ **IMPORTANT:** Add this file to `.gitignore` immediately:
```bash
echo "STAGE0_CREDENTIALS.txt" >> backend/.gitignore
```

---

## Section 2: API Endpoint Testing

### Test 2.1: Create Payment Session

**Purpose:** Verify API endpoint, request structure, and response format

**Endpoint:** `POST https://sandbox.api.getsafepay.com/order/payments/v3/`

**Request:**
```bash
curl -X POST https://sandbox.api.getsafepay.com/order/payments/v3/ \
  -H "Authorization: Bearer sk_sandbox_YOUR_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_api_key": "pk_sandbox_YOUR_PUBLIC_KEY",
    "intent": "CYBERSOURCE",
    "mode": "payment",
    "currency": "PKR",
    "amount": 100000,
    "metadata": {
      "order_id": "test-stage0-001",
      "product_type": "course",
      "test_run": "stage0_verification"
    }
  }'
```

**Expected Response (Verify Actual Structure):**
```json
{
  "data": {
    "tracker": {
      "token": "track_abc123...",
      "state": "TRACKER_STARTED",
      "intent": "CYBERSOURCE",
      "mode": "payment"
    }
  }
}
```

**What to Document:**
- [ ] Response status code (should be 200 or 201)
- [ ] Exact response structure (paste full JSON)
- [ ] Does response include `checkout_url` field? (YES/NO)
- [ ] Tracker token format (length, prefix)
- [ ] Any additional fields not shown in revised plan
- [ ] Any errors encountered

**Document Response Here:**
```
Status Code: ___________

Full Response:
{
  // PASTE ACTUAL RESPONSE
}

checkout_url Present: [ ] YES  [ ] NO

If NO, checkout URL generation method must be determined separately.
```

---

### Test 2.2: Determine Checkout URL Generation

**Purpose:** Confirm how to generate the URL user is redirected to for payment

**Three Possible Methods (Test Each):**

#### Method A: API Returns URL in Response
If Test 2.1 response includes `checkout_url` field:
```json
{
  "data": {
    "checkout_url": "https://sandbox.getsafepay.com/checkout/...",
    "tracker": { ... }
  }
}
```
✅ **If this works:** Document the exact field path and URL format

#### Method B: Manual URL Construction
Try constructing URL manually:
```
Format: https://sandbox.getsafepay.com/checkout/pay/{tracker_token}

Example: https://sandbox.getsafepay.com/checkout/pay/track_abc123...
```

**Test:**
1. Copy tracker token from Test 2.1
2. Open browser
3. Navigate to: `https://sandbox.getsafepay.com/checkout/pay/{YOUR_TRACKER_TOKEN}`
4. Do you see payment form? (YES/NO)

#### Method C: Authentication Token + SDK
Check if additional endpoint needed:
```bash
curl -X POST https://sandbox.api.getsafepay.com/client/passport/v1/token \
  -H "Authorization: Bearer sk_sandbox_YOUR_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_api_key": "pk_sandbox_YOUR_PUBLIC_KEY"
  }'
```

**Document Findings:**
```
Working Method: [ ] A  [ ] B  [ ] C  [ ] OTHER

Exact Checkout URL Format:
_________________________________________________________________

Additional Steps Required (if any):
_________________________________________________________________

Can user directly access this URL? [ ] YES  [ ] NO

Does URL expire? [ ] YES  [ ] NO  [ ] UNKNOWN

Expiry Time (if known): ___________
```

---

### Test 2.3: Complete Test Payment (Success)

**Purpose:** Test full payment flow and observe webhook

**Steps:**

1. **Create Payment Session** (Test 2.1)
2. **Get Checkout URL** (Test 2.2)
3. **Open URL in browser**
4. **Enter Test Card (Success):**
   - Card: `4456 5300 0000 1005`
   - CVV: Try `123` (document if different required)
   - Expiry: Try `12/28` (document if different required)
   - Name: Any name
5. **Submit Payment**
6. **Observe Result:**
   - Success page shown? (YES/NO)
   - Redirect URL (if any): ___________
   - Payment confirmation message: ___________

**Document Test Card Requirements:**
```
CVV Required: [ ] YES  [ ] NO  [ ] ANY_VALUE_WORKS

Expiry Format: [ ] MM/YY  [ ] MM/YYYY  [ ] ANY_FUTURE_DATE

Name on Card Required: [ ] YES  [ ] NO

Other Required Fields:
_________________________________________________________________
```

---

### Test 2.4: Test Failed Payment

**Purpose:** Verify failed payment handling

**Steps:**

1. **Create New Payment Session**
2. **Get Checkout URL**
3. **Enter Test Card (Failure):**
   - Card: `4456 5300 0000 1013`
   - CVV: Same as Test 2.3
   - Expiry: Same as Test 2.3
4. **Submit Payment**
5. **Observe Result:**
   - Error message shown? (YES/NO)
   - Error message text: ___________
   - Does page redirect? (YES/NO)
   - Redirect URL (if any): ___________

**Document:**
```
Failure Behavior:
_________________________________________________________________

User Sees Error: [ ] YES  [ ] NO

Can User Retry: [ ] YES  [ ] NO
```

---

## Section 3: Webhook Testing

### Test 3.1: Configure Webhook URL

**Prerequisites:**
- Publicly accessible webhook endpoint (use ngrok for local testing)

**Option A: Use ngrok (Recommended for Testing)**
```bash
# Start backend locally
cd backend
uvicorn app.main:app --reload --port 8000

# In another terminal, start ngrok
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

**Option B: Use Webhook Testing Service**
- Use https://webhook.site/ or https://hookbin.com/
- Copy the unique URL

**Configure in Safepay Dashboard:**
1. Dashboard → Developers → Endpoints
2. Add Endpoint: `{YOUR_NGROK_URL}/webhooks/safepay`
3. Select Events: `payment.succeeded`, `payment.failed`
4. Save

---

### Test 3.2: Capture Webhook Payload (Success)

**Steps:**

1. **Complete Test Payment** (Test 2.3)
2. **Wait for Webhook** (usually within seconds)
3. **Capture Full Payload**

**Expected Webhook (Verify Actual Structure):**
```json
{
  "token": "evt_xxx",
  "version": "2.0.0",
  "merchant_api_key": "pk_sandbox_xxx",
  "type": "payment.succeeded",
  "endpoint": "https://yourdomain.com/webhooks/safepay",
  "data": {
    "tracker": "track_xxx",
    "intent": "CYBERSOURCE",
    "state": "TRACKER_ENDED",
    "net": 43525,
    "fee": 1475,
    "customer_email": "user@example.com",
    "amount": 45000,
    "currency": "PKR",
    "metadata": {
      "order_id": "test-stage0-001",
      "product_type": "course"
    },
    "charged_at": {
      "seconds": 1698754230,
      "nanos": 752997627
    }
  },
  "created_at": {
    "seconds": 1698754230,
    "nanos": 752997627
  }
}
```

**Document Actual Webhook:**
```
Full Webhook Payload (SUCCESS):
{
  // PASTE ACTUAL WEBHOOK
}

Header "X-SFPY-SIGNATURE" Present: [ ] YES  [ ] NO

If NO, document actual header name: ___________

Payment Method Field Present: [ ] YES  [ ] NO

If YES, field path: ___________
Value example: ___________

metadata.order_id Preserved: [ ] YES  [ ] NO

Timestamp Format: [ ] Unix (seconds)  [ ] ISO 8601  [ ] OTHER
```

---

### Test 3.3: Capture Webhook Payload (Failure)

**Steps:**

1. **Complete Failed Payment** (Test 2.4)
2. **Wait for Webhook**
3. **Capture Full Payload**

**Expected Webhook (Verify Actual Structure):**
```json
{
  "token": "evt_xxx",
  "version": "2.0.0",
  "type": "payment.failed",
  "data": {
    "tracker": "track_xxx",
    "intent": "CYBERSOURCE",
    "state": "TRACKER_ENROLLED",
    "customer_email": "user@example.com",
    "metadata": {
      "order_id": "test-stage0-001"
    },
    "category": "PAYMENT_METHOD_ERROR",
    "code": 403,
    "message": "The card you have used has been flagged as either stolen or lost.",
    "failed_at": {
      "seconds": 1698754648,
      "nanos": 494424793
    }
  }
}
```

**Document Actual Webhook:**
```
Full Webhook Payload (FAILURE):
{
  // PASTE ACTUAL WEBHOOK
}

Error Category Field: ___________
Error Code Field: ___________
Error Message Field: ___________

State Value: ___________

metadata.order_id Preserved: [ ] YES  [ ] NO
```

---

### Test 3.4: Verify Webhook Signature

**Purpose:** Confirm HMAC-SHA512 algorithm and header format

**Steps:**

1. **Capture Webhook Request:**
   - Full raw body (as bytes, no modifications)
   - Signature header value

2. **Compute Expected Signature:**

**Python Script:**
```python
import hmac
import hashlib
import json

# Your webhook secret
webhook_secret = "whsec_YOUR_SECRET_HERE"

# The raw webhook body (as received, no modifications)
body_string = '''
{
  "token": "evt_xxx",
  "version": "2.0.0",
  ...
}
'''

body_bytes = body_string.encode('utf-8')

# Compute signature with SHA512
signature_sha512 = hmac.new(
    webhook_secret.encode('utf-8'),
    body_bytes,
    hashlib.sha512
).hexdigest()

# Compute signature with SHA256 (for comparison)
signature_sha256 = hmac.new(
    webhook_secret.encode('utf-8'),
    body_bytes,
    hashlib.sha256
).hexdigest()

print("Received Signature:", "PASTE_HERE")
print("Expected (SHA512):", signature_sha512)
print("Expected (SHA256):", signature_sha256)
print("Matches SHA512:", "PASTE_HERE" == signature_sha512)
```

**Document Results:**
```
Header Name: ___________
Header Value (Signature): ___________

Computed SHA512: ___________
Computed SHA256: ___________

Matches SHA512: [ ] YES  [ ] NO
Matches SHA256: [ ] YES  [ ] NO

Algorithm Confirmed: [ ] SHA512  [ ] SHA256  [ ] OTHER
```

**⚠️ CRITICAL:** If signature does NOT match SHA512, document actual algorithm

---

## Section 4: Additional Verification

### Test 4.1: Idempotency

**Purpose:** Verify duplicate webhooks are safe

**Steps:**

1. From Safepay Dashboard → Developers → Events
2. Find recent `payment.succeeded` event
3. Click "Resend Webhook"
4. Observe if sent again

**Document:**
```
Can Webhooks be Resent: [ ] YES  [ ] NO

Duplicate Event Token: [ ] SAME  [ ] DIFFERENT

Recommendation: Always handle idempotently (check purchase status first)
```

---

### Test 4.2: Amount Format Verification

**Purpose:** Confirm paisa (100 paisa = 1 PKR) format

**Test Cases:**

| Amount (PKR) | Amount Sent | Webhook Amount | Match? |
|--------------|-------------|----------------|--------|
| 1000.00      | 100000      | _________      | Y/N    |
| 50.50        | 5050        | _________      | Y/N    |
| 0.01         | 1           | _________      | Y/N    |

**Document:**
```
Amount Format Confirmed: [ ] Paisa (x100)  [ ] OTHER

Decimal Places in Webhook: [ ] 0  [ ] 2  [ ] OTHER

Currency Always PKR: [ ] YES  [ ] NO
```

---

### Test 4.3: Tracker Token Correlation

**Purpose:** Verify tracker token links payment session to webhook

**Steps:**

1. **Create Payment Session** → Note tracker token: `track_abc123...`
2. **Complete Payment**
3. **Check Webhook** → data.tracker value: `___________`

**Document:**
```
Tracker Token in Response: ___________
Tracker Token in Webhook: ___________

Tokens Match: [ ] YES  [ ] NO

Tracker Format: [ ] track_[uuid]  [ ] track_[random]  [ ] OTHER

Tracker Length: _____ characters
```

---

## Section 5: Findings Summary

### Confirmed API Details ✅

**Endpoint:**
```
POST /order/payments/v3/
Base URL: https://sandbox.api.getsafepay.com
```

**Authentication:**
```
Authorization: Bearer {secret_key}
Body: { "merchant_api_key": "{public_key}", ... }
```

**Checkout URL Generation:**
```
Method: [ ] API Returns URL  [ ] Manual Construction  [ ] SDK Required

Format (if manual): _________________________________________________________________
```

**Webhook Structure:**
```
Event Types: payment.succeeded, payment.failed
Payload Nesting: data.tracker, data.metadata.order_id
Success State: TRACKER_ENDED
Failure State: TRACKER_ENROLLED
```

**Signature Verification:**
```
Algorithm: HMAC-SHA512
Header: X-SFPY-SIGNATURE
Verified: [ ] YES  [ ] NO
```

**Payment Method Availability:**
```
Present in Webhook: [ ] YES  [ ] NO

If YES, Field Path: _________________________________________________________________
Example Value: _________________________________________________________________
```

**Test Card Requirements:**
```
CVV: [ ] Required  [ ] Optional  Value: ___________
Expiry: [ ] Required  [ ] Optional  Format: ___________
Name: [ ] Required  [ ] Optional
```

---

### Discrepancies Found ⚠️

**List any differences from revised plan:**

1. _________________________________________________________________
2. _________________________________________________________________
3. _________________________________________________________________

**If none:** ✅ Revised plan matches actual API

---

### Recommended Plan Updates

**Required Code Changes:**

1. _________________________________________________________________
2. _________________________________________________________________
3. _________________________________________________________________

**If none:** ✅ Revised plan is accurate, proceed to Stage 1

---

## Section 6: Stage 0 Completion Checklist

### Tests Completed
- [ ] Test 2.1: Create Payment Session
- [ ] Test 2.2: Determine Checkout URL Generation
- [ ] Test 2.3: Complete Test Payment (Success)
- [ ] Test 2.4: Test Failed Payment
- [ ] Test 3.1: Configure Webhook URL
- [ ] Test 3.2: Capture Webhook Payload (Success)
- [ ] Test 3.3: Capture Webhook Payload (Failure)
- [ ] Test 3.4: Verify Webhook Signature
- [ ] Test 4.1: Idempotency
- [ ] Test 4.2: Amount Format Verification
- [ ] Test 4.3: Tracker Token Correlation

### Documentation Completed
- [ ] All test responses documented
- [ ] Webhook payloads captured
- [ ] Signature verification confirmed
- [ ] Checkout URL method identified
- [ ] Payment method availability documented
- [ ] Test card requirements documented
- [ ] Discrepancies (if any) listed
- [ ] Recommended plan updates provided

### Ready for Stage 1?
- [ ] All critical uncertainties resolved
- [ ] Revised plan confirmed accurate OR updates documented
- [ ] Credentials securely stored
- [ ] User approval received

---

## Section 7: Security Checklist

### Credentials Security
- [ ] Credentials stored in STAGE0_CREDENTIALS.txt (NOT .env yet)
- [ ] STAGE0_CREDENTIALS.txt added to .gitignore
- [ ] No credentials in screenshots or documentation
- [ ] No credentials committed to Git
- [ ] No credentials in browser history (use private/incognito mode)

### Test Data Security
- [ ] Used test cards only (no real cards)
- [ ] Test amounts small (< 100 PKR)
- [ ] Test purchases clearly marked (metadata: "test_run": "stage0")
- [ ] Webhook URLs temporary (ngrok or testing service)

---

## Section 8: Next Steps

### After Stage 0 Completion

1. **Review Findings:**
   - Present findings to team
   - Confirm any plan updates needed
   - Get approval to proceed

2. **Update Phase 6 Plan:**
   - Correct any discrepancies found
   - Update code examples with verified details
   - Mark all uncertainties as resolved

3. **Prepare for Stage 1:**
   - Move credentials from STAGE0_CREDENTIALS.txt to backend/.env
   - Update backend/.env.example with Safepay variables
   - Ensure .env is in .gitignore

4. **Begin Stage 1 Implementation:**
   - Environment & Configuration
   - Database Migration
   - SafepayClient implementation
   - (Continue with revised plan Stages 1-10)

---

## Appendix A: Troubleshooting

### Issue: Cannot Create Payment Session

**Possible Causes:**
1. Wrong API endpoint
2. Wrong secret key in Authorization header
3. Wrong public key in request body
4. Missing required fields (intent, mode, merchant_api_key)

**Solutions:**
- Verify endpoint: `/order/payments/v3/` (note the trailing slash)
- Verify credentials copied correctly (no extra spaces)
- Check Safepay dashboard for API errors
- Review Safepay documentation: https://safepay-docs.netlify.app

---

### Issue: Checkout URL Not Working

**Possible Causes:**
1. Tracker token expired
2. Wrong URL format
3. Sandbox vs production mismatch

**Solutions:**
- Create new payment session (tokens may expire)
- Try different URL formats (with/without /pay/ segment)
- Ensure using sandbox.getsafepay.com for sandbox tokens
- Check browser console for JavaScript errors

---

### Issue: No Webhook Received

**Possible Causes:**
1. Webhook URL not publicly accessible
2. ngrok tunnel expired
3. Webhook not configured in dashboard
4. Payment not actually completed

**Solutions:**
- Verify ngrok still running: `curl https://YOUR-NGROK-URL/webhooks/safepay`
- Check ngrok web interface: http://127.0.0.1:4040
- Verify webhook URL in Safepay dashboard
- Check Safepay dashboard → Events for delivery status
- Try manual webhook resend from dashboard

---

### Issue: Signature Verification Fails

**Possible Causes:**
1. Wrong webhook secret
2. Wrong algorithm (SHA256 vs SHA512)
3. Body modified before verification
4. Encoding issues (UTF-8)

**Solutions:**
- Copy webhook secret again from dashboard
- Confirm using SHA512 (not SHA256)
- Use raw body bytes (no JSON parsing before verification)
- Ensure UTF-8 encoding
- Try online HMAC calculator to verify manually

---

## Appendix B: Official Safepay Resources

**Documentation:**
- Main Docs: https://safepay-docs.netlify.app
- Webhooks: https://safepay-docs.netlify.app/developers/webhooks/
- Test Cards: https://safepay-docs.netlify.app/developers/safepay/test-cards

**Dashboard:**
- Sandbox Login: https://sandbox.api.getsafepay.com/dashboard/login
- Production Login: https://getsafepay.com/dashboard/login

**Support:**
- Email: support@getsafepay.pk
- WhatsApp: Check Safepay website for number

---

## Appendix C: Postman Collection (Optional)

If using Postman instead of curl, create collection:

**Collection: Safepay Sandbox Verification**

**Environment Variables:**
- `base_url`: `https://sandbox.api.getsafepay.com`
- `public_key`: `pk_sandbox_YOUR_KEY`
- `secret_key`: `sk_sandbox_YOUR_KEY`

**Requests:**

1. **Create Payment**
   - Method: POST
   - URL: `{{base_url}}/order/payments/v3/`
   - Headers: `Authorization: Bearer {{secret_key}}`
   - Body: (see Test 2.1)

2. **Get Auth Token** (if needed)
   - Method: POST
   - URL: `{{base_url}}/client/passport/v1/token`
   - Headers: `Authorization: Bearer {{secret_key}}`
   - Body: `{ "merchant_api_key": "{{public_key}}" }`

---

**Stage 0 Report Status:** READY FOR EXECUTION  
**Last Updated:** 2026-08-31  
**Document Version:** 1.0
