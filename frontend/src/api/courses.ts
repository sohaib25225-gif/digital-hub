import { apiClient } from './client';
import { CourseListResponse, CourseWithSections, CreateCourseRequest, UpdateCourseRequest } from '../types/course';

export const coursesAPI = {
  // Public endpoints
  getPublishedCourses: async (page = 1, pageSize = 20): Promise<CourseListResponse> => {
    const response = await apiClient.get('/courses', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  getCourseBySlug: async (slug: string): Promise<CourseWithSections> => {
    const response = await apiClient.get(`/courses/${slug}`);
    return response.data;
  },

  // Admin endpoints
  createCourse: async (data: CreateCourseRequest): Promise<CourseWithSections> => {
    const response = await apiClient.post('/admin/courses', data);
    return response.data;
  },

  updateCourse: async (id: string, data: UpdateCourseRequest): Promise<CourseWithSections> => {
    const response = await apiClient.put(`/admin/courses/${id}`, data);
    return response.data;
  },

  deleteCourse: async (id: string): Promise<void> => {
    await apiClient.delete(`/admin/courses/${id}`);
  },

  // Get course by ID (admin)
  getCourseById: async (id: string): Promise<CourseWithSections> => {
    const response = await apiClient.get(`/admin/courses/${id}`);
    return response.data;
  },
};
