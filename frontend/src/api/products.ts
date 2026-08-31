import { apiClient } from './client';
import { ProductListResponse, Product, CreateProductRequest, UpdateProductRequest } from '../types/product';

export const productsAPI = {
  // Public endpoints
  getPublishedProducts: async (page = 1, pageSize = 20): Promise<ProductListResponse> => {
    const response = await apiClient.get('/products', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  getProductBySlug: async (slug: string): Promise<Product> => {
    const response = await apiClient.get(`/products/${slug}`);
    return response.data;
  },

  // Admin endpoints
  createProduct: async (data: CreateProductRequest): Promise<Product> => {
    const response = await apiClient.post('/admin/products', data);
    return response.data;
  },

  updateProduct: async (id: string, data: UpdateProductRequest): Promise<Product> => {
    const response = await apiClient.put(`/admin/products/${id}`, data);
    return response.data;
  },

  deleteProduct: async (id: string): Promise<void> => {
    await apiClient.delete(`/admin/products/${id}`);
  },

  // Get product by ID (admin)
  getProductById: async (id: string): Promise<Product> => {
    const response = await apiClient.get(`/admin/products/${id}`);
    return response.data;
  },
};
