import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.db.models.user import User, UserRole
from app.db.models.creator import Creator
from app.db.models.course import Course, CourseStatus
from app.db.models.section import Section
from app.db.models.lesson import Lesson, LessonContentType
from app.core.security import get_password_hash
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
def sample_course(db_session: Session, admin_user_with_creator):
    """Create a sample published course."""
    creator = db_session.query(Creator).filter(Creator.user_id == admin_user_with_creator.id).first()

    course = Course(
        creator_id=creator.id,
        title="Sample Course",
        slug="sample-course",
        description="A sample course for testing",
        price=Decimal("99.99"),
        status=CourseStatus.PUBLISHED
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course


@pytest.fixture
def draft_course(db_session: Session, admin_user_with_creator):
    """Create a draft course."""
    creator = db_session.query(Creator).filter(Creator.user_id == admin_user_with_creator.id).first()

    course = Course(
        creator_id=creator.id,
        title="Draft Course",
        slug="draft-course",
        description="A draft course",
        price=Decimal("49.99"),
        status=CourseStatus.DRAFT
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course


# ============================================================================
# Public Course Listing Tests
# ============================================================================

class TestPublicCourseListing:
    """Tests for public course listing endpoint."""

    def test_list_published_courses(self, client, sample_course):
        """Test listing published courses returns only published courses."""
        response = client.get("/courses/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "courses" in data
        assert "total" in data
        assert data["total"] >= 1
        assert len(data["courses"]) >= 1

        # Verify course data
        course = data["courses"][0]
        assert course["slug"] == "sample-course"
        assert course["title"] == "Sample Course"
        assert course["status"] == "published"

    def test_list_courses_excludes_drafts(self, client, sample_course, draft_course):
        """Test that draft courses are not visible in public listing."""
        response = client.get("/courses/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify only published course is returned
        slugs = [course["slug"] for course in data["courses"]]
        assert "sample-course" in slugs
        assert "draft-course" not in slugs

    def test_list_courses_pagination(self, client, admin_user_with_creator, db_session):
        """Test course listing pagination."""
        creator = db_session.query(Creator).filter(Creator.user_id == admin_user_with_creator.id).first()

        # Create multiple courses
        for i in range(5):
            course = Course(
                creator_id=creator.id,
                title=f"Course {i}",
                slug=f"course-{i}",
                status=CourseStatus.PUBLISHED
            )
            db_session.add(course)
        db_session.commit()

        # Test page 1
        response = client.get("/courses/?page=1&page_size=3")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["courses"]) == 3
        assert data["page"] == 1
        assert data["page_size"] == 3

        # Test page 2
        response = client.get("/courses/?page=2&page_size=3")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["courses"]) >= 1


# ============================================================================
# Public Course Detail Tests
# ============================================================================

class TestPublicCourseDetail:
    """Tests for public course detail endpoint."""

    def test_get_published_course_by_slug(self, client, sample_course):
        """Test getting published course by slug."""
        response = client.get(f"/courses/{sample_course.slug}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["slug"] == "sample-course"
        assert data["title"] == "Sample Course"
        assert data["description"] == "A sample course for testing"
        assert float(data["price"]) == 99.99
        assert data["status"] == "published"
        assert "sections" in data

    def test_get_draft_course_returns_404(self, client, draft_course):
        """Test that draft courses cannot be accessed publicly."""
        response = client.get(f"/courses/{draft_course.slug}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_nonexistent_course_returns_404(self, client):
        """Test getting non-existent course returns 404."""
        response = client.get("/courses/nonexistent-slug")

        assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Admin Course Creation Tests
# ============================================================================

class TestAdminCourseCreation:
    """Tests for admin course creation."""

    def test_create_course_success(self, client, admin_token):
        """Test successful course creation by admin."""
        response = client.post(
            "/admin/courses",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "New Course",
                "description": "A brand new course",
                "price": 149.99,
                "status": "draft"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "New Course"
        assert data["slug"] == "new-course"  # Auto-generated slug
        assert data["description"] == "A brand new course"
        assert float(data["price"]) == 149.99
        assert data["status"] == "draft"
        assert "id" in data
        assert "creator_id" in data

    def test_create_course_generates_unique_slug(self, client, admin_token, sample_course):
        """Test that duplicate titles generate unique slugs."""
        # Create course with same title as existing
        response = client.post(
            "/admin/courses",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Sample Course",  # Same as existing
                "description": "Another course",
                "status": "draft"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Sample Course"
        assert data["slug"] != "sample-course"  # Should be unique
        assert data["slug"].startswith("sample-course-")

    def test_create_course_without_auth_fails(self, client):
        """Test that unauthenticated users cannot create courses."""
        response = client.post(
            "/admin/courses",
            json={
                "title": "Unauthorized Course",
                "status": "draft"
            }
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_course_as_student_fails(self, client, student_token):
        """Test that students cannot create courses."""
        response = client.post(
            "/admin/courses",
            headers={"Authorization": f"Bearer {student_token}"},
            json={
                "title": "Student Course",
                "status": "draft"
            }
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


# ============================================================================
# Admin Course Management Tests
# ============================================================================

class TestAdminCourseManagement:
    """Tests for admin course management."""

    def test_list_all_courses_includes_drafts(self, client, admin_token, sample_course, draft_course):
        """Test that admin can see both published and draft courses."""
        response = client.get(
            "/admin/courses",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        slugs = [course["slug"] for course in data["courses"]]
        assert "sample-course" in slugs
        assert "draft-course" in slugs

    def test_get_course_detail_by_id(self, client, admin_token, sample_course):
        """Test getting course detail by ID."""
        response = client.get(
            f"/admin/courses/{sample_course.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(sample_course.id)
        assert data["title"] == sample_course.title
        assert "sections" in data

    def test_update_course(self, client, admin_token, sample_course):
        """Test updating course fields."""
        response = client.put(
            f"/admin/courses/{sample_course.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Updated Course Title",
                "price": 199.99
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Course Title"
        assert float(data["price"]) == 199.99

    def test_publish_course(self, client, admin_token, draft_course):
        """Test publishing a draft course."""
        response = client.put(
            f"/admin/courses/{draft_course.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "status": "published"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "published"

    def test_unpublish_course(self, client, admin_token, sample_course):
        """Test unpublishing a course."""
        response = client.put(
            f"/admin/courses/{sample_course.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "status": "draft"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "draft"

    def test_delete_course(self, client, admin_token, draft_course):
        """Test deleting a course."""
        response = client.delete(
            f"/admin/courses/{draft_course.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify course is deleted
        response = client.get(
            f"/admin/courses/{draft_course.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Section Management Tests
# ============================================================================

class TestSectionManagement:
    """Tests for course section management."""

    def test_create_section(self, client, admin_token, sample_course):
        """Test creating a section in a course."""
        response = client.post(
            f"/admin/courses/{sample_course.id}/sections",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Section 1: Introduction",
                "order_index": 0
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Section 1: Introduction"
        assert data["order_index"] == 0
        assert data["course_id"] == str(sample_course.id)
        assert "id" in data

    def test_create_section_invalid_course(self, client, admin_token):
        """Test creating section with invalid course ID."""
        import uuid
        fake_id = uuid.uuid4()

        response = client.post(
            f"/admin/courses/{fake_id}/sections",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Invalid Section",
                "order_index": 0
            }
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_section(self, client, admin_token, sample_course, db_session):
        """Test updating a section."""
        # Create section
        section = Section(
            course_id=sample_course.id,
            title="Original Title",
            order_index=0
        )
        db_session.add(section)
        db_session.commit()
        db_session.refresh(section)

        # Update section
        response = client.put(
            f"/admin/sections/{section.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Updated Section Title",
                "order_index": 1
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Section Title"
        assert data["order_index"] == 1

    def test_delete_section(self, client, admin_token, sample_course, db_session):
        """Test deleting a section."""
        # Create section
        section = Section(
            course_id=sample_course.id,
            title="Section to Delete",
            order_index=0
        )
        db_session.add(section)
        db_session.commit()
        db_session.refresh(section)

        # Delete section
        response = client.delete(
            f"/admin/sections/{section.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT


# ============================================================================
# Lesson Management Tests
# ============================================================================

class TestLessonManagement:
    """Tests for course lesson management."""

    def test_create_lesson(self, client, admin_token, sample_course, db_session):
        """Test creating a lesson in a section."""
        # Create section first
        section = Section(
            course_id=sample_course.id,
            title="Section 1",
            order_index=0
        )
        db_session.add(section)
        db_session.commit()
        db_session.refresh(section)

        # Create lesson
        response = client.post(
            f"/admin/sections/{section.id}/lessons",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Lesson 1: Getting Started",
                "content_type": "video",
                "file_url": "https://example.com/video.mp4",
                "order_index": 0,
                "is_preview": True
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Lesson 1: Getting Started"
        assert data["content_type"] == "video"
        assert data["file_url"] == "https://example.com/video.mp4"
        assert data["order_index"] == 0
        assert data["is_preview"] is True
        assert data["section_id"] == str(section.id)

    def test_create_lesson_all_content_types(self, client, admin_token, sample_course, db_session):
        """Test creating lessons with different content types."""
        section = Section(
            course_id=sample_course.id,
            title="Section 1",
            order_index=0
        )
        db_session.add(section)
        db_session.commit()
        db_session.refresh(section)

        content_types = ["video", "pdf", "text", "quiz"]

        for idx, content_type in enumerate(content_types):
            response = client.post(
                f"/admin/sections/{section.id}/lessons",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={
                    "title": f"Lesson {idx + 1}",
                    "content_type": content_type,
                    "order_index": idx,
                    "is_preview": False
                }
            )

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["content_type"] == content_type

    def test_update_lesson(self, client, admin_token, sample_course, db_session):
        """Test updating a lesson."""
        # Create section and lesson
        section = Section(
            course_id=sample_course.id,
            title="Section 1",
            order_index=0
        )
        db_session.add(section)
        db_session.commit()

        lesson = Lesson(
            section_id=section.id,
            title="Original Lesson",
            content_type=LessonContentType.VIDEO,
            order_index=0,
            is_preview=False
        )
        db_session.add(lesson)
        db_session.commit()
        db_session.refresh(lesson)

        # Update lesson
        response = client.put(
            f"/admin/lessons/{lesson.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Updated Lesson Title",
                "is_preview": True,
                "order_index": 1
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Lesson Title"
        assert data["is_preview"] is True
        assert data["order_index"] == 1

    def test_delete_lesson(self, client, admin_token, sample_course, db_session):
        """Test deleting a lesson."""
        # Create section and lesson
        section = Section(
            course_id=sample_course.id,
            title="Section 1",
            order_index=0
        )
        db_session.add(section)
        db_session.commit()

        lesson = Lesson(
            section_id=section.id,
            title="Lesson to Delete",
            content_type=LessonContentType.VIDEO,
            order_index=0,
            is_preview=False
        )
        db_session.add(lesson)
        db_session.commit()
        db_session.refresh(lesson)

        # Delete lesson
        response = client.delete(
            f"/admin/lessons/{lesson.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT


# ============================================================================
# Authorization Tests
# ============================================================================

class TestAuthorization:
    """Tests for endpoint authorization."""

    def test_student_cannot_access_admin_endpoints(self, client, student_token, sample_course):
        """Test that students cannot access admin endpoints."""
        # Try to create course
        response = client.post(
            "/admin/courses",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"title": "Unauthorized", "status": "draft"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Try to update course
        response = client.put(
            f"/admin/courses/{sample_course.id}",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"title": "Hacked"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Try to delete course
        response = client.delete(
            f"/admin/courses/{sample_course.id}",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_access_admin_endpoints(self, client, sample_course):
        """Test that unauthenticated users cannot access admin endpoints."""
        # Try to list all courses (including drafts)
        response = client.get("/admin/courses")
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Try to create course
        response = client.post(
            "/admin/courses",
            json={"title": "Unauthorized", "status": "draft"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ============================================================================
# Edge Cases and Validation Tests
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and validation."""

    def test_create_course_with_special_characters_in_title(self, client, admin_token):
        """Test slug generation with special characters."""
        response = client.post(
            "/admin/courses",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "C++ Programming: From Zero to Hero!",
                "status": "draft"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        # Slug should be cleaned of special characters
        assert "c" in data["slug"].lower()
        assert "programming" in data["slug"].lower()

    def test_create_course_with_negative_price_fails(self, client, admin_token):
        """Test that negative prices are rejected."""
        response = client.post(
            "/admin/courses",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Free Course",
                "price": -10.00,
                "status": "draft"
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_course_with_duplicate_slug(self, client, admin_token, sample_course, draft_course):
        """Test that updating to a duplicate slug fails."""
        response = client.put(
            f"/admin/courses/{draft_course.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "slug": sample_course.slug  # Duplicate slug
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()

    def test_course_with_sections_and_lessons_ordering(self, client, admin_token, sample_course, db_session):
        """Test that sections and lessons are properly ordered."""
        # Create sections out of order
        section2 = Section(course_id=sample_course.id, title="Section 2", order_index=1)
        section1 = Section(course_id=sample_course.id, title="Section 1", order_index=0)
        db_session.add(section2)
        db_session.add(section1)
        db_session.commit()

        # Create lessons out of order
        lesson2 = Lesson(
            section_id=section1.id,
            title="Lesson 2",
            content_type=LessonContentType.VIDEO,
            order_index=1,
            is_preview=False
        )
        lesson1 = Lesson(
            section_id=section1.id,
            title="Lesson 1",
            content_type=LessonContentType.VIDEO,
            order_index=0,
            is_preview=False
        )
        db_session.add(lesson2)
        db_session.add(lesson1)
        db_session.commit()

        # Get course detail
        response = client.get(f"/courses/{sample_course.slug}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify sections are ordered
        assert len(data["sections"]) == 2
        assert data["sections"][0]["title"] == "Section 1"
        assert data["sections"][1]["title"] == "Section 2"

        # Verify lessons are ordered
        assert len(data["sections"][0]["lessons"]) == 2
        assert data["sections"][0]["lessons"][0]["title"] == "Lesson 1"
        assert data["sections"][0]["lessons"][1]["title"] == "Lesson 2"
