import { apiClient } from '@/lib/axios'

export interface User { id: string; full_name: string; email: string; role: string; is_active: boolean; is_verified: boolean; created_at: string }
export interface UsersResponse { data: User[]; total: number; page: number; page_size: number; total_pages: number }
export interface CreateUserPayload { full_name: string; email: string; password: string; role: string }

export const userService = {
  list: (params?: { page?: number; page_size?: number }) =>
    apiClient.get<UsersResponse>('/users', { params }).then((r) => r.data),

  get: (id: string) =>
    apiClient.get<{ data: User }>(`/users/${id}`).then((r) => r.data.data),

  create: (data: CreateUserPayload) =>
    apiClient.post<{ data: User }>('/users', data).then((r) => r.data.data),

  update: (id: string, data: Partial<{ full_name: string; role: string; is_active: boolean }>) =>
    apiClient.put<{ data: User }>(`/users/${id}`, data).then((r) => r.data.data),

  delete: (id: string) => apiClient.delete(`/users/${id}`),

  changePassword: (current_password: string, new_password: string) =>
    apiClient.post('/users/me/change-password', { current_password, new_password }),
}
