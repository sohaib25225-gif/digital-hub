import { apiClient } from './client';
import { PurchaseWithDetails, CreatePurchaseRequest, CreatePurchaseResponse } from '../types/purchase';

export const purchasesAPI = {
  createPurchase: async (data: CreatePurchaseRequest): Promise<CreatePurchaseResponse> => {
    const response = await apiClient.post('/me/purchases', data);
    return response.data;
  },

  getMyPurchases: async (): Promise<PurchaseWithDetails[]> => {
    const response = await apiClient.get('/me/purchases');
    return response.data;
  },

  getPurchase: async (purchaseId: string): Promise<PurchaseWithDetails> => {
    const response = await apiClient.get(`/me/purchases/${purchaseId}`);
    return response.data;
  },
};
