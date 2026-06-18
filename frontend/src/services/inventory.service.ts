import { apiClient } from '@/lib/axios'
import type { Product } from './product.service'

export type MovementType = 'IN' | 'OUT' | 'ADJUSTMENT' | 'RETURN'
export interface InventoryMovement {
  id: string; product_id: string; movement_type: MovementType
  quantity: number; quantity_before: number; quantity_after: number
  reason?: string; performed_by?: string; created_at: string
}
export interface MovementsResponse { data: InventoryMovement[]; total: number; page: number; page_size: number; total_pages: number }

export const inventoryService = {
  adjust: (data: { product_id: string; quantity: number; movement_type: MovementType; reason?: string }) =>
    apiClient.post<{ data: InventoryMovement }>('/inventory/adjust', data).then((r) => r.data.data),

  history: (params?: { page?: number; page_size?: number; product_id?: string }) =>
    apiClient.get<MovementsResponse>('/inventory/history', { params }).then((r) => r.data),

  lowStock: () =>
    apiClient.get<{ data: Product[] }>('/inventory/low-stock').then((r) => r.data.data),
}
