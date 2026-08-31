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

export interface CreateCourseRequest {
  title: string;
  description: string;
  price: number;
  thumbnail_url?: string;
  status: 'draft' | 'published';
}

export interface UpdateCourseRequest {
  title?: string;
  description?: string;
  price?: number;
  thumbnail_url?: string;
  status?: 'draft' | 'published';
}
