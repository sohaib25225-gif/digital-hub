# Development Setup Guide

This guide explains how to set up and run the Digital Hub project locally.

## Prerequisites

- Python 3.10+ (for backend)
- Node.js 18+ (for frontend)
- PostgreSQL 14+ (local or remote instance)
- Git

## Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env and update the following:
   # - DATABASE_URL with your PostgreSQL connection string
   # - FRONTEND_ORIGIN (default: http://localhost:5173)
   # - JWT_SECRET_KEY (generate a secure random string)
   ```

5. **Run database migrations:**
   ```bash
   # Initialize Alembic (if not already done)
   alembic upgrade head
   ```
   
   Note: Phase 1A has no models yet, so no tables will be created. This verifies Alembic works.

6. **Start the development server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

   The API will be available at `http://localhost:8000`
   - API docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`

## Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables:**
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env and update:
   # - VITE_API_BASE_URL (default: http://localhost:8000)
   ```

4. **Start the development server:**
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:5173`

5. **Build for production:**
   ```bash
   npm run build
   ```

   Built files will be in the `dist/` directory.

## Database Management with Alembic

### Generate a new migration
```bash
cd backend
alembic revision --autogenerate -m "description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback one migration
```bash
alembic downgrade -1
```

### View migration history
```bash
alembic history
```

### View current migration version
```bash
alembic current
```

## Verification

### Backend Verification
1. Check that the server starts without errors
2. Visit `http://localhost:8000` - you should see a JSON response with status "healthy"
3. Visit `http://localhost:8000/docs` - you should see the FastAPI Swagger documentation

### Frontend Verification
1. Check that the dev server starts without errors
2. Visit `http://localhost:5173` - you should see the home page
3. Navigate to `/courses` and `/products` - you should see placeholder pages
4. Run `npm run build` - it should complete without TypeScript errors

### Alembic Verification
```bash
cd backend
alembic current  # Should show no errors (may show no version if no migrations run)
alembic check    # Should show database is up to date
```

## Common Issues

### Backend won't start
- Verify PostgreSQL is running and accessible
- Check DATABASE_URL in `.env` is correct
- Ensure all dependencies are installed: `pip list`
- Check Python version: `python --version` (should be 3.10+)

### Frontend won't start
- Ensure Node.js is installed: `node --version`
- Delete `node_modules/` and `package-lock.json`, then run `npm install` again
- Check for port conflicts (port 5173)

### Database connection errors
- Verify PostgreSQL service is running
- Check database credentials in DATABASE_URL
- Ensure the database exists: `createdb digital_hub`
- Test connection: `psql <your-database-url>`

## Project Structure

```
digital-hub/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── main.py   # FastAPI app entry point
│   │   ├── core/     # Config, security, dependencies
│   │   ├── db/       # Database setup and models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── routers/  # API endpoints
│   │   ├── services/ # Business logic
│   │   └── repositories/ # Data access layer
│   ├── alembic/      # Database migrations
│   ├── tests/        # Backend tests
│   └── requirements.txt
├── frontend/          # React + TypeScript frontend
│   ├── src/
│   │   ├── api/      # API client
│   │   ├── components/ # React components
│   │   ├── pages/    # Page components
│   │   ├── routes/   # Routing configuration
│   │   ├── context/  # React context
│   │   ├── hooks/    # Custom hooks
│   │   └── types/    # TypeScript types
│   └── package.json
└── docs/             # Documentation
    ├── phase1-architecture-spec.md
    └── development-setup.md
```

## Next Steps

Phase 1A provides the foundation. Phase 1B will add:
- Database models (users, creators, courses, products)
- Authentication (JWT)
- API endpoints for courses and products
- Admin dashboard
- User registration and login

See `phase1-architecture-spec.md` for the complete architecture and planned features.
