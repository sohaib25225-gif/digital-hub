# Phase 5 Implementation Plan — Frontend Implementation & User Experience

**Date:** 2026-08-31  
**Status:** PLANNING  
**Estimated Implementation:** 12-16 hours

---

## Executive Summary

Phase 5 implements the **complete frontend user interface** for the Digital Hub platform. The backend (Phases 1-4) provides a fully functional API with authentication, courses, products, uploads, enrollments, and purchases. However, the frontend remains at Phase 1A placeholder state with only basic routing and stub pages.

**Phase 5 bridges this gap** by building a production-ready React + TypeScript frontend that consumes all existing backend APIs, providing users with a complete, functional digital products and courses platform.

### Why Frontend Implementation is Phase 5

**Current State Analysis:**
- ✅ Backend: 125/125 tests passing, all APIs implemented
- ✅ Auth, Courses, Products, Uploads, Enrollments, Purchases complete
- ✅ Access control, authorization, validation all working
- ❌ Frontend: Only 6 placeholder pages from Phase 1A
- ❌ No authentication UI, no course browsing, no enrollment flow
- ❌ No way for users to interact with the platform

**Strategic Decision:**
The original Phase 4 completion report suggested "Phase 5: Real Payment Provider Integration" as the next step. However, payment integration requires a working frontend to:
- Display course/product details
- Show pricing and purchase buttons
- Redirect users to payment providers
- Display purchase confirmation pages

**Therefore, Phase 5 must be Frontend Implementation before payment integration can occur.**

---

## Current State: What Exists

### Backend (100% Complete) ✅

**Phase 1 (Foundation):**
- User authentication (JWT with access + refresh tokens)
- User registration and login
- Course CRUD API (title, description, price, status, sections, lessons)
- Product CRUD API (title, description, price, file URL, status)
- Admin-only endpoints for content management
- Public endpoints for browsing published content

**Phase 2 (File Storage):**
- Supabase Storage integration
- File upload endpoints (course videos/PDFs, products, thumbnails)
- Signed URL generation for private content
- Admin-only upload authorization

**Phase 3 (Enrollment & Access Control):**
- Enrollment system (free courses can be enrolled immediately)
- Access control service (paid courses require purchase)
- Lesson access verification
- Product download verification
- Progress tracking structure

**Phase 4 (Purchases):**
- Purchase creation API (pending state)
- Admin purchase management (mark complete/failed)
- Auto-enrollment on course purchase completion
- Purchase history tracking
- Duplicate prevention and validation

### Frontend (Incomplete - Phase 1A Only) ❌

**What Exists:**
- Basic Vite + React + TypeScript setup
- React Router v6 configured
- 6 placeholder pages (Home, Courses, Products, and 3 route files)
- No API integration
- No authentication context
- No data fetching
- No forms or user interactions
- Static placeholder content only

**What's Missing:**
- Authentication UI (login, register, logout)
- Course browsing and detail pages
- Product browsing and detail pages
- Enrollment flow
- Purchase flow
- Student dashboard (my courses, my purchases)
- Admin dashboard (manage content)
- All API integration
- State management
- Error handling
- Loading states

---

## Phase 5 Objectives

### Primary Goals ✅
1. Implement complete authentication flow with JWT tokens
2. Build course browsing and detail pages consuming backend APIs
3. Build product browsing and detail pages consuming backend APIs
4. Implement enrollment system for free courses
5. Implement purchase creation for paid courses
6. Build student dashboard (my enrollments, my purchases)
7. Build admin dashboard (manage courses, manage products)
8. Integrate all backend APIs into frontend
9. Provide complete user journey from landing to course access
10. Production-ready responsive UI

### Out of Scope ❌
1. Payment provider integration (Stripe, PayPal) — **Phase 6**
2. Payment checkout flow and redirects — **Phase 6**
3. Webhook handling UI — **Phase 6**
4. Course video player implementation — **Phase 7**
5. Advanced course features (quizzes, assignments) — **Phase 7+**
6. Multi-creator onboarding UI — **Phase 8+**
7. Revenue analytics dashboard — **Phase 8+**
8. Mobile app — Future
9. Real-time notifications — Future

---

## Architecture Design

### Frontend Stack (Confirmed)

```
React 18.3.1 + TypeScript 5.6.2
├── Routing: React Router v6.28.0
├── HTTP Client: Axios 1.7.9
├── State: React Context API + Hooks
├── Styling: CSS Modules (already configured)
└── Build: Vite 5.4.21
```

**Why Context API instead of Redux:**
- Project is single-creator V1, not complex state
- Context + hooks sufficient for auth and basic state
- Avoids Redux boilerplate
- Easy to upgrade to Zustand/Redux later if needed

### Folder Structure

