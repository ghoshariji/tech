import { apiClient } from '@/lib/axios'

export interface AuditLog {
  id: string; user_id?: string; action: string; resource: string
  resource_id?: string; ip_address?: string; user_agent?: string
  old_values?: Record<string, unknown>; new_values?: Record<string, unknown>
  status: string; error_message?: string; created_at: string
}
export interface AuditLogsResponse { data: AuditLog[]; total: number; page: number; page_size: number; total_pages: number }

export const auditService = {
  list: (params?: { page?: number; page_size?: number; user_id?: string; action?: string; resource?: string }) =>
    apiClient.get<AuditLogsResponse>('/audit', { params }).then((r) => r.data),
}
