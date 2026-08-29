# Phase 1 — Foundation Architecture Specification
## Personal Digital Products & Courses Platform (Sohaib)

**Stack:** React + TypeScript (frontend) · FastAPI + Python (backend) · Supabase PostgreSQL (database) · Supabase Storage (files) · JWT (auth, implemented in FastAPI — not Supabase Auth, since you specifically want to learn FastAPI auth) · Free-tier hosting

**Repo structure:** Monorepo (`digital-hub/frontend`, `digital-hub/backend`, `digital-hub/docs`) — simpler to manage solo, can split into two repos later if needed.

**V1 scope:** Single creator (you). Database and API designed so multi-creator upgrade later needs *migrations*, not a rewrite.

---

## 1. High-Level System Architecture

```
                        ┌─────────────────────┐
                        │   React + TS SPA     │
                        │  (Vercel/Netlify)    │
                        └──────────┬───────────┘
                                   │ REST (HTTPS, JWT in header)
                                   ▼
                        ┌─────────────────────┐
                        │   FastAPI Backend    │
                        │  (Render/Railway)    │
                        │  ┌───────────────┐   │
                        │  │  Routers      │   │
                        │  │  Services     │   │
                        │  │  Repositories │   │
                        │  └───────────────┘   │
                        └───┬─────────────┬────┘
                            │             │
                 ┌──────────▼───┐   ┌─────▼──────────┐
                 │  PostgreSQL   │   │ Supabase Storage│
                 │ (Neon/Supabase)│  │ (videos, PDFs,  │
                 │                │   │  images)        │
                 └────────────────┘   └─────────────────┘
```

**Why this shape:** Frontend and backend are fully decoupled (separate deploys, separate repos or a monorepo with two folders). This is what lets you later add a mobile app, admin app, or public API without touching the core backend — and it's the more "real-world" pattern for your portfolio compared to a framework that merges both.

---

## 2. Frontend Folder Structure

```
frontend/
├── src/
│   ├── api/                # axios instances + endpoint functions (one file per resource)
│   │   ├── client.ts
│   │   ├── courses.ts
│   │   ├── products.ts
│   │   └── auth.ts
│   ├── components/
│   │   ├── common/          # Button, Card, Modal, Loader
│   │   ├── courses/
│   │   └── products/
│   ├── pages/
│   │   ├── Home.tsx
│   │   ├── Courses.tsx
│   │   ├── CourseDetail.tsx
│   │   ├── Products.tsx
│   │   ├── ProductDetail.tsx
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   └── admin/
│   │       ├── Dashboard.tsx
│   │       ├── ManageCourses.tsx
│   │       └── ManageProducts.tsx
│   ├── context/
│   │   └── AuthContext.tsx
│   ├── hooks/
│   │   └── useAuth.ts
│   ├── types/               # shared TS interfaces mirroring backend Pydantic schemas
│   │   ├── course.ts
│   │   ├── product.ts
│   │   └── user.ts
│   ├── routes/
│   │   ├── AppRoutes.tsx
│   │   └── ProtectedRoute.tsx
│   └── App.tsx
├── .env.example
└── package.json
```

**Why:** `types/` mirroring backend schemas keeps frontend and backend contracts in sync manually now — cheap insurance against silent bugs. `ProtectedRoute.tsx` gives you one place to gate admin pages.

---

