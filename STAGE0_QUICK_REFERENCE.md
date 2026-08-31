# Stage 0 Quick Reference — Safepay Sandbox Verification

**Status:** Ready for Execution  
**Estimated Time:** 2-3 hours  
**Prerequisites:** Safepay sandbox credentials

---

## 📋 Quick Checklist

### Before You Start
- [ ] Read: `STAGE0_SAFEPAY_SANDBOX_VERIFICATION.md` (full guide)
- [ ] Read: `STAGE0_STATUS_REPORT.md` (status summary)

### Obtain Credentials (30 minutes)
- [ ] Sign up: https://getsafepay.pk/signup
- [ ] Complete sandbox KYC
- [ ] Login: https://sandbox.api.getsafepay.com/dashboard/login
- [ ] Get Public Key: Dashboard → Developers → API Keys
- [ ] Get Secret Key: Dashboard → Developers → API Keys
- [ ] Get Webhook Secret: Dashboard → Developers → Endpoints
- [ ] Copy `backend/STAGE0_CREDENTIALS_TEMPLATE.txt` to `backend/STAGE0_CREDENTIALS.txt`
- [ ] Paste credentials into `backend/STAGE0_CREDENTIALS.txt`

### Run Tests (2-3 hours)
- [ ] Test 2.1: Create Payment Session (curl or Postman)
- [ ] Test 2.2: Identify Checkout URL Method
- [ ] Test 2.3: Complete Success Payment (test card: 4456 5300 0000 1005)
- [ ] Test 2.4: Complete Failed Payment (test card: 4456 5300 0000 1013)
- [ ] Test 3.1-3.4: Webhook Testing (requires ngrok)
- [ ] Test 4.1-4.3: Additional Verification

### Document Results
- [ ] Fill in all test results in verification doc
- [ ] Capture actual webhook payloads (success and failure)
- [ ] Verify SHA512 signature algorithm
- [ ] Document checkout URL generation method
- [ ] Note any discrepancies from revised plan

---

## 🔑 Required Credentials

**You need 3 credentials from Safepay sandbox:**

```bash
# 1. Public API Key (pk_sandbox_...)
SAFEPAY_PUBLIC_KEY=pk_sandbox_[40_chars]

# 2. Secret API Key (sk_sandbox_...)
SAFEPAY_SECRET_KEY=sk_sandbox_[40_chars]

# 3. Webhook Secret (whsec_...)
SAFEPAY_WEBHOOK_SECRET=whsec_[32_chars]
```

**Where to get them:**
1. Dashboard → Developers → API Keys (for #1 and #2)
2. Dashboard → Developers → Endpoints → View Shared Secret (for #3)

---

## 🧪 Quick Test Commands

### Test 1: Create Payment
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
    "metadata": {"order_id": "test-001"}
  }'
```

### Test 2: Setup Webhook Testing (ngrok)
```bash
# Terminal 1: Start backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Start ngrok
ngrok http 8000

# Use the HTTPS URL in Safepay dashboard webhook config
```

### Test 3: Verify Signature (Python)
```python
import hmac, hashlib

webhook_secret = "whsec_YOUR_SECRET"
body_bytes = b'{"token":"evt_xxx",...}'  # Raw webhook body

signature = hmac.new(
    webhook_secret.encode('utf-8'),
    body_bytes,
    hashlib.sha512  # SHA512, not SHA256
).hexdigest()

print(f"Expected: {signature}")
print(f"Received: {received_signature}")
print(f"Match: {signature == received_signature}")
```

---

## 🎯 Key Questions to Answer

1. **Checkout URL:** Does API return it, or build manually?
2. **Payment Method:** Is it in the webhook payload?
3. **Test Cards:** What CVV/expiry values work?
4. **Signature:** Confirm SHA512 algorithm works?
5. **Webhook Structure:** Matches revised plan exactly?

---

## ⚠️ Critical Things to Document

### API Response (Test 2.1)
- [ ] Full JSON response
- [ ] Does `checkout_url` field exist?
- [ ] Tracker token format

### Checkout URL (Test 2.2)
- [ ] Working URL format
- [ ] How to construct it

### Webhook Success (Test 3.2)
- [ ] Full webhook payload
- [ ] Event type value
- [ ] State value (should be TRACKER_ENDED)
- [ ] Payment method field (present or not?)
- [ ] metadata.order_id preserved?

### Webhook Failure (Test 3.3)
- [ ] Full webhook payload
- [ ] Event type value
- [ ] State value (should be TRACKER_ENROLLED)
- [ ] Error category/code/message fields

### Signature (Test 3.4)
- [ ] Header name (X-SFPY-SIGNATURE)
- [ ] Algorithm confirmed (SHA512)
- [ ] Signature verification works

---

## 📊 Expected Results

### If Revised Plan is Correct ✅
- Endpoint: `/order/payments/v3/` ✅
- Algorithm: HMAC-SHA512 ✅
- Success state: TRACKER_ENDED ✅
- Failure state: TRACKER_ENROLLED ✅
- Webhook structure: Nested data object ✅

**Action:** Proceed to Stage 1 immediately

### If Adjustments Needed ⚠️
- Document all differences
- Update revised plan
- Get approval
- Then proceed to Stage 1

---

## 🚀 After Stage 0

### Next Steps
1. Review findings with team
2. Update Phase 6 plan if needed
3. Get user approval
4. Move credentials to `backend/.env`
5. Begin Stage 1: Environment & Configuration
6. Continue Stages 2-10

### Timeline
- Stage 0: 1 day (done)
- Stage 1-10: 6-8 days
- **Total Phase 6:** 7-9 days

---

## 📚 Full Documentation

- **Complete Guide:** `STAGE0_SAFEPAY_SANDBOX_VERIFICATION.md`
- **Status Report:** `STAGE0_STATUS_REPORT.md`
- **Credentials Template:** `backend/STAGE0_CREDENTIALS_TEMPLATE.txt`
- **Phase 6 Plan:** `docs/PHASE6_IMPLEMENTATION_PLAN_REVISED.md`

---

## 🆘 Need Help?

### Troubleshooting
- See Appendix A in full verification doc
- Common issues: Wrong endpoint, expired tokens, ngrok issues

### Safepay Support
- Dashboard: https://sandbox.api.getsafepay.com/dashboard/login
- Docs: https://safepay-docs.netlify.app
- Email: support@getsafepay.pk

---

**Quick Ref Version:** 1.0  
**Date:** 2026-08-31  
**Full Docs:** See main Stage 0 documents
