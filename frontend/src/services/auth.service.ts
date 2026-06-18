import { apiClient } from '@/lib/axios'

export interface LoginPayload { email: string; password: string }
export interface RegisterPayload { full_name: string; email: string; password: string; role?: string }
export interface TokenResponse { access_token: string; refresh_token: string; token_type: string; expires_in: number }
export interface UserResponse { id: string; full_name: string; email: string; role: string; is_active: boolean; is_verified: boolean; created_at: string; updated_at: string }

export const authService = {
  login: (data: LoginPayload) =>
    apiClient.post<{ data: TokenResponse }>('/auth/login', data).then((r) => r.data.data),

  register: (data: RegisterPayload) =>
    apiClient.post<{ data: UserResponse }>('/auth/register', data).then((r) => r.data.data),

  logout: () => apiClient.post('/auth/logout'),

  me: () => apiClient.get<{ data: UserResponse }>('/auth/me').then((r) => r.data.data),

  refreshToken: (refresh_token: string) =>
    apiClient.post<{ data: TokenResponse }>('/auth/refresh', { refresh_token }).then((r) => r.data.data),

  forgotPassword: (email: string) =>
    apiClient.post('/auth/forgot-password', { email }),

  resetPassword: (token: string, new_password: string) =>
    apiClient.post('/auth/reset-password', { token, new_password }),
}
