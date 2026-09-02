# Phase 6 Stage 7 Analysis: Cybersource Capture Context

## Current State

### Backend Response Structure
POST /me/purchases now returns:
```json
{
  "purchase": {...},
  "tracker_token": "track_xxx",
  "payment_provider": "safepay",
  "payment_state": "TRACKER_STARTED",
  "intent": "CYBERSOURCE",
  "mode": "payment",
  "next_actions": {
    "CYBERSOURCE": {
      "kind": "GENERATE_CAPTURE_CONTEXT"
    }
  },
  "message": "..."
}
```

### Critical Finding

The `next_actions` field contains only an INSTRUCTION ("GENERATE_CAPTURE_CONTEXT") but NOT the actual capture context JWT required by the Cybersource SDK.

## Cybersource Capture Context Requirements

According to the Cybersource Unified Checkout documentation:
1. Capture context is a signed JWT token
2. Must be generated server-side via Cybersource API
3. Used by frontend Cybersource SDK to initialize payment UI
4. Contains merchant configuration and session data

## Problem

**Safepay returns:** "You need to generate a capture context"  
**Safepay does NOT return:** The actual capture context JWT

## Possible Solutions

### Option A: Safepay Provides Capture Context Endpoint
Safepay may have an API endpoint like:
- `POST /cybersource/capture-context`
- `POST /order/payments/{tracker_id}/capture-context`

This would accept the tracker_token and return the Cybersource capture context.

**Status:** UNVERIFIED - Requires Safepay API documentation or sandbox testing

### Option B: Direct Cybersource Integration
Backend calls Cybersource API directly to generate capture context.

**Requirements:**
- Cybersource merchant credentials
- Cybersource API key
- Direct Cybersource API integration

**Status:** NO CREDENTIALS CONFIGURED - Would require additional setup

### Option C: Safepay Full Response Contains Hidden Data
The capture context might be in `full_response` under a different field name.

**Status:** NEEDS INVESTIGATION of actual Safepay API response

## Recommendation

**DO NOT GUESS OR FABRICATE IMPLEMENTATION**

Instead:
1. ✅ Update backend endpoint to return `next_actions` (DONE)
2. ✅ Create frontend that handles the response structure (IN PROGRESS)
3. ⚠️ Frontend should detect "GENERATE_CAPTURE_CONTEXT" instruction
4. ⚠️ Frontend should STOP and show message: "Payment flow requires manual configuration"
5. 📋 Document what's needed for manual verification

## Next Steps

1. Implement conservative frontend that:
   - Receives payment session data
   - Detects next_action type
   - Shows appropriate message based on what data is available
   - Does NOT fabricate Cybersource integration without capture context

2. Create manual verification checklist documenting:
   - What Safepay sandbox testing should verify
   - Whether Safepay provides capture context endpoint
   - What credentials/configuration are needed

3. Mark as "NOT VERIFIED" items requiring real Safepay/Cybersource testing

## Security Notes

- ✅ Backend properly returns payment session data
- ✅ No secrets exposed to frontend
- ✅ tracker_token is safe to send to frontend
- ✅ next_actions structure is safe information
- ⚠️ Capture context JWT (when obtained) is SAFE to send (designed for frontend)
- ❌ NEVER send Safepay secret keys or webhook secrets
