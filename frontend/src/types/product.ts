export interface Product {
  id: string;
  creator_id: string;
  title: string;
  slug: string;
  description: string;
  price: number;
  file_url: string;
  thumbnail_url: string | null;
  status: 'draft' | 'published';
  created_at: string;
}

export interface ProductListResponse {
  products: Product[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface CreateProductRequest {
  title: string;
  description: string;
  price: number;
  file_url: string;
  thumbnail_url?: string;
  status: 'draft' | 'published';
}

export interface UpdateProductRequest {
  title?: string;
  description?: string;
  price?: number;
  file_url?: string;
  thumbnail_url?: string;
  status?: 'draft' | 'published';
}
