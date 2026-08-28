import re
import uuid
from typing import Optional, Tuple, List
from fastapi import HTTPException, status

from app.repositories.course_repo import CourseRepository
from app.schemas.course import (
    CourseCreate,
    CourseUpdate,
    SectionCreate,
    SectionUpdate,
    LessonCreate,
    LessonUpdate,
    CourseListResponse,
    CourseListItem,
)
from app.db.models.course import Course
from app.db.models.section import Section
from app.db.models.lesson import Lesson
from app.db.models.user import User


class CourseService:
    """Service layer for course business logic."""

    def __init__(self, repository: CourseRepository):
        self.repository = repository

    # ============================================================================
    # Utility Methods
    # ============================================================================

    @staticmethod
    def generate_slug(title: str) -> str:
        """
        Generate a URL-friendly slug from a title.

        Args:
            title: The course title

        Returns:
            A slugified version of the title
        """
        # Convert to lowercase
        slug = title.lower()

        # Replace spaces and special characters with hyphens
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)

        # Remove leading/trailing hyphens
        slug = slug.strip('-')

        # Ensure slug is not empty
        if not slug:
            slug = "course"

        return slug

    def ensure_unique_slug(self, base_slug: str, exclude_course_id: Optional[uuid.UUID] = None) -> str:
        """
        Ensure slug is unique by appending a number if necessary.

        Args:
            base_slug: The base slug to check
            exclude_course_id: Optional course ID to exclude from uniqueness check

        Returns:
            A unique slug
        """
        slug = base_slug
        counter = 1

        while not self.repository.is_slug_available(slug, exclude_course_id):
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def get_creator_id_for_user(self, user: User) -> uuid.UUID:
        """
        Get the creator ID for a user.

        Args:
            user: The user object

        Returns:
            The creator ID

        Raises:
            HTTPException: If user doesn't have a creator profile
        """
        if not user.creator:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have a creator profile"
            )

        return user.creator.id

    # ============================================================================
    # Course Operations
    # ============================================================================

    def create_course(self, course_data: CourseCreate, current_user: User) -> Course:
        """
        Create a new course.

        Args:
            course_data: Course creation data
            current_user: The authenticated admin user

        Returns:
            The created course

        Raises:
            HTTPException: If user doesn't have creator profile
        """
        # Get or validate creator
        creator_id = self.get_creator_id_for_user(current_user)

        # Generate unique slug
        base_slug = self.generate_slug(course_data.title)
        unique_slug = self.ensure_unique_slug(base_slug)

        # Create course
        course = self.repository.create_course(
            course_data=course_data,
            creator_id=creator_id,
            slug=unique_slug
        )

        return course

    def get_course_by_id(self, course_id: uuid.UUID) -> Course:
        """
        Get course by ID.

        Args:
            course_id: The course ID

        Returns:
            The course

        Raises:
            HTTPException: If course not found
        """
        course = self.repository.get_course_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        return course

    def get_course_with_details(self, course_id: uuid.UUID) -> Course:
        """
        Get course with sections and lessons.

        Args:
            course_id: The course ID

        Returns:
            The course with sections and lessons

        Raises:
            HTTPException: If course not found
        """
        course = self.repository.get_course_with_sections_and_lessons(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        # Sort sections and lessons by order_index
        course.sections.sort(key=lambda s: s.order_index)
        for section in course.sections:
            section.lessons.sort(key=lambda l: l.order_index)

        return course

    def get_published_course_by_slug(self, slug: str) -> Course:
        """
        Get published course by slug with sections and lessons.

        Args:
            slug: The course slug

        Returns:
            The published course with sections and lessons

        Raises:
            HTTPException: If course not found or not published
        """
        course = self.repository.get_published_course_by_slug(slug)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        # Sort sections and lessons by order_index
        course.sections.sort(key=lambda s: s.order_index)
        for section in course.sections:
            section.lessons.sort(key=lambda l: l.order_index)

        return course

    def get_all_courses(self, page: int = 1, page_size: int = 20) -> CourseListResponse:
        """
        Get all courses with pagination (admin only).

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            Paginated course list
        """
        skip = (page - 1) * page_size
        courses, total = self.repository.get_all_courses(skip=skip, limit=page_size)

        total_pages = (total + page_size - 1) // page_size

        return CourseListResponse(
            courses=[CourseListItem.model_validate(course) for course in courses],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    def get_published_courses(self, page: int = 1, page_size: int = 20) -> CourseListResponse:
        """
        Get published courses with pagination (public).

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            Paginated course list
        """
        skip = (page - 1) * page_size
        courses, total = self.repository.get_published_courses(skip=skip, limit=page_size)

        total_pages = (total + page_size - 1) // page_size

        return CourseListResponse(
            courses=[CourseListItem.model_validate(course) for course in courses],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    def update_course(self, course_id: uuid.UUID, course_data: CourseUpdate) -> Course:
        """
        Update a course.

        Args:
            course_id: The course ID
            course_data: Course update data

        Returns:
            The updated course

        Raises:
            HTTPException: If course not found or slug already exists
        """
        course = self.get_course_by_id(course_id)

        # If slug is being updated, ensure it's unique
        if course_data.slug is not None:
            if not self.repository.is_slug_available(course_data.slug, exclude_course_id=course_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Slug already exists"
                )

        return self.repository.update_course(course, course_data)

    def delete_course(self, course_id: uuid.UUID) -> None:
        """
        Delete a course.

        Args:
            course_id: The course ID

        Raises:
            HTTPException: If course not found
        """
        course = self.get_course_by_id(course_id)
        self.repository.delete_course(course)

    # ============================================================================
    # Section Operations
    # ============================================================================

    def create_section(self, course_id: uuid.UUID, section_data: SectionCreate) -> Section:
        """
        Create a new section.

        Args:
            course_id: The course ID
            section_data: Section creation data

        Returns:
            The created section

        Raises:
            HTTPException: If course not found
        """
        # Verify course exists
        self.get_course_by_id(course_id)

        return self.repository.create_section(course_id, section_data)

    def get_section_by_id(self, section_id: uuid.UUID) -> Section:
        """
        Get section by ID.

        Args:
            section_id: The section ID

        Returns:
            The section

        Raises:
            HTTPException: If section not found
        """
        section = self.repository.get_section_by_id(section_id)
        if not section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Section not found"
            )
        return section

    def update_section(self, section_id: uuid.UUID, section_data: SectionUpdate) -> Section:
        """
        Update a section.

        Args:
            section_id: The section ID
            section_data: Section update data

        Returns:
            The updated section

        Raises:
            HTTPException: If section not found
        """
        section = self.get_section_by_id(section_id)
        return self.repository.update_section(section, section_data)

    def delete_section(self, section_id: uuid.UUID) -> None:
        """
        Delete a section.

        Args:
            section_id: The section ID

        Raises:
            HTTPException: If section not found
        """
        section = self.get_section_by_id(section_id)
        self.repository.delete_section(section)

    # ============================================================================
    # Lesson Operations
    # ============================================================================

    def create_lesson(self, section_id: uuid.UUID, lesson_data: LessonCreate) -> Lesson:
        """
        Create a new lesson.

        Args:
            section_id: The section ID
            lesson_data: Lesson creation data

        Returns:
            The created lesson

        Raises:
            HTTPException: If section not found
        """
        # Verify section exists
        self.get_section_by_id(section_id)

        return self.repository.create_lesson(section_id, lesson_data)

    def get_lesson_by_id(self, lesson_id: uuid.UUID) -> Lesson:
        """
        Get lesson by ID.

        Args:
            lesson_id: The lesson ID

        Returns:
            The lesson

        Raises:
            HTTPException: If lesson not found
        """
        lesson = self.repository.get_lesson_by_id(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        return lesson

    def update_lesson(self, lesson_id: uuid.UUID, lesson_data: LessonUpdate) -> Lesson:
        """
        Update a lesson.

        Args:
            lesson_id: The lesson ID
            lesson_data: Lesson update data

        Returns:
            The updated lesson

        Raises:
            HTTPException: If lesson not found
        """
        lesson = self.get_lesson_by_id(lesson_id)
        return self.repository.update_lesson(lesson, lesson_data)

    def delete_lesson(self, lesson_id: uuid.UUID) -> None:
        """
        Delete a lesson.

        Args:
            lesson_id: The lesson ID

        Raises:
            HTTPException: If lesson not found
        """
        lesson = self.get_lesson_by_id(lesson_id)
        self.repository.delete_lesson(lesson)
