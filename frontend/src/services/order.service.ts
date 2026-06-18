import { apiClient } from '@/lib/axios'
import type { Customer } from './customer.service'
import type { Product } from './product.service'

export type OrderStatus = 'PENDING' | 'CONFIRMED' | 'SHIPPED' | 'DELIVERED' | 'CANCELLED'

export interface OrderItem { id: string; product_id: string; quantity: number; price: string; product?: Product }
export interface Order {
  id: string; order_number: string; customer_id: string
  status: OrderStatus; total_amount: string; notes?: string
  customer?: Customer; items: OrderItem[]; created_at: string; updated_at: string
}
export interface OrdersResponse { data: Order[]; total: number; page: number; page_size: number; total_pages: number }
export interface CreateOrderPayload { customer_id: string; items: { product_id: string; quantity: number }[]; notes?: string }

export const orderService = {
  list: (params?: { page?: number; page_size?: number; search?: string; status?: string; customer_id?: string }) =>
    apiClient.get<OrdersResponse>('/orders', { params }).then((r) => r.data),

  get: (id: string) =>
    apiClient.get<{ data: Order }>(`/orders/${id}`).then((r) => r.data.data),

  create: (data: CreateOrderPayload) =>
    apiClient.post<{ data: Order }>('/orders', data).then((r) => r.data.data),

  updateStatus: (id: string, status: OrderStatus, notes?: string) =>
    apiClient.put<{ data: Order }>(`/orders/${id}`, { status, notes }).then((r) => r.data.data),

  cancel: (id: string) => apiClient.delete(`/orders/${id}`),

  exportCsv: () =>
    apiClient.get('/orders/export/csv', { responseType: 'blob' }).then((r) => r.data),
}
