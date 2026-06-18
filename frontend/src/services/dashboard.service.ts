import { apiClient } from '@/lib/axios'
import type { Product } from './product.service'
import type { Order } from './order.service'

export interface DashboardStats {
  total_products: number; total_customers: number; total_orders: number
  total_revenue: string; pending_orders: number; low_stock_count: number
  low_stock_products: Product[]; recent_orders: Order[]
  revenue_this_month: string; orders_this_month: number
}

export const dashboardService = {
  stats: () =>
    apiClient.get<{ data: DashboardStats }>('/dashboard').then((r) => r.data.data),
}
