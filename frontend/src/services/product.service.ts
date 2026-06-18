import { apiClient } from '@/lib/axios'

export interface Product {
  id: string; name: string; sku: string; description?: string
  price: string; quantity: number; reorder_level: number
  category?: string; is_low_stock: boolean; created_at: string; updated_at: string
}
export interface ProductsResponse { data: Product[]; total: number; page: number; page_size: number; total_pages: number }
export interface CreateProductPayload { name: string; sku: string; description?: string; price: string; quantity: number; reorder_level?: number; category?: string }
export type UpdateProductPayload = Partial<CreateProductPayload>

export interface ProductListParams {
  page?: number; page_size?: number; search?: string; category?: string
  min_price?: string; max_price?: string; low_stock_only?: boolean
  sort_by?: string; sort_order?: 'asc' | 'desc'
}

export const productService = {
  list: (params?: ProductListParams) =>
    apiClient.get<ProductsResponse>('/products', { params }).then((r) => r.data),

  get: (id: string) =>
    apiClient.get<{ data: Product }>(`/products/${id}`).then((r) => r.data.data),

  create: (data: CreateProductPayload) =>
    apiClient.post<{ data: Product }>('/products', data).then((r) => r.data.data),

  update: (id: string, data: UpdateProductPayload) =>
    apiClient.put<{ data: Product }>(`/products/${id}`, data).then((r) => r.data.data),

  delete: (id: string) => apiClient.delete(`/products/${id}`),

  exportCsv: () =>
    apiClient.get('/products/export/csv', { responseType: 'blob' }).then((r) => r.data),
}