```
frontend/src/
├── api/                     # Backend API clients
│   ├── client.ts            # Axios instance with auth interceptors
│   ├── auth.ts              # Auth API calls
│   ├── courses.ts           # Course API calls
│   ├── products.ts          # Product API calls
│   ├── enrollments.ts       # Enrollment API calls
│   ├── purchases.ts         # Purchase API calls
│   └── admin.ts             # Admin API calls
├── components/
│   ├── common/              # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── Modal.tsx
│   │   ├── Loader.tsx
│   │   └── Navbar.tsx
│   ├── courses/             # Course-specific components
│   │   ├── CourseCard.tsx
│   │   ├── CourseList.tsx
│   │   ├── LessonList.tsx
│   │   └── EnrollButton.tsx
│   └── products/            # Product-specific components
│       ├── ProductCard.tsx
│       ├── ProductList.tsx
│       └── PurchaseButton.tsx
├── context/
│   └── AuthContext.tsx      # Authentication state and methods
├── hooks/
│   ├── useAuth.ts           # Auth hook
│   ├── useCourses.ts        # Course data fetching
│   └── useProducts.ts       # Product data fetching
├── pages/
│   ├── Home.tsx             # Landing page
│   ├── Login.tsx            # Login page
│   ├── Register.tsx         # Registration page
│   ├── Courses.tsx          # Course list (public)
│   ├── CourseDetail.tsx     # Course detail (public)
│   ├── Products.tsx         # Product list (public)
│   ├── ProductDetail.tsx    # Product detail (public)
│   ├── student/
│   │   ├── Dashboard.tsx    # Student dashboard
│   │   ├── MyCourses.tsx    # Enrolled courses
│   │   ├── MyPurchases.tsx  # Purchase history
│   │   └── CourseView.tsx   # Course content (enrolled)
│   └── admin/
│       ├── Dashboard.tsx    # Admin dashboard
│       ├── ManageCourses.tsx    # Course management
│       ├── ManageProducts.tsx   # Product management
│       ├── CreateCourse.tsx     # Create course form
│       ├── EditCourse.tsx       # Edit course form
│       ├── CreateProduct.tsx    # Create product form
│       └── EditProduct.tsx      # Edit product form
├── routes/
│   ├── AppRoutes.tsx        # Main routing configuration
│   └── ProtectedRoute.tsx   # Auth guard for protected routes
├── types/
│   ├── user.ts              # User interfaces
│   ├── course.ts            # Course interfaces
│   ├── product.ts           # Product interfaces
│   ├── enrollment.ts        # Enrollment interfaces
│   └── purchase.ts          # Purchase interfaces
├── utils/
│   ├── formatters.ts        # Date, currency formatters
│   └── validators.ts        # Form validation helpers
├── App.tsx
└── main.tsx
```

---

## Implementation Stages

### Stage 1: API Layer & Type Definitions (2-3 hours)

**Purpose:** Create the foundation for all API communication and TypeScript interfaces

#### 1.1 Type Definitions

**Files to Create:**

**`frontend/src/types/user.ts`**
```typescript
export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'student';
  is_active: boolean;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
```

**`frontend/src/types/course.ts`**
```typescript
export interface Course {
  id: string;
  creator_id: string;
  title: string;
  slug: string;
  description: string;
  price: number;
  thumbnail_url: string | null;
  status: 'draft' | 'published';
  created_at: string;
  updated_at: string;
}

export interface Section {
  id: string;
  course_id: string;
  title: string;
  order_index: number;
}

export interface Lesson {
  id: string;
  section_id: string;
  title: string;
  content_type: 'video' | 'pdf' | 'text';
  file_url: string | null;
  order_index: number;
  is_preview: boolean;
}

export interface CourseWithSections extends Course {
  sections: (Section & { lessons: Lesson[] })[];
}

export interface CourseListResponse {
  courses: Course[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
```

**`frontend/src/types/product.ts`**
```typescript
export interface Product {
  id: string;
  creator_id: string;
  title: string;
  slug: string;
  description: string;
  price: number;
  file_url: string;
  thumbnail_url: string | null;
  status: 'draft' | 'published';
  created_at: string;
}

export interface ProductListResponse {
  products: Product[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
```

**`frontend/src/types/enrollment.ts`**
```typescript
export interface Enrollment {
  id: string;
  user_id: string;
  course_id: string;
  enrolled_at: string;
  progress_percent: number;
}

export interface EnrollmentWithCourse extends Enrollment {
  course_title: string;
  course_slug: string;
  course_thumbnail: string | null;
}
```

**`frontend/src/types/purchase.ts`**
```typescript
export interface Purchase {
  id: string;
  user_id: string;
  course_id: string | null;
  product_id: string | null;
  amount: number;
  currency: string;
  status: 'pending' | 'completed' | 'failed';
  created_at: string;
}

export interface PurchaseWithDetails extends Purchase {
  item_title: string;
  item_type: 'course' | 'product';
}

export interface CreatePurchaseRequest {
  course_id?: string;
  product_id?: string;
  amount: number;
  currency: string;
}
```

#### 1.2 Axios Client Setup

