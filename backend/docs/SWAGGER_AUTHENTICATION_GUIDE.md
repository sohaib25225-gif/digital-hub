# Swagger UI Authentication Guide

This guide explains how to properly authenticate with JWT tokens in Swagger UI to test admin endpoints.

## Common Issue: "Could not validate credentials" (401 Error)

If you're getting a **401 Unauthorized** error with the message "Could not validate credentials", the most common cause is **incorrectly formatted JWT token input in Swagger UI**.

### The Problem

Swagger UI uses HTTPBearer authentication, which automatically adds the `Bearer` prefix to your token. If you:

1. **Include quotes around the token** → ❌ WRONG
2. **Include "Bearer" prefix yourself** → ❌ WRONG  
3. **Include both** → ❌ DEFINITELY WRONG

The backend receives a malformed token and cannot decode it, resulting in a 401 error.

### The Solution

When using Swagger UI's "Authorize" button:

✅ **CORRECT**: Paste **ONLY** the raw JWT token, no quotes, no "Bearer" prefix

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

❌ **WRONG**: Don't include quotes:
```
"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

❌ **WRONG**: Don't include Bearer prefix:
```
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Expected Authentication Behavior

Understanding the difference between 401 and 403 errors:

| Status | Meaning | When It Happens |
|--------|---------|-----------------|
| **401 Unauthorized** | Authentication failed | - Token is malformed/has quotes<br>- Token is expired<br>- Token is invalid<br>- No token provided |
| **403 Forbidden** | Authenticated but not authorized | - Valid token but user is STUDENT<br>- Admin access required |

### Example Scenarios

1. **No authentication** → 401 or 403 (depending on endpoint)
2. **Student JWT token on admin endpoint** → 403 Forbidden ✅ (This means auth is working!)
3. **Quoted JWT token** → 401 Unauthorized ❌ (This means token is malformed)
4. **Admin JWT token on admin endpoint** → 200 OK ✅

## Step-by-Step: Testing Admin Endpoints

### 1. Create an Admin User

Run the script to create a test admin user:

```bash
cd backend
python scripts/create_admin_user.py
```

This creates:
- **Email**: `admin@test.com`
- **Password**: `admin123456`
- **Role**: `ADMIN`

### 2. Get an Admin JWT Token

#### Option A: Using Swagger UI

1. Navigate to http://localhost:8000/docs
2. Find the **POST /auth/login** endpoint
3. Click "Try it out"
4. Enter:
   ```json
   {
     "email": "admin@test.com",
     "password": "admin123456"
   }
   ```
5. Click "Execute"
6. Copy the `access_token` value from the response (without quotes!)

#### Option B: Using curl

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"admin123456"}'
```

Copy the `access_token` from the response.

### 3. Authorize in Swagger UI

1. Click the **"Authorize"** button (🔓 lock icon) at the top of the Swagger page
2. In the "Value" field, paste **ONLY** the JWT token
   - ✅ Do: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - ❌ Don't: `"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."`
   - ❌ Don't: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
3. Click "Authorize"
4. Click "Close"

### 4. Test Admin Endpoints

Now you can test any admin endpoint. For example:

#### Test Admin Health Check
- **GET /admin/health**
- Should return 200 OK with admin user info

#### Test Create Course
- **POST /admin/courses**
- Provide course data
- Should return 201 Created

## Troubleshooting

### Still Getting 401 After Following Steps?

1. **Check token expiration**: Access tokens expire after 30 minutes (default). Get a fresh token.
2. **Check token format**: Ensure no hidden characters or line breaks in the token.
3. **Check backend logs**: Look for JWT decode errors in the FastAPI console.

### Getting 403 Instead of 200?

1. **Check user role**: Verify the user has `role: "admin"` (not `"student"`)
2. **Run the check script**:
   ```bash
   python scripts/check_user_role.py admin@test.com
   ```

### Testing with curl (Bypass Swagger UI)

If Swagger UI isn't working, test directly with curl:

```bash
# 1. Login to get token
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"admin123456"}' \
  | jq -r '.access_token')

# 2. Test admin endpoint
curl -X GET "http://localhost:8000/admin/health" \
  -H "Authorization: Bearer $TOKEN"

# 3. Create a course
curl -X POST "http://localhost:8000/admin/courses" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Course",
    "description": "A test course",
    "category": "programming",
    "difficulty": "beginner",
    "price": 99.99,
    "currency": "USD"
  }'
```

## Authentication Flow Summary

```
1. User → POST /auth/login → Backend
2. Backend validates credentials
3. Backend generates JWT with user_id and token type
4. Backend → Returns {access_token, refresh_token, token_type} → User
5. User includes token in subsequent requests:
   Header: Authorization: Bearer <token>
6. Backend extracts token from header
7. Backend decodes JWT and validates:
   - Signature is valid
   - Token type is "access" (not "refresh")
   - Token hasn't expired
   - User exists in database
   - User is active
8. For admin endpoints, additionally check:
   - User role is "admin"
9. If all checks pass → Process request
   If auth fails → 401 Unauthorized
   If role check fails → 403 Forbidden
```

## JWT Token Structure

The JWT tokens generated by the backend have this structure:

```json
{
  "sub": "<user-uuid>",
  "type": "access",
  "exp": <expiration-timestamp>
}
```

- `sub`: User ID (UUID string)
- `type`: Either "access" or "refresh"
- `exp`: Expiration timestamp (Unix epoch)

Only "access" tokens can be used for API endpoints. "Refresh" tokens are only valid for the `/auth/refresh` endpoint.

## Related Files

- **Authentication**: `backend/app/core/security.py`
- **Dependencies**: `backend/app/core/dependencies.py`
- **User Model**: `backend/app/db/models/user.py`
- **Tests**: `backend/tests/test_auth.py`, `backend/tests/test_swagger_token_issue.py`
