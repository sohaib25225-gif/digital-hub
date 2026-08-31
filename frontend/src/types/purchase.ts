export interface Purchase {
  id: string;
  user_id: string;
  course_id: string | null;
  product_id: string | null;
  amount: number;
  currency: string;
  status: 'pending' | 'completed' | 'failed';
  created_at: string;
}

export interface PurchaseWithDetails extends Purchase {
  item_title: string;
  item_type: 'course' | 'product';
}

export interface CreatePurchaseRequest {
  course_id?: string;
  product_id?: string;
  amount: number;
  currency: string;
}
