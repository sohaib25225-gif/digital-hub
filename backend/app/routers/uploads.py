from typing import Annotated
from fastapi import APIRouter, Depends, UploadFile, File, Form
from enum import Enum

from app.core.dependencies import get_current_admin
from app.db.models.user import User
from app.services.storage_service import StorageService

router = APIRouter()


class CourseFileType(str, Enum):
    """Enum for course file types."""
    VIDEO = "video"
    PDF = "pdf"


@router.get("/health")
def uploads_health():
    """Health check endpoint for uploads router."""
    return {"status": "ok", "router": "uploads"}


@router.post("/course-file")
async def upload_course_file(
    file: UploadFile = File(...),
    file_type: CourseFileType = Form(...),
    current_admin: Annotated[User, Depends(get_current_admin)] = None
):
    """
    Upload a course file (video or PDF) - Admin only.

    Uploads files to Supabase Storage in the appropriate bucket.
    Returns the public URL of the uploaded file.

    Args:
        file: The file to upload
        file_type: Type of file (video or pdf)
        current_admin: Authenticated admin user

    Returns:
        URL of the uploaded file

    Raises:
        403: If user is not admin
        413: If file exceeds size limit
        415: If file type not allowed
        500: If upload fails
    """
    storage_service = StorageService()

    if file_type == CourseFileType.VIDEO:
        url = await storage_service.upload_course_video(file)
    else:  # PDF
        url = await storage_service.upload_course_pdf(file)

    return {
        "url": url,
        "filename": file.filename,
        "content_type": file.content_type,
        "file_type": file_type.value
    }


@router.post("/product-file")
async def upload_product_file(
    file: UploadFile = File(...),
    current_admin: Annotated[User, Depends(get_current_admin)] = None
):
    """
    Upload a product downloadable file - Admin only.

    Uploads files to Supabase Storage in the product-files bucket.
    Returns the public URL of the uploaded file.

    Supports: PDF, ZIP, EPUB, DOCX, TXT

    Args:
        file: The file to upload
        current_admin: Authenticated admin user

    Returns:
        URL of the uploaded file

    Raises:
        403: If user is not admin
        413: If file exceeds size limit
        415: If file type not allowed
        500: If upload fails
    """
    storage_service = StorageService()
    url = await storage_service.upload_product_file(file)

    return {
        "url": url,
        "filename": file.filename,
        "content_type": file.content_type
    }


@router.post("/thumbnail")
async def upload_thumbnail(
    file: UploadFile = File(...),
    current_admin: Annotated[User, Depends(get_current_admin)] = None
):
    """
    Upload a thumbnail image - Admin only.

    Uploads images to Supabase Storage in the thumbnails bucket.
    Returns the public URL of the uploaded image.

    Supports: JPEG, PNG, WebP, GIF

    Args:
        file: The image file to upload
        current_admin: Authenticated admin user

    Returns:
        URL of the uploaded image

    Raises:
        403: If user is not admin
        413: If file exceeds size limit (5MB)
        415: If file type not allowed
        500: If upload fails
    """
    storage_service = StorageService()
    url = await storage_service.upload_thumbnail(file)

    return {
        "url": url,
        "filename": file.filename,
        "content_type": file.content_type
    }
