import pytest
from fastapi import status
from sqlalchemy.orm import Session
from unittest.mock import Mock, MagicMock, patch
from io import BytesIO

from app.db.models.user import User, UserRole
from app.db.models.creator import Creator
from app.core.security import get_password_hash
from app.services.storage_service import StorageService
from decimal import Decimal


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def admin_user_with_creator(db_session: Session):
    """Create an admin user with creator profile."""
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    creator = Creator(
        user_id=user.id,
        display_name="Admin Creator",
        bio="Test creator bio",
        revenue_share_percent=Decimal("100.00")
    )
    db_session.add(creator)
    db_session.commit()
    db_session.refresh(creator)

    return user


@pytest.fixture
def admin_token(client, admin_user_with_creator):
    """Get admin authentication token."""
    response = client.post(
        "/auth/login",
        json={
            "email": "admin@example.com",
            "password": "password123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def student_user(db_session: Session):
    """Create a student user."""
    user = User(
        email="student@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Student User",
        role=UserRole.STUDENT,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def student_token(client, student_user):
    """Get student authentication token."""
    response = client.post(
        "/auth/login",
        json={
            "email": "student@example.com",
            "password": "password123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def mock_supabase_storage():
    """Mock Supabase storage client."""
    with patch('app.services.storage_service.create_client') as mock_create:
        mock_client = MagicMock()
        mock_storage = MagicMock()
        mock_bucket = MagicMock()

        # Setup upload response
        mock_bucket.upload.return_value = {"path": "test-file.pdf"}

        # Setup get_public_url response
        mock_bucket.get_public_url.return_value = "https://example.com/storage/test-file.pdf"

        # Setup create_signed_url response
        mock_bucket.create_signed_url.return_value = {
            "signedURL": "https://example.com/storage/test-file.pdf?token=abc123"
        }

        mock_storage.from_.return_value = mock_bucket
        mock_client.storage = mock_storage
        mock_create.return_value = mock_client

        yield mock_client


# ============================================================================
# Storage Service Unit Tests
# ============================================================================

class TestStorageServiceValidation:
    """Tests for file validation in storage service."""

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        service = StorageService()

        # Test basic sanitization
        assert service._sanitize_filename("test file.pdf") == "test_file.pdf"
        sanitized = service._sanitize_filename("../../../etc/passwd")
        assert "passwd" in sanitized  # Should contain passwd
        assert "/" not in sanitized  # Should not contain path separators
        assert ".." not in sanitized  # Should not contain ..
        assert service._sanitize_filename("file@name!.jpg") == "file_name_.jpg"

        # Test path traversal prevention
        assert ".." not in service._sanitize_filename("../../secret.txt")
        assert "/" not in service._sanitize_filename("path/to/file.pdf")
        assert "\\" not in service._sanitize_filename("path\\to\\file.pdf")

    def test_generate_unique_filename(self):
        """Test unique filename generation."""
        service = StorageService()

        filename1 = service._generate_unique_filename("test.pdf")
        filename2 = service._generate_unique_filename("test.pdf")

        # Should be different
        assert filename1 != filename2

        # Should preserve extension
        assert filename1.endswith(".pdf")
        assert filename2.endswith(".pdf")

    def test_validate_file_size_within_limit(self, mock_supabase_storage):
        """Test file size validation passes for small file."""
        service = StorageService()

        # Create mock file under size limit
        mock_file = Mock()
        mock_file.file = BytesIO(b"small file content")
        mock_file.file.seek(0, 2)  # Seek to end
        mock_file.filename = "test.pdf"
        mock_file.content_type = "application/pdf"

        # Should not raise exception
        service._validate_file_size(mock_file, 10)  # 10MB limit

    def test_validate_file_size_exceeds_limit(self, mock_supabase_storage):
        """Test file size validation fails for large file."""
        service = StorageService()

        # Create mock file over size limit
        mock_file = Mock()
        large_content = b"x" * (2 * 1024 * 1024)  # 2MB
        mock_file.file = BytesIO(large_content)
        mock_file.file.seek(0, 2)
        mock_file.filename = "large.pdf"
        mock_file.content_type = "application/pdf"

        # Should raise exception
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            service._validate_file_size(mock_file, 1)  # 1MB limit

        assert exc_info.value.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        assert "too large" in exc_info.value.detail.lower()

    def test_validate_content_type_allowed(self, mock_supabase_storage):
        """Test content type validation passes for allowed type."""
        service = StorageService()

        mock_file = Mock()
        mock_file.content_type = "application/pdf"

        # Should not raise exception
        service._validate_content_type(mock_file, {"application/pdf", "text/plain"})

    def test_validate_content_type_not_allowed(self, mock_supabase_storage):
        """Test content type validation fails for disallowed type."""
        service = StorageService()

        mock_file = Mock()
        mock_file.content_type = "application/x-msdownload"  # .exe file

        # Should raise exception
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            service._validate_content_type(mock_file, {"application/pdf"})

        assert exc_info.value.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        assert "not allowed" in exc_info.value.detail.lower()


# ============================================================================
# Upload Endpoint Tests
# ============================================================================

class TestCourseFileUpload:
    """Tests for course file upload endpoint."""

    def test_upload_course_file_without_auth(self, client):
        """Test that unauthenticated users cannot upload."""
        response = client.post(
            "/uploads/course-file",
            files={"file": ("test.mp4", BytesIO(b"content"), "video/mp4")},
            data={"file_type": "video"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_upload_course_file_as_student(self, client, student_token):
        """Test that students cannot upload."""
        response = client.post(
            "/uploads/course-file",
            headers={"Authorization": f"Bearer {student_token}"},
            files={"file": ("test.mp4", BytesIO(b"content"), "video/mp4")},
            data={"file_type": "video"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestProductFileUpload:
    """Tests for product file upload endpoint."""

    def test_upload_product_file_without_auth(self, client):
        """Test that unauthenticated users cannot upload."""
        response = client.post(
            "/uploads/product-file",
            files={"file": ("product.pdf", BytesIO(b"content"), "application/pdf")}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestThumbnailUpload:
    """Tests for thumbnail upload endpoint."""

    def test_upload_thumbnail_without_auth(self, client):
        """Test that unauthenticated users cannot upload."""
        response = client.post(
            "/uploads/thumbnail",
            files={"file": ("thumb.jpg", BytesIO(b"content"), "image/jpeg")}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


# ============================================================================
# File Type Validation Tests
# ============================================================================

class TestFileTypeValidation:
    """Tests for file type validation."""

    def test_reject_executable_file(self, client, admin_token):
        """Test that executable files are rejected."""
        exe_content = b"MZ\x90\x00"  # .exe header

        response = client.post(
            "/uploads/product-file",
            headers={"Authorization": f"Bearer {admin_token}"},
            files={"file": ("malware.exe", BytesIO(exe_content), "application/x-msdownload")}
        )

        assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        assert "not allowed" in response.json()["detail"].lower()

    def test_reject_script_file(self, client, admin_token):
        """Test that script files are rejected."""
        script_content = b"#!/bin/bash\nrm -rf /"

        response = client.post(
            "/uploads/product-file",
            headers={"Authorization": f"Bearer {admin_token}"},
            files={"file": ("script.sh", BytesIO(script_content), "application/x-sh")}
        )

        assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

    def test_reject_invalid_video_type(self, client, admin_token):
        """Test that invalid video types are rejected."""
        response = client.post(
            "/uploads/course-file",
            headers={"Authorization": f"Bearer {admin_token}"},
            files={"file": ("video.avi", BytesIO(b"content"), "video/x-msvideo")},
            data={"file_type": "video"}
        )

        assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


# ============================================================================
# Security Tests
# ============================================================================

class TestSecurityValidation:
    """Tests for security validation."""

    def test_filename_path_traversal_prevention(self):
        """Test that path traversal in filenames is prevented."""
        service = StorageService()

        malicious_names = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//etc/passwd",
            "/etc/passwd",
            "C:\\Windows\\System32\\config\\sam"
        ]

        for name in malicious_names:
            sanitized = service._sanitize_filename(name)

            # Should not contain path separators
            assert "/" not in sanitized
            assert "\\" not in sanitized
            assert ".." not in sanitized

    def test_filename_special_characters_removed(self):
        """Test that special characters are removed from filenames."""
        service = StorageService()

        test_cases = [
            ("file<script>.pdf", "file_script_.pdf"),
            ("file|name.pdf", "file_name.pdf"),
            ("file:name.pdf", "file_name.pdf"),
            ("file*name.pdf", "file_name.pdf"),
            ("file?name.pdf", "file_name.pdf"),
        ]

        for original, expected_pattern in test_cases:
            sanitized = service._sanitize_filename(original)
            # Should not contain special characters
            assert "<" not in sanitized
            assert ">" not in sanitized
            assert "|" not in sanitized
            assert "*" not in sanitized
            assert "?" not in sanitized


# ============================================================================
# Note: Actual upload tests and signed URL tests require Supabase credentials
# and are better suited for integration testing. The tests above focus on:
# - Authorization (admin-only access)
# - File validation (type, size, filename)
# - Security (path traversal, special characters)
# These are the critical tests that don't require external dependencies.
# ============================================================================
