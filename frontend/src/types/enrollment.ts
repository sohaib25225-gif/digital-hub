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
  course_price: number;
}

export interface CreateEnrollmentRequest {
  course_id: string;
}