## 3. FastAPI Backend Folder Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI app init, CORS, router mounting
│   ├── core/
│   │   ├── config.py             # env var loading (pydantic-settings)
│   │   ├── security.py           # password hashing, JWT create/verify
│   │   └── dependencies.py       # get_current_user, get_current_admin
│   ├── db/
│   │   ├── base.py                # SQLAlchemy Base
│   │   ├── session.py             # engine + SessionLocal
│   │   └── models/
│   │       ├── user.py
│   │       ├── course.py
│   │       ├── section.py
│   │       ├── lesson.py
│   │       ├── product.py
│   │       └── enrollment.py
│   ├── schemas/                  # Pydantic request/response models
│   │   ├── user.py
│   │   ├── course.py
│   │   └── product.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── courses.py
│   │   ├── products.py
│   │   ├── admin.py
│   │   └── uploads.py
│   ├── services/                 # business logic, separate from routers
│   │   ├── course_service.py
│   │   └── storage_service.py    # Supabase Storage wrapper
│   └── repositories/             # DB query layer, separate from services
│       ├── course_repo.py
│       └── product_repo.py
├── alembic/                      # DB migrations
├── tests/
├── .env.example
└── requirements.txt
```

**Why routers → services → repositories:** This is a standard layered pattern. Routers stay thin (just validate + call service). Services hold business rules (e.g. "only creator can publish"). Repositories hold raw DB queries. When multi-creator arrives, you change the repository/service layer — routers barely change. This separation is also a good talking point in interviews.

---

## 4. PostgreSQL Database Schema

### Core tables

**`users`**
| Column | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| email | VARCHAR, unique | |
| hashed_password | VARCHAR | |
| full_name | VARCHAR | |
| role | ENUM('admin','student') | V1: you are the only 'admin' |
| is_active | BOOLEAN | default true |
| created_at | TIMESTAMP | |

**`creators`** *(new table, even though V1 has only one row — this is the key future-proofing move)*
| Column | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| user_id | UUID (FK → users.id) | one-to-one in V1 |
| display_name | VARCHAR | |
| bio | TEXT | |
| revenue_share_percent | NUMERIC | default 100 for V1, adjustable later |
| created_at | TIMESTAMP | |

**`courses`**
| Column | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| creator_id | UUID (FK → creators.id) | not user_id directly |
| title | VARCHAR | |
| slug | VARCHAR, unique | |
| description | TEXT | |
| thumbnail_url | VARCHAR | |
| price | NUMERIC | 0 = free |
| status | ENUM('draft','published') | |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

**`sections`**
| id | UUID (PK) |
| course_id | UUID (FK → courses.id) |
| title | VARCHAR |
| order_index | INTEGER |

**`lessons`**
| id | UUID (PK) |
| section_id | UUID (FK → sections.id) |
| title | VARCHAR |
| content_type | ENUM('video','pdf','text','quiz') |
| file_url | VARCHAR (nullable) |
| order_index | INTEGER |
| is_preview | BOOLEAN | free preview lesson |

**`products`**
| id | UUID (PK) |
| creator_id | UUID (FK → creators.id) |
| title | VARCHAR |
| slug | VARCHAR, unique |
| description | TEXT |
| price | NUMERIC |
| file_url | VARCHAR | downloadable asset |
| thumbnail_url | VARCHAR |
| status | ENUM('draft','published') |
| created_at | TIMESTAMP |

**`enrollments`** *(course access — you'll need this even for free courses, to track "purchased courses" per your own spec)*
| id | UUID (PK) |
| user_id | UUID (FK → users.id) |
| course_id | UUID (FK → courses.id) |
| enrolled_at | TIMESTAMP |
| progress_percent | NUMERIC | default 0 — simple aggregate for V1 |

> **Future evolution note:** A single percentage is fine for V1, but doesn't tell you *which* lessons were completed. When accurate progress tracking matters, add a `lesson_progress` table (`enrollment_id`, `lesson_id`, `completed_at`) and derive `progress_percent` from it instead of storing it as a raw number. Not built now.

**`purchases`** *(created now, unused by payment logic until Phase 4 — but the shape exists)*
| id | UUID (PK) |
| user_id | UUID (FK → users.id) |
| product_id | UUID (FK → products.id, nullable) |
| course_id | UUID (FK → courses.id, nullable) |
| amount | NUMERIC |
| currency | VARCHAR(3) | e.g. 'PKR', 'USD' — mandatory even now, since multi-currency is easy to plan for and hard to retrofit |
| status | ENUM('pending','completed','failed') |
| created_at | TIMESTAMP |

> **Future evolution note:** `purchases` (one row per item) is fine for V1 where a purchase is always a single course or product. Once cart/bundle support is needed, this should evolve into `orders` (one row per checkout) + `order_items` (one row per line item, referencing product_id/course_id). Not built now — just keep this in mind so the migration path is a known one, not a surprise later.

**Why `creators` as its own table instead of just using `users.role='admin'`:** This is the single most important decision in the schema. If courses/products point directly to `users.id`, "multi-creator" later means changing every foreign key across the system. If they point to `creators.id` (which just wraps a user) from day one, adding new creators later is just inserting new rows — zero schema migration on courses/products/enrollments.

**Why `purchases` exists even though Phase 4 (payments) isn't built:** Creating the table now means enrollments/downloads can be wired to check "is there a completed purchase" from day one, even if for V1 every purchase is manually marked `completed` by you (e.g. after a WhatsApp payment). This avoids retrofitting access-control logic later.

---

## 5–6. Relationships summary

```
users (1) ── (1) creators
creators (1) ── (*) courses
creators (1) ── (*) products
courses (1) ── (*) sections
sections (1) ── (*) lessons
users (1) ── (*) enrollments (*) ── (1) courses
users (1) ── (*) purchases
```

All foreign keys use `ON DELETE RESTRICT` for creator/course relationships (don't accidentally cascade-delete content) and `ON DELETE CASCADE` for sections→lessons (deleting a course section should clean up its lessons).

---

## 7. Authentication & Authorization Flow

1. `POST /auth/register` → creates `users` row, hashes password (bcrypt via passlib)
2. `POST /auth/login` → verifies password, issues JWT access token (short-lived, ~30 min) + refresh token (long-lived, stored httpOnly cookie or returned for the client to store securely)
3. Every protected request sends `Authorization: Bearer <token>`
4. `get_current_user` dependency decodes JWT, loads user from DB
5. `get_current_admin` dependency additionally checks `role == 'admin'`

**Why access + refresh tokens instead of one long-lived token:** Short-lived access tokens limit damage if a token leaks; refresh token lets the user stay logged in without re-entering a password constantly. This is standard practice and worth having in your portfolio regardless of project size.

**Refresh token storage:** Store the refresh token in an `HttpOnly`, `Secure`, `SameSite` cookie — not returned in the JSON body for the frontend to store itself. This protects it from XSS. Since frontend and backend will likely be on different domains (e.g. Vercel + Render), set `SameSite=None` and enable `credentials: true` on both the CORS config and frontend fetch calls.

---

## 8. Admin / RBAC Design

- V1 has exactly two roles: `admin` (you) and `student`.
- Admin-only routes live under `/admin/*` and use `get_current_admin`.
- **Future-ready move:** don't hardcode `role == 'admin'` checks scattered everywhere — centralize in the dependency. When multi-creator arrives, you add a `creator` role and a permission check like "is this course's `creator_id` linked to the current user's `creators.id`" rather than a blanket admin check.

---

## 9. API Endpoint Structure

```
POST   /auth/register
POST   /auth/login
POST   /auth/refresh
GET    /auth/me

GET    /courses                # public, published only
GET    /courses/{slug}
GET    /products
GET    /products/{slug}

POST   /admin/courses          # admin only
PUT    /admin/courses/{id}
DELETE /admin/courses/{id}
POST   /admin/courses/{id}/sections
POST   /admin/sections/{id}/lessons

POST   /admin/products
PUT    /admin/products/{id}
DELETE /admin/products/{id}

POST   /uploads/course-file     # returns Supabase Storage URL
POST   /uploads/product-file

GET    /me/enrollments          # student's purchased/enrolled courses
GET    /me/purchases
```

---

## 10–11. Product & Course Data Models

Already captured in section 4 — `courses → sections → lessons` is a strict one-to-many chain, each level ordered by `order_index` so you control display order without relying on creation timestamps.

---

## 12. File/Storage Architecture

- Supabase Storage buckets: `course-videos`, `course-pdfs`, `product-files`, `thumbnails`
- Backend generates a **signed upload URL**; the frontend then uploads the file **directly to Supabase Storage** using that URL. The backend never proxies the raw file bytes — this avoids server memory/timeout issues with large course videos, and the storage service key never reaches the frontend.
- For paid content, lesson/product file URLs should NOT be public — backend issues a **short-lived signed download URL** only after verifying enrollment/purchase (this hook exists from day one even if V1 has no free-vs-paid enforcement yet)

---

## 13. Future Orders/Payments Architecture (not built now)

```
Cart (frontend state) → Checkout → Create `purchases` row (status=pending)
   → Redirect to payment provider → Webhook confirms → status=completed
   → Auto-create `enrollments` row / unlock product download
```

Keeping `purchases` as its own table (section 4) means this phase only adds a payment-provider integration and a webhook handler — no schema rework.

---

## 14. Future Multi-Creator Architecture (not built now)

Because `courses`/`products` already reference `creators.id`, going multi-creator later means:
1. Allow public signup to also create a `creators` row (creator application/approval flow)
2. Add `revenue_share_percent` logic to the purchase-completion handler
3. Add a "My Courses" dashboard scoped to `creator_id = current_user's creator`
4. Add admin-level platform moderation (approve/reject published content)

No changes needed to `sections`, `lessons`, `enrollments`.

---

## 15. Security Considerations

- Passwords: bcrypt, never store plaintext
- JWT secret: strong random value, stored only in env vars
- CORS: restrict to your frontend domain only
- Rate limiting on `/auth/login` (basic in-memory or slowapi) to reduce brute-force risk
- File uploads: validate file type/size server-side, never trust frontend validation alone
- SQL injection: mitigated by using SQLAlchemy ORM/parameterized queries, never raw string-formatted SQL
- Admin routes: always re-check role server-side, never rely on frontend hiding buttons

---

## 16. Environment Variables

**Backend `.env`**
```
DATABASE_URL=
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
FRONTEND_ORIGIN=
```

**Frontend `.env`**
```
VITE_API_BASE_URL=
```

Never commit `.env` — only commit `.env.example` with empty/placeholder values.

---

## 17. Local Development Setup

1. `python -m venv venv && source venv/bin/activate` → `pip install -r requirements.txt`
2. Local Postgres via Docker (`docker run postgres:16`) or free Supabase/Neon project used directly for dev too
3. `alembic upgrade head` to apply migrations
4. `uvicorn app.main:app --reload`
5. Frontend: `npm install && npm run dev`, pointed at local backend URL

---

## 18. Recommended Git/GitHub Structure

**Monorepo** — single repo, easier to manage solo:

```
digital-hub/
├── frontend/
├── backend/
├── docs/               # architecture spec, README, notes
├── .gitignore
└── README.md
```

`.gitignore` must exclude `.env`, `venv/`, `node_modules/`, `__pycache__/`. Use feature branches (`feature/course-upload`) even solo — good habit for interviews and for when this becomes multi-contributor. Can split into `digital-hub-frontend` / `digital-hub-backend` later if ever needed.

---

## Summary — what V1 actually ships

Home · Courses list/detail · Products list/detail · Login/Register · Student "my enrollments" page · Admin dashboard to create/edit courses (with sections/lessons) and products · File upload to Supabase Storage · No payment, no multi-creator UI — but both are one layer away, not a rewrite away.