**`frontend/src/api/client.ts`**
```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: Add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: Handle 401 (refresh token or logout)
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and not already retried, try refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          throw new Error('No refresh token');
        }

        const { data } = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);

        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
```

#### 1.3 API Modules

**`frontend/src/api/auth.ts`**
```typescript
import { apiClient } from './client';
import { LoginRequest, RegisterRequest, AuthResponse, User } from '../types/user';

export const authAPI = {
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const response = await apiClient.post('/auth/login', credentials);
    return response.data;
  },

  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const response = await apiClient.post('/auth/register', data);
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};
```

**`frontend/src/api/courses.ts`**
```typescript
import { apiClient } from './client';
import { CourseListResponse, CourseWithSections } from '../types/course';

export const coursesAPI = {
  getPublishedCourses: async (page = 1, pageSize = 20): Promise<CourseListResponse> => {
    const response = await apiClient.get('/courses', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  getCourseBySlug: async (slug: string): Promise<CourseWithSections> => {
    const response = await apiClient.get(`/courses/${slug}`);
    return response.data;
  },
};
```

**`frontend/src/api/products.ts`**
```typescript
import { apiClient } from './client';
import { ProductListResponse, Product } from '../types/product';

export const productsAPI = {
  getPublishedProducts: async (page = 1, pageSize = 20): Promise<ProductListResponse> => {
    const response = await apiClient.get('/products', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  getProductBySlug: async (slug: string): Promise<Product> => {
    const response = await apiClient.get(`/products/${slug}`);
    return response.data;
  },
};
```

**`frontend/src/api/enrollments.ts`**
```typescript
import { apiClient } from './client';
import { EnrollmentWithCourse } from '../types/enrollment';

export const enrollmentsAPI = {
  enrollInCourse: async (courseId: string): Promise<void> => {
    await apiClient.post('/me/enrollments', { course_id: courseId });
  },

  getMyEnrollments: async (): Promise<EnrollmentWithCourse[]> => {
    const response = await apiClient.get('/me/enrollments');
    return response.data;
  },
};
```

**`frontend/src/api/purchases.ts`**
```typescript
import { apiClient } from './client';
import { PurchaseWithDetails, CreatePurchaseRequest, Purchase } from '../types/purchase';

export const purchasesAPI = {
  createPurchase: async (data: CreatePurchaseRequest): Promise<Purchase> => {
    const response = await apiClient.post('/me/purchases', data);
    return response.data;
  },

  getMyPurchases: async (): Promise<PurchaseWithDetails[]> => {
    const response = await apiClient.get('/me/purchases');
    return response.data;
  },
};
```

**Testing Stage 1:**
- Verify TypeScript compilation passes
- Verify Axios client initializes correctly
- Verify API base URL from env var
- Test token interceptor logic (unit test or manual)

---

### Stage 2: Authentication Context & Flow (2-3 hours)

**Purpose:** Implement complete authentication system with JWT token management

#### 2.1 Auth Context

**`frontend/src/context/AuthContext.tsx`**
```typescript
import React, { createContext, useState, useEffect, ReactNode } from 'react';
import { authAPI } from '../api/auth';
import { User, LoginRequest, RegisterRequest } from '../types/user';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isAdmin: boolean;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Load user on mount if token exists
  useEffect(() => {
    const loadUser = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const userData = await authAPI.getMe();
          setUser(userData);
        } catch (error) {
          console.error('Failed to load user:', error);
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      }
      setLoading(false);
    };

    loadUser();
  }, []);

  const login = async (credentials: LoginRequest) => {
    const authResponse = await authAPI.login(credentials);
    localStorage.setItem('access_token', authResponse.access_token);
    localStorage.setItem('refresh_token', authResponse.refresh_token);

    const userData = await authAPI.getMe();
    setUser(userData);
  };

  const register = async (data: RegisterRequest) => {
    const authResponse = await authAPI.register(data);
    localStorage.setItem('access_token', authResponse.access_token);
    localStorage.setItem('refresh_token', authResponse.refresh_token);

    const userData = await authAPI.getMe();
    setUser(userData);
  };

  const logout = () => {
    authAPI.logout();
    setUser(null);
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin',
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
```

#### 2.2 Auth Hook

**`frontend/src/hooks/useAuth.ts`**
```typescript
import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

#### 2.3 Protected Route Component

**`frontend/src/routes/ProtectedRoute.tsx`**
```typescript
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

