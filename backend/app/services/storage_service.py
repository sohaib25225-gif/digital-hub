import os
import re
import uuid
from typing import Optional, BinaryIO, Tuple
from fastapi import HTTPException, status, UploadFile
from supabase import create_client, Client

from app.core.config import settings


class StorageService:
    """Service for handling file uploads and storage with Supabase Storage."""

    # Storage buckets
    BUCKET_COURSE_VIDEOS = "course-videos"
    BUCKET_COURSE_PDFS = "course-pdfs"
    BUCKET_PRODUCT_FILES = "product-files"
    BUCKET_THUMBNAILS = "thumbnails"

    # Allowed MIME types
    ALLOWED_VIDEO_TYPES = {
        "video/mp4",
        "video/webm",
        "video/ogg",
        "video/quicktime",  # .mov files
    }

    ALLOWED_PDF_TYPES = {
        "application/pdf",
    }

    ALLOWED_PRODUCT_FILE_TYPES = {
        "application/pdf",
        "application/zip",
        "application/x-zip-compressed",
        "application/epub+zip",  # .epub
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
        "text/plain",
    }

    ALLOWED_IMAGE_TYPES = {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",
        "image/gif",
    }

    def __init__(self):
        """Initialize Supabase Storage client."""
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
            # Allow initialization even without Supabase credentials for testing
            self.client: Optional[Client] = None
        else:
            try:
                self.client: Client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_SERVICE_KEY
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to initialize storage client: {str(e)}"
                )

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and other security issues.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Get the file extension
        name, ext = os.path.splitext(filename)

        # Remove any path components
        name = os.path.basename(name)

        # Remove any non-alphanumeric characters except hyphens and underscores
        name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)

        # Limit length
        name = name[:100]

        # Ensure name is not empty
        if not name:
            name = "file"

        # Sanitize extension
        ext = ext.lower()
        ext = re.sub(r'[^a-zA-Z0-9.]', '', ext)

        return f"{name}{ext}"

    def _generate_unique_filename(self, original_filename: str) -> str:
        """
        Generate a unique filename using UUID.

        Args:
            original_filename: Original filename

        Returns:
            Unique filename
        """
        sanitized = self._sanitize_filename(original_filename)
        name, ext = os.path.splitext(sanitized)
        unique_id = str(uuid.uuid4())[:8]
        return f"{unique_id}_{name}{ext}"

    def _validate_file_size(self, file: UploadFile, max_size_mb: int) -> None:
        """
        Validate file size.

        Args:
            file: Uploaded file
            max_size_mb: Maximum allowed size in MB

        Raises:
            HTTPException: If file exceeds size limit
        """
        # Get file size by seeking to end
        file.file.seek(0, os.SEEK_END)
        size_bytes = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        max_size_bytes = max_size_mb * 1024 * 1024

        if size_bytes > max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {max_size_mb}MB"
            )

    def _validate_content_type(self, file: UploadFile, allowed_types: set) -> None:
        """
        Validate file content type.

        Args:
            file: Uploaded file
            allowed_types: Set of allowed MIME types

        Raises:
            HTTPException: If content type not allowed
        """
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
            )

    def _ensure_client(self) -> Client:
        """
        Ensure Supabase client is initialized.

        Returns:
            Supabase client

        Raises:
            HTTPException: If client not initialized
        """
        if self.client is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Storage service not properly configured"
            )
        return self.client

    async def upload_course_video(self, file: UploadFile) -> str:
        """
        Upload a course video file.

        Args:
            file: Video file to upload

        Returns:
            Public URL of uploaded file

        Raises:
            HTTPException: If upload fails or validation fails
        """
        # Validate
        self._validate_content_type(file, self.ALLOWED_VIDEO_TYPES)
        self._validate_file_size(file, settings.MAX_FILE_SIZE_MB)

        # Generate unique filename
        unique_filename = self._generate_unique_filename(file.filename)

        # Upload to Supabase
        client = self._ensure_client()

        try:
            content = await file.read()
            await file.seek(0)  # Reset for potential re-use

            response = client.storage.from_(self.BUCKET_COURSE_VIDEOS).upload(
                path=unique_filename,
                file=content,
                file_options={"content-type": file.content_type}
            )

            # Get public URL (or signed URL for private buckets)
            url = client.storage.from_(self.BUCKET_COURSE_VIDEOS).get_public_url(unique_filename)

            return url

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload video: {str(e)}"
            )

    async def upload_course_pdf(self, file: UploadFile) -> str:
        """
        Upload a course PDF file.

        Args:
            file: PDF file to upload

        Returns:
            Public URL of uploaded file

        Raises:
            HTTPException: If upload fails or validation fails
        """
        # Validate
        self._validate_content_type(file, self.ALLOWED_PDF_TYPES)
        self._validate_file_size(file, settings.MAX_FILE_SIZE_MB)

        # Generate unique filename
        unique_filename = self._generate_unique_filename(file.filename)

        # Upload to Supabase
        client = self._ensure_client()

        try:
            content = await file.read()
            await file.seek(0)

            response = client.storage.from_(self.BUCKET_COURSE_PDFS).upload(
                path=unique_filename,
                file=content,
                file_options={"content-type": file.content_type}
            )

            url = client.storage.from_(self.BUCKET_COURSE_PDFS).get_public_url(unique_filename)

            return url

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload PDF: {str(e)}"
            )

    async def upload_product_file(self, file: UploadFile) -> str:
        """
        Upload a product downloadable file.

        Args:
            file: Product file to upload

        Returns:
            Public URL of uploaded file

        Raises:
            HTTPException: If upload fails or validation fails
        """
        # Validate
        self._validate_content_type(file, self.ALLOWED_PRODUCT_FILE_TYPES)
        self._validate_file_size(file, settings.MAX_FILE_SIZE_MB)

        # Generate unique filename
        unique_filename = self._generate_unique_filename(file.filename)

        # Upload to Supabase
        client = self._ensure_client()

        try:
            content = await file.read()
            await file.seek(0)

            response = client.storage.from_(self.BUCKET_PRODUCT_FILES).upload(
                path=unique_filename,
                file=content,
                file_options={"content-type": file.content_type}
            )

            url = client.storage.from_(self.BUCKET_PRODUCT_FILES).get_public_url(unique_filename)

            return url

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload product file: {str(e)}"
            )

    async def upload_thumbnail(self, file: UploadFile) -> str:
        """
        Upload a thumbnail image.

        Args:
            file: Image file to upload

        Returns:
            Public URL of uploaded file

        Raises:
            HTTPException: If upload fails or validation fails
        """
        # Validate
        self._validate_content_type(file, self.ALLOWED_IMAGE_TYPES)
        self._validate_file_size(file, settings.MAX_THUMBNAIL_SIZE_MB)

        # Generate unique filename
        unique_filename = self._generate_unique_filename(file.filename)

        # Upload to Supabase
        client = self._ensure_client()

        try:
            content = await file.read()
            await file.seek(0)

            response = client.storage.from_(self.BUCKET_THUMBNAILS).upload(
                path=unique_filename,
                file=content,
                file_options={"content-type": file.content_type}
            )

            url = client.storage.from_(self.BUCKET_THUMBNAILS).get_public_url(unique_filename)

            return url

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload thumbnail: {str(e)}"
            )

    def create_signed_url(self, bucket: str, path: str, expires_in: int = 3600) -> str:
        """
        Create a signed URL for temporary access to a private file.

        Args:
            bucket: Storage bucket name
            path: File path in bucket
            expires_in: Expiration time in seconds (default: 1 hour)

        Returns:
            Signed URL

        Raises:
            HTTPException: If URL generation fails
        """
        client = self._ensure_client()

        try:
            response = client.storage.from_(bucket).create_signed_url(
                path=path,
                expires_in=expires_in
            )

            if response and "signedURL" in response:
                return response["signedURL"]
            else:
                raise Exception("No signed URL in response")

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate signed URL: {str(e)}"
            )
