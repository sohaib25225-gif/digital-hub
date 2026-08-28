from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, courses, products, admin, uploads, me

# Create FastAPI application instance
app = FastAPI(
    title="Digital Hub API",
    description="Personal Digital Products & Courses Platform",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Digital Hub API is running",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok"}


# Mount routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(courses.router, prefix="/courses", tags=["Courses"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(uploads.router, prefix="/uploads", tags=["Uploads"])
app.include_router(me.router, prefix="/me", tags=["User Protected"])