interface ProtectedRouteProps {
  requireAdmin?: boolean;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ requireAdmin = false }) => {
  const { isAuthenticated, isAdmin, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requireAdmin && !isAdmin) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
};
```

#### 2.4 Login Page

**`frontend/src/pages/Login.tsx`**
```typescript
import { useState, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login({ email, password });
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '4rem auto', padding: '2rem' }}>
      <h1>Login</h1>
      <form onSubmit={handleSubmit} style={{ marginTop: '2rem' }}>
        {error && (
          <div style={{ padding: '1rem', backgroundColor: '#fee', color: '#c00', borderRadius: '4px', marginBottom: '1rem' }}>
            {error}
          </div>
        )}
        
        <div style={{ marginBottom: '1rem' }}>
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
          />
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%',
            padding: '0.75rem',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
          }}
        >
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>

      <p style={{ marginTop: '1rem', textAlign: 'center' }}>
        Don't have an account? <Link to="/register">Register</Link>
      </p>
    </div>
  );
}
```

#### 2.5 Register Page

**`frontend/src/pages/Register.tsx`** (similar structure to Login)

#### 2.6 Update App.tsx

**`frontend/src/App.tsx`**
```typescript
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import AppRoutes from './routes/AppRoutes';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
```

**Testing Stage 2:**
- Login with valid credentials
- Login with invalid credentials (verify error)
- Register new user
- Verify JWT tokens stored in localStorage
- Verify protected routes redirect to login
- Verify logout clears tokens

---

### Stage 3: Common UI Components (2 hours)

**Purpose:** Build reusable components for consistent UI

#### Components to Create:

**`frontend/src/components/common/Navbar.tsx`**
- Logo and site title
- Navigation links (Home, Courses, Products)
- Auth status (Login/Register or User menu)
- Logout button for authenticated users
- Admin link if user is admin

**`frontend/src/components/common/Button.tsx`**
- Primary, secondary, danger variants
- Loading state
- Disabled state

**`frontend/src/components/common/Card.tsx`**
- Container for course/product cards
- Consistent padding, shadows, hover effects

**`frontend/src/components/common/Input.tsx`**
- Text input with label
- Error message display
- Validation state

**`frontend/src/components/common/Modal.tsx`**
- Overlay modal for confirmations
- Close button and backdrop click

**`frontend/src/components/common/Loader.tsx`**
- Spinner for loading states
- Full-page and inline variants

**Testing Stage 3:**
- Visual inspection of all components
- Test different variants and states
- Verify responsive behavior

---

### Stage 4: Course Browsing & Detail (2-3 hours)

**Purpose:** Implement course listing and detail pages with enrollment

#### 4.1 Course Card Component

**`frontend/src/components/courses/CourseCard.tsx`**
- Display thumbnail, title, price
- Link to course detail page
- "Free" badge if price = 0
- Clean card design

#### 4.2 Course List Page

**`frontend/src/pages/Courses.tsx`**
- Fetch published courses from API
- Display in grid layout
- Pagination controls
- Loading and error states
- Empty state if no courses

#### 4.3 Course Detail Page

**`frontend/src/pages/CourseDetail.tsx`**
- Fetch course with sections/lessons by slug
- Display course info (title, description, price, thumbnail)
- Show course curriculum (sections and lessons)
- Enroll button (if not enrolled)
- "Go to Course" button (if enrolled)
- "Purchase Required" message (if paid course)
- Handle enrollment API call
- Success/error notifications

#### 4.4 Enroll Button Component

**`frontend/src/components/courses/EnrollButton.tsx`**
- Check if user is authenticated
- Check if user is enrolled
- Check if course is free or requires purchase
- Display appropriate button state
- Handle enrollment click

**Testing Stage 4:**
- Browse course list
- View course details
- Enroll in free course
- Verify enrolled status updates
- Test unauthenticated access
- Test paid course purchase requirement

---

### Stage 5: Product Browsing & Purchase (2-3 hours)

**Purpose:** Implement product listing and detail pages with purchase flow

#### 5.1 Product Card Component

**`frontend/src/components/products/ProductCard.tsx`**
- Display thumbnail, title, price
- Link to product detail page

#### 5.2 Product List Page

**`frontend/src/pages/Products.tsx`**
- Fetch published products from API
- Display in grid layout
- Pagination controls
- Loading and error states

#### 5.3 Product Detail Page

**`frontend/src/pages/ProductDetail.tsx`**
- Fetch product by slug
- Display product info
- Purchase button (if not purchased)
- "Download" button (if purchased)
- Handle purchase creation API call
- Show "Purchase Pending" status
- Explain admin needs to approve (Phase 4 limitation)

#### 5.4 Purchase Button Component

**`frontend/src/components/products/PurchaseButton.tsx`**
- Check authentication
- Check purchase status
- Create purchase on click
- Display pending/completed status

**Testing Stage 5:**
- Browse products
- View product details
- Create purchase for product
- Verify purchase appears in "My Purchases"
- Test authentication requirement

---

### Stage 6: Student Dashboard (2-3 hours)

**Purpose:** Build student portal for viewing enrollments and purchases

#### 6.1 Student Dashboard Page

**`frontend/src/pages/student/Dashboard.tsx`**
- Welcome message
- Quick stats (courses enrolled, purchases)
- Links to My Courses and My Purchases

#### 6.2 My Courses Page

**`frontend/src/pages/student/MyCourses.tsx`**
- Fetch user enrollments
- Display enrolled courses with progress
- Link to course content
- Empty state if no enrollments

#### 6.3 My Purchases Page

**`frontend/src/pages/student/MyPurchases.tsx`**
- Fetch user purchases
- Display purchase history (item, amount, status, date)
- Show pending/completed/failed status
- Link to item (course or product)
- Empty state if no purchases

#### 6.4 Course View Page (Enrolled Users Only)

**`frontend/src/pages/student/CourseView.tsx`**
- Verify user has access (enrolled + purchase if paid)
- Display course sections and lessons
- Click lesson to view content
- For Phase 5: Show lesson title and file link
- Video player implementation deferred to Phase 7

**Testing Stage 6:**
- View dashboard as student
- See enrolled courses
- View purchase history
- Access course content
- Verify access control (cannot access unpurchased paid courses)

---

### Stage 7: Admin Dashboard (2-3 hours)

**Purpose:** Build admin interface for content management

#### 7.1 Admin Dashboard Page

**`frontend/src/pages/admin/Dashboard.tsx`**
- Stats overview (total courses, products, users, purchases)
- Quick actions (create course, create product)
- Recent activity

#### 7.2 Manage Courses Page

**`frontend/src/pages/admin/ManageCourses.tsx`**
- List all courses (including drafts)
- Show status (draft/published)
- Edit and Delete buttons
- Link to Create Course

#### 7.3 Create Course Page

**`frontend/src/pages/admin/CreateCourse.tsx`**
- Form for course creation (title, description, price, status)
- File upload for thumbnail
- Submit to backend API
- Redirect to Manage Courses on success

#### 7.4 Edit Course Page

**`frontend/src/pages/admin/EditCourse.tsx`**
- Load existing course data
- Edit form (same fields as create)
- Update course API call

#### 7.5 Manage Products Page

**`frontend/src/pages/admin/ManageProducts.tsx`**
- List all products
- Edit/Delete actions
- Link to Create Product

#### 7.6 Create/Edit Product Pages

**`frontend/src/pages/admin/CreateProduct.tsx` and `EditProduct.tsx`**
- Form for product creation/editing
- File upload for product file and thumbnail
- Submit to backend

**Note:** Section and Lesson management can be simplified for Phase 5:
- Edit course page shows existing sections/lessons
- "Add Section" and "Add Lesson" can be basic forms
- Full rich editor for course structure deferred to Phase 7 if needed

**Testing Stage 7:**
- Login as admin
- Create new course
- Edit existing course
- Create new product
- Edit existing product
- Delete course/product
- Verify draft vs published status

---

## Routing Configuration

### Update `frontend/src/routes/AppRoutes.tsx`

```typescript
import { Routes, Route } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import Navbar from '../components/common/Navbar';

