import { apiClient } from './client';
import { PurchaseWithDetails, CreatePurchaseRequest, Purchase } from '../types/purchase';

export const purchasesAPI = {
  createPurchase: async (data: CreatePurchaseRequest): Promise<Purchase> => {
    const response = await apiClient.post('/me/purchases', data);
    return response.data;
  },

  getMyPurchases: async (): Promise<PurchaseWithDetails[]> => {
    const response = await apiClient.get('/me/purchases');
    return response.data;
  },
};
