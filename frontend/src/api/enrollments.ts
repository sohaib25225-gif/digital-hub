import { apiClient } from './client';
import { EnrollmentWithCourse, CreateEnrollmentRequest } from '../types/enrollment';

export const enrollmentsAPI = {
  enrollInCourse: async (data: CreateEnrollmentRequest): Promise<void> => {
    await apiClient.post(`/me/enrollments/${data.course_id}`);
  },

  getMyEnrollments: async (): Promise<EnrollmentWithCourse[]> => {
    const response = await apiClient.get('/me/enrollments');
    return response.data;
  },
};