// Pages
import Home from '../pages/Home';
import Login from '../pages/Login';
import Register from '../pages/Register';
import Courses from '../pages/Courses';
import CourseDetail from '../pages/CourseDetail';
import Products from '../pages/Products';
import ProductDetail from '../pages/ProductDetail';

// Student Pages
import StudentDashboard from '../pages/student/Dashboard';
import MyCourses from '../pages/student/MyCourses';
import MyPurchases from '../pages/student/MyPurchases';
import CourseView from '../pages/student/CourseView';

// Admin Pages
import AdminDashboard from '../pages/admin/Dashboard';
import ManageCourses from '../pages/admin/ManageCourses';
import ManageProducts from '../pages/admin/ManageProducts';
import CreateCourse from '../pages/admin/CreateCourse';
import EditCourse from '../pages/admin/EditCourse';
import CreateProduct from '../pages/admin/CreateProduct';
import EditProduct from '../pages/admin/EditProduct';

export default function AppRoutes() {
  return (
    <>
      <Navbar />
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/courses" element={<Courses />} />
        <Route path="/courses/:slug" element={<CourseDetail />} />
        <Route path="/products" element={<Products />} />
        <Route path="/products/:slug" element={<ProductDetail />} />

        {/* Protected student routes */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<StudentDashboard />} />
          <Route path="/my-courses" element={<MyCourses />} />
          <Route path="/my-purchases" element={<MyPurchases />} />
          <Route path="/course/:slug/view" element={<CourseView />} />
        </Route>

        {/* Admin routes */}
        <Route element={<ProtectedRoute requireAdmin />}>
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/admin/courses" element={<ManageCourses />} />
          <Route path="/admin/courses/create" element={<CreateCourse />} />
          <Route path="/admin/courses/:id/edit" element={<EditCourse />} />
          <Route path="/admin/products" element={<ManageProducts />} />
          <Route path="/admin/products/create" element={<CreateProduct />} />
          <Route path="/admin/products/:id/edit" element={<EditProduct />} />
        </Route>
      </Routes>
    </>
  );
}
```

---

## Environment Variables

### Update `frontend/.env.example`

```env
VITE_API_BASE_URL=http://localhost:8000
```

### Create `frontend/.env`

```env
VITE_API_BASE_URL=http://localhost:8000
```

**Note:** `.env` should already be in `.gitignore`

---

## Testing Strategy

### Manual Testing Checklist

**Authentication:**
- [ ] Register new user
- [ ] Login with valid credentials
- [ ] Login with invalid credentials (verify error)
- [ ] Logout
- [ ] Token refresh on 401
- [ ] Protected routes redirect to login when not authenticated
- [ ] Admin routes redirect non-admin users

**Public Pages:**
- [ ] View course list
- [ ] View course detail
- [ ] View product list
- [ ] View product detail
- [ ] Pagination works on lists

**Student Flow:**
- [ ] Enroll in free course
- [ ] View enrolled courses
- [ ] Access course content
- [ ] Create purchase for paid course
- [ ] View purchase history
- [ ] Verify purchase shows "pending" status

**Admin Flow:**
- [ ] Create course (draft)
- [ ] Edit course
- [ ] Publish course
- [ ] Create product
- [ ] Edit product
- [ ] Delete course/product

**Access Control:**
- [ ] Cannot access paid course without purchase
- [ ] Can access free course with enrollment
- [ ] Cannot enroll twice in same course
- [ ] Cannot access admin pages as student

### Integration Testing

Run backend test suite to verify no regressions:
```bash
cd backend
pytest
# Expected: 125/125 tests passing
```

Build frontend to verify no compilation errors:
```bash
cd frontend
npm run build
# Expected: Build succeeds
```

---

## Files to Create/Modify

### New Files (48 files)

**API Layer (6 files):**
- `frontend/src/api/client.ts`
- `frontend/src/api/auth.ts`
- `frontend/src/api/courses.ts`
- `frontend/src/api/products.ts`
- `frontend/src/api/enrollments.ts`
- `frontend/src/api/purchases.ts`

**Types (5 files):**
- `frontend/src/types/user.ts`
- `frontend/src/types/course.ts`
- `frontend/src/types/product.ts`
- `frontend/src/types/enrollment.ts`
- `frontend/src/types/purchase.ts`

**Context & Hooks (2 files):**
- `frontend/src/context/AuthContext.tsx`
- `frontend/src/hooks/useAuth.ts`

**Common Components (6 files):**
- `frontend/src/components/common/Navbar.tsx`
- `frontend/src/components/common/Button.tsx`
- `frontend/src/components/common/Card.tsx`
- `frontend/src/components/common/Input.tsx`
- `frontend/src/components/common/Modal.tsx`
- `frontend/src/components/common/Loader.tsx`

**Course Components (3 files):**
- `frontend/src/components/courses/CourseCard.tsx`
- `frontend/src/components/courses/CourseList.tsx`
- `frontend/src/components/courses/EnrollButton.tsx`

**Product Components (3 files):**
- `frontend/src/components/products/ProductCard.tsx`
- `frontend/src/components/products/ProductList.tsx`
- `frontend/src/components/products/PurchaseButton.tsx`

**Public Pages (4 files):**
- `frontend/src/pages/Login.tsx` (replace)
- `frontend/src/pages/Register.tsx` (new)
- `frontend/src/pages/CourseDetail.tsx` (new)
- `frontend/src/pages/ProductDetail.tsx` (new)

**Student Pages (4 files):**
- `frontend/src/pages/student/Dashboard.tsx`
- `frontend/src/pages/student/MyCourses.tsx`
- `frontend/src/pages/student/MyPurchases.tsx`
- `frontend/src/pages/student/CourseView.tsx`

**Admin Pages (7 files):**
- `frontend/src/pages/admin/Dashboard.tsx`
- `frontend/src/pages/admin/ManageCourses.tsx`
- `frontend/src/pages/admin/ManageProducts.tsx`
- `frontend/src/pages/admin/CreateCourse.tsx`
- `frontend/src/pages/admin/EditCourse.tsx`
- `frontend/src/pages/admin/CreateProduct.tsx`
- `frontend/src/pages/admin/EditProduct.tsx`

**Utils (2 files):**
- `frontend/src/utils/formatters.ts`
- `frontend/src/utils/validators.ts`

### Modified Files (5 files)

- `frontend/src/App.tsx` (add AuthProvider)
- `frontend/src/routes/AppRoutes.tsx` (add all routes)
- `frontend/src/routes/ProtectedRoute.tsx` (implement auth guard)
- `frontend/src/pages/Home.tsx` (update with real content)
- `frontend/src/pages/Courses.tsx` (implement course list)
- `frontend/src/pages/Products.tsx` (implement product list)

### Configuration Files

- `frontend/.env.example` (update)
- `frontend/.env` (create with real values)

---

## Success Criteria

### Functional Requirements ✅

**Authentication:**
- [ ] User can register
- [ ] User can login
- [ ] User can logout
- [ ] JWT tokens stored and used correctly
- [ ] Token refresh works on 401
- [ ] Protected routes require authentication

**Course System:**
- [ ] Users can browse published courses
- [ ] Users can view course details
- [ ] Users can enroll in free courses
- [ ] Enrolled courses appear in "My Courses"
- [ ] Course curriculum displays sections and lessons
- [ ] Access control prevents access to unpurchased paid courses

**Product System:**
- [ ] Users can browse published products
- [ ] Users can view product details
- [ ] Users can create purchases for products
- [ ] Purchase history displays in "My Purchases"
- [ ] Purchases show correct status (pending/completed/failed)

**Admin System:**
- [ ] Admins can create courses
- [ ] Admins can edit courses
- [ ] Admins can create products
- [ ] Admins can edit products
- [ ] Admins can set draft/published status
- [ ] Non-admins cannot access admin pages

**Access Control:**
- [ ] Free courses accessible after enrollment
- [ ] Paid courses require purchase before access
- [ ] Enrollment verification works
- [ ] Purchase verification works

### Technical Requirements ✅

- [ ] TypeScript compilation succeeds with no errors
- [ ] All API endpoints integrated
- [ ] Error handling for all API calls
- [ ] Loading states for all async operations
- [ ] Responsive design (mobile-friendly)
- [ ] No console errors in browser
- [ ] Frontend builds successfully
- [ ] Backend tests still pass (125/125)

### User Experience ✅

- [ ] Clear navigation between pages
- [ ] Consistent UI design
- [ ] Helpful error messages
- [ ] Success feedback for actions
- [ ] Loading indicators
- [ ] Empty states for lists
- [ ] Accessible (keyboard navigation, labels)

---

## Known Limitations (By Design)

### Not Implemented in Phase 5

**Payment Integration:**
- ❌ No real payment provider (Stripe, PayPal)
- ❌ No checkout flow with redirect
- ❌ Purchases remain "pending" until admin manually completes
- ⚠️ Users see "Purchase Created - Awaiting Admin Approval" message

**Course Content:**
- ❌ No video player (just file URLs shown)
- ❌ No PDF viewer (just download links)
- ❌ No progress tracking (percentage stored but not updated)
- ❌ No lesson completion marking

**Advanced Features:**
- ❌ No search/filter on course/product lists
- ❌ No user profile page
- ❌ No email notifications
- ❌ No analytics/reporting
- ❌ No multi-creator support in UI

### Phase 5 Simplifications

**Admin Course Management:**
- Sections and lessons can be created via simple forms
- No drag-and-drop reordering (use order_index field)
- No rich text editor (plain textarea for description)
- File uploads for lessons link to existing upload endpoints

**UI/UX:**
- Minimal styling (clean but basic)
- No UI framework (plain CSS or CSS modules)
- No animations or transitions
- Mobile-responsive but not mobile-optimized

---

## Database & Backend Changes

### No Database Migration Required ✅

Phase 5 is frontend-only. The backend remains unchanged.

### No Backend Code Changes Required ✅

All necessary APIs exist:
- ✅ Auth endpoints (login, register, me)
- ✅ Course endpoints (list, detail, create, update, delete)
- ✅ Product endpoints (list, detail, create, update, delete)
- ✅ Enrollment endpoints (create, list)
- ✅ Purchase endpoints (create, list)
- ✅ Upload endpoints (course files, product files, thumbnails)
- ✅ Admin endpoints (all CRUD operations)

**Verification:**
```bash
cd backend
source venv/Scripts/activate
pytest
# Expected: 125/125 tests passing
```

---

## Security Considerations

### Frontend Security ✅

**Token Storage:**
- ✅ JWT tokens stored in localStorage (acceptable for Phase 5)
- ⚠️ Future: Consider httpOnly cookies for refresh tokens (Phase 6+)

**Authorization:**
- ✅ Protected routes check authentication
- ✅ Admin routes check role
- ✅ Backend always validates (never trust frontend)

**API Communication:**
- ✅ HTTPS enforced in production
- ✅ CORS configured on backend
- ✅ No sensitive data in URLs (use POST body)

**Input Validation:**
- ✅ Frontend validates form inputs
- ✅ Backend always validates (primary defense)
- ✅ No client-side only security

**XSS Prevention:**
- ✅ React automatically escapes user content
- ✅ Use `dangerouslySetInnerHTML` only if absolutely necessary

---

## Production Considerations

### Before Production ⚠️

**Environment:**
1. Update `VITE_API_BASE_URL` to production API URL
2. Build frontend with production config: `npm run build`
3. Deploy `frontend/dist/` to Vercel/Netlify/static hosting
4. Verify CORS settings on backend for production frontend domain

**Security:**
1. Enforce HTTPS for all requests
2. Set secure CORS policy (specific domains, not "*")
3. Implement rate limiting (backend)
4. Add CAPTCHA to registration (future)

**Performance:**
1. Enable gzip compression on hosting
2. Configure CDN for static assets
3. Optimize images (thumbnails)
4. Implement lazy loading for course/product lists

**Monitoring:**
1. Add error tracking (Sentry)
2. Add analytics (Google Analytics, Plausible)
3. Monitor API response times
4. Track user flows (funnels)

---

## Next Steps (Phase 6)

**Phase 6 will implement Real Payment Integration:**
1. Stripe/PayPal integration
2. Payment checkout flow
3. Redirect to payment provider
4. Webhook handlers (backend)
5. Automatic purchase completion
6. Payment confirmation page
7. Email notifications (purchase complete, enrollment confirmed)
8. Receipt/invoice generation

**Requirements for Phase 6:**
- ✅ Frontend Phase 5 complete (this phase)
- ✅ Backend Phase 4 purchase system complete
- ✅ User can create purchases
- ✅ Admin can mark purchases complete (manual fallback)
- 🔲 Payment provider account (Stripe recommended)
- 🔲 Webhook endpoint on backend
- 🔲 SSL certificate for webhook security

---

## Implementation Timeline

### Week 1: Foundation (6-8 hours)
- **Day 1-2:** Stage 1 + Stage 2 (API layer, auth context, login/register)
- **Day 3:** Stage 3 (common components)

### Week 2: Core Features (6-8 hours)
- **Day 4-5:** Stage 4 (course browsing, detail, enrollment)
- **Day 6:** Stage 5 (product browsing, detail, purchase)

### Week 3: Dashboards (6-8 hours)
- **Day 7-8:** Stage 6 (student dashboard, my courses, my purchases)
- **Day 9-10:** Stage 7 (admin dashboard, course/product management)

### Week 4: Testing & Polish (2-4 hours)
- **Day 11:** Testing checklist completion
- **Day 12:** Bug fixes, polish, documentation

**Total Estimated Time:** 12-16 hours over 12 days (1-2 hours per day)

---

## Risk Mitigation

### Risk: Breaking Backend APIs
**Mitigation:** Run backend test suite after Phase 5 (should still be 125/125)

### Risk: Authentication Issues (Token Expiry)
**Mitigation:** Implement refresh token logic in axios interceptor from day 1

### Risk: Access Control Bypass
**Mitigation:** Backend always validates. Frontend checks are UX only.

### Risk: CORS Errors in Development
**Mitigation:** Backend already configured for `localhost:5173` (Vite default)

### Risk: Scope Creep (Adding Features)
**Mitigation:** Strict adherence to Phase 5 scope. Note features for Phase 6+.

---

## Questions for Review

1. **Styling approach:** Plain CSS or add Tailwind CSS for faster development?
2. **State management:** Context API sufficient or add Zustand for better DX?
3. **Form library:** Plain forms or add React Hook Form for validation?
4. **File uploads:** Direct from browser to Supabase (future) or via backend (current)?
5. **Admin section/lesson management:** Simple forms or richer interface?

**Recommendation:** Keep Phase 5 simple. Use Context API, plain forms, current backend flow. Polish in Phase 6+.

---

## Appendix: API Endpoints Reference

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user

### Courses (Public)
- `GET /courses?page=1&page_size=20` - List published courses
- `GET /courses/{slug}` - Get course details with sections/lessons

### Products (Public)
- `GET /products?page=1&page_size=20` - List published products
- `GET /products/{slug}` - Get product details

### Enrollments (Authenticated)
- `POST /me/enrollments` - Enroll in course
- `GET /me/enrollments` - List user's enrollments

### Purchases (Authenticated)
- `POST /me/purchases` - Create purchase
- `GET /me/purchases` - List user's purchases

### Admin - Courses
- `POST /admin/courses` - Create course
- `PUT /admin/courses/{id}` - Update course
- `DELETE /admin/courses/{id}` - Delete course
- `POST /admin/courses/{id}/sections` - Add section
- `POST /admin/sections/{id}/lessons` - Add lesson

### Admin - Products
- `POST /admin/products` - Create product
- `PUT /admin/products/{id}` - Update product
- `DELETE /admin/products/{id}` - Delete product

### Uploads (Admin)
- `POST /uploads/course-file` - Upload course video/PDF
- `POST /uploads/product-file` - Upload product file
- `POST /uploads/thumbnail` - Upload thumbnail image

---

## Conclusion

Phase 5 implements the **complete frontend user interface** required for the Digital Hub platform to function as an MVP. Upon completion, users will be able to:

- ✅ Register and login
- ✅ Browse courses and products
- ✅ Enroll in free courses
- ✅ Purchase paid courses and products
- ✅ Access enrolled course content
- ✅ View purchase history
- ✅ Manage content as admin

**This phase transforms the Digital Hub from a backend API into a fully functional web application.**

**Phase 5 Status:** READY FOR IMPLEMENTATION  
**Backend Status:** 125/125 tests passing, all APIs ready  
**Frontend Status:** Phase 1A only, needs full implementation  
**Estimated Time:** 12-16 hours  
**Next Phase:** Phase 6 - Payment Provider Integration

---

**End of Phase 5 Implementation Plan**
