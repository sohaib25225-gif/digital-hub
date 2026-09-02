export interface Purchase {
  id: string;
  user_id: string;
  course_id: string | null;
  product_id: string | null;
  amount: number;
  currency: string;
  status: 'pending' | 'completed' | 'failed';
  created_at: string;
  payment_provider_tx_id?: string | null;
  payment_method?: string | null;
  updated_at?: string | null;
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

// Phase 6 Stage 7: Payment session response types
export interface NextActions {
  CYBERSOURCE?: {
    kind: string;
    capture_context?: string; // JWT if provided
    [key: string]: any;
  };
  [key: string]: any;
}

export interface CreatePurchaseResponse {
  purchase: Purchase;
  tracker_token: string;
  payment_provider: string;
  payment_state: string;
  intent?: string;
  mode?: string;
  next_actions?: NextActions;
  message: string;
}
