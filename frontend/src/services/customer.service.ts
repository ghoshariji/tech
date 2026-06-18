import { apiClient } from '@/lib/axios'

export interface Customer {
  id: string; full_name: string; email: string
  phone?: string; address?: string; created_at: string; updated_at: string
}
export interface CustomersResponse { data: Customer[]; total: number; page: number; page_size: number; total_pages: number }
export interface CreateCustomerPayload { full_name: string; email: string; phone?: string; address?: string }
export type UpdateCustomerPayload = Partial<CreateCustomerPayload>

export const customerService = {
  list: (params?: { page?: number; page_size?: number; search?: string }) =>
    apiClient.get<CustomersResponse>('/customers', { params }).then((r) => r.data),

  get: (id: string) =>
    apiClient.get<{ data: Customer }>(`/customers/${id}`).then((r) => r.data.data),

  create: (data: CreateCustomerPayload) =>
    apiClient.post<{ data: Customer }>('/customers', data).then((r) => r.data.data),

  update: (id: string, data: UpdateCustomerPayload) =>
    apiClient.put<{ data: Customer }>(`/customers/${id}`, data).then((r) => r.data.data),

  delete: (id: string) => apiClient.delete(`/customers/${id}`),
}
