from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
import uuid

from app.db.models.course import Course, CourseStatus
from app.db.models.section import Section
from app.db.models.lesson import Lesson
from app.schemas.course import CourseCreate, CourseUpdate, SectionCreate, SectionUpdate, LessonCreate, LessonUpdate


class CourseRepository:
    """Repository for course database operations."""

    def __init__(self, db: Session):
        self.db = db

    # ============================================================================
    # Course Operations
    # ============================================================================

    def create_course(self, course_data: CourseCreate, creator_id: uuid.UUID, slug: str) -> Course:
        """Create a new course."""
        course = Course(
            creator_id=creator_id,
            title=course_data.title,
            slug=slug,
            description=course_data.description,
            thumbnail_url=course_data.thumbnail_url,
            price=course_data.price,
            status=course_data.status,
        )
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return course

    def get_course_by_id(self, course_id: uuid.UUID) -> Optional[Course]:
        """Get course by ID."""
        return self.db.query(Course).filter(Course.id == course_id).first()

    def get_course_by_slug(self, slug: str) -> Optional[Course]:
        """Get course by slug."""
        return self.db.query(Course).filter(Course.slug == slug).first()

    def get_course_with_sections_and_lessons(self, course_id: uuid.UUID) -> Optional[Course]:
        """Get course with all sections and lessons loaded."""
        return (
            self.db.query(Course)
            .options(
                joinedload(Course.sections).joinedload(Section.lessons)
            )
            .filter(Course.id == course_id)
            .first()
        )

    def get_published_course_by_slug(self, slug: str) -> Optional[Course]:
        """Get published course by slug with sections and lessons."""
        return (
            self.db.query(Course)
            .options(
                joinedload(Course.sections).joinedload(Section.lessons)
            )
            .filter(Course.slug == slug, Course.status == CourseStatus.PUBLISHED)
            .first()
        )

    def get_all_courses(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[CourseStatus] = None
    ) -> Tuple[List[Course], int]:
        """
        Get all courses with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Optional status filter

        Returns:
            Tuple of (courses list, total count)
        """
        query = self.db.query(Course)

        if status:
            query = query.filter(Course.status == status)

        total = query.count()
        courses = query.order_by(Course.created_at.desc()).offset(skip).limit(limit).all()

        return courses, total

    def get_published_courses(self, skip: int = 0, limit: int = 100) -> Tuple[List[Course], int]:
        """Get published courses with pagination."""
        return self.get_all_courses(skip=skip, limit=limit, status=CourseStatus.PUBLISHED)

    def update_course(self, course: Course, course_data: CourseUpdate) -> Course:
        """Update course fields."""
        update_data = course_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(course, field, value)

        self.db.commit()
        self.db.refresh(course)
        return course

    def delete_course(self, course: Course) -> None:
        """Delete a course."""
        self.db.delete(course)
        self.db.commit()

    def is_slug_available(self, slug: str, exclude_course_id: Optional[uuid.UUID] = None) -> bool:
        """Check if a slug is available."""
        query = self.db.query(Course).filter(Course.slug == slug)

        if exclude_course_id:
            query = query.filter(Course.id != exclude_course_id)

        return query.first() is None

    # ============================================================================
    # Section Operations
    # ============================================================================

    def create_section(self, course_id: uuid.UUID, section_data: SectionCreate) -> Section:
        """Create a new section."""
        section = Section(
            course_id=course_id,
            title=section_data.title,
            order_index=section_data.order_index,
        )
        self.db.add(section)
        self.db.commit()
        self.db.refresh(section)
        return section

    def get_section_by_id(self, section_id: uuid.UUID) -> Optional[Section]:
        """Get section by ID."""
        return self.db.query(Section).filter(Section.id == section_id).first()

    def get_sections_by_course(self, course_id: uuid.UUID) -> List[Section]:
        """Get all sections for a course."""
        return (
            self.db.query(Section)
            .filter(Section.course_id == course_id)
            .order_by(Section.order_index)
            .all()
        )

    def update_section(self, section: Section, section_data: SectionUpdate) -> Section:
        """Update section fields."""
        update_data = section_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(section, field, value)

        self.db.commit()
        self.db.refresh(section)
        return section

    def delete_section(self, section: Section) -> None:
        """Delete a section."""
        self.db.delete(section)
        self.db.commit()

    # ============================================================================
    # Lesson Operations
    # ============================================================================

    def create_lesson(self, section_id: uuid.UUID, lesson_data: LessonCreate) -> Lesson:
        """Create a new lesson."""
        lesson = Lesson(
            section_id=section_id,
            title=lesson_data.title,
            content_type=lesson_data.content_type,
            file_url=lesson_data.file_url,
            order_index=lesson_data.order_index,
            is_preview=lesson_data.is_preview,
        )
        self.db.add(lesson)
        self.db.commit()
        self.db.refresh(lesson)
        return lesson

    def get_lesson_by_id(self, lesson_id: uuid.UUID) -> Optional[Lesson]:
        """Get lesson by ID."""
        return self.db.query(Lesson).filter(Lesson.id == lesson_id).first()

    def get_lessons_by_section(self, section_id: uuid.UUID) -> List[Lesson]:
        """Get all lessons for a section."""
        return (
            self.db.query(Lesson)
            .filter(Lesson.section_id == section_id)
            .order_by(Lesson.order_index)
            .all()
        )

    def update_lesson(self, lesson: Lesson, lesson_data: LessonUpdate) -> Lesson:
        """Update lesson fields."""
        update_data = lesson_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(lesson, field, value)

        self.db.commit()
        self.db.refresh(lesson)
        return lesson

    def delete_lesson(self, lesson: Lesson) -> None:
        """Delete a lesson."""
        self.db.delete(lesson)
        self.db.commit()
