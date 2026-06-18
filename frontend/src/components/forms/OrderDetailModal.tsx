import { useMutation, useQueryClient } from '@tanstack/react-query'
import { X, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { orderService, type Order, type OrderStatus } from '@/services/order.service'
import { formatCurrency, formatDateTime, getStatusColor, getApiError } from '@/lib/utils'
import { useState } from 'react'

const STATUS_TRANSITIONS: Record<OrderStatus, OrderStatus[]> = {
  PENDING: ['CONFIRMED', 'CANCELLED'],
  CONFIRMED: ['SHIPPED', 'CANCELLED'],
  SHIPPED: ['DELIVERED', 'CANCELLED'],
  DELIVERED: [],
  CANCELLED: [],
}

interface Props { order: Order; onClose: () => void }

export function OrderDetailModal({ order, onClose }: Props) {
  const qc = useQueryClient()
  const [newStatus, setNewStatus] = useState<OrderStatus | ''>('')

  const mutation = useMutation({
    mutationFn: (status: OrderStatus) => orderService.updateStatus(order.id, status),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['orders'] }); toast.success('Order updated'); onClose() },
    onError: (err) => toast.error(getApiError(err)),
  })

  const transitions = STATUS_TRANSITIONS[order.status] || []

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="bg-card border border-border rounded-2xl w-full max-w-lg shadow-2xl">
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div>
            <h2 className="text-lg font-semibold">{order.order_number}</h2>
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${getStatusColor(order.status)}`}>{order.status}</span>
          </div>
          <button onClick={onClose} className="p-1 rounded-md hover:bg-muted"><X className="h-4 w-4" /></button>
        </div>

        <div className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground text-xs mb-0.5">Customer</p>
              <p className="font-medium">{order.customer?.full_name}</p>
              <p className="text-xs text-muted-foreground">{order.customer?.email}</p>
            </div>
            <div>
              <p className="text-muted-foreground text-xs mb-0.5">Created</p>
              <p>{formatDateTime(order.created_at)}</p>
            </div>
          </div>

          <div>
            <p className="text-xs text-muted-foreground mb-2 font-medium uppercase tracking-wide">Order Items</p>
            <div className="border border-border rounded-lg overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="px-3 py-2 text-left text-xs text-muted-foreground">Product</th>
                    <th className="px-3 py-2 text-right text-xs text-muted-foreground">Qty</th>
                    <th className="px-3 py-2 text-right text-xs text-muted-foreground">Price</th>
                    <th className="px-3 py-2 text-right text-xs text-muted-foreground">Subtotal</th>
                  </tr>
                </thead>
                <tbody>
                  {order.items.map((item) => (
                    <tr key={item.id} className="border-t border-border">
                      <td className="px-3 py-2">{item.product?.name || item.product_id}</td>
                      <td className="px-3 py-2 text-right">{item.quantity}</td>
                      <td className="px-3 py-2 text-right">{formatCurrency(item.price)}</td>
                      <td className="px-3 py-2 text-right">{formatCurrency(parseFloat(item.price) * item.quantity)}</td>
                    </tr>
                  ))}
                  <tr className="border-t-2 border-border bg-muted/30 font-bold">
                    <td colSpan={3} className="px-3 py-2 text-right">Total</td>
                    <td className="px-3 py-2 text-right text-primary">{formatCurrency(order.total_amount)}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {order.notes && (
            <div>
              <p className="text-xs text-muted-foreground mb-1">Notes</p>
              <p className="text-sm bg-muted rounded-lg px-3 py-2">{order.notes}</p>
            </div>
          )}

          {transitions.length > 0 && (
            <div className="flex items-center gap-3 pt-2">
              <select value={newStatus} onChange={(e) => setNewStatus(e.target.value as OrderStatus)} className="flex-1 px-3 py-2 border border-border rounded-lg text-sm bg-background focus:outline-none focus:ring-2 focus:ring-ring">
                <option value="">Update status...</option>
                {transitions.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
              <button
                onClick={() => newStatus && mutation.mutate(newStatus as OrderStatus)}
                disabled={!newStatus || mutation.isPending}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm hover:bg-primary/90 disabled:opacity-60 flex items-center gap-2"
              >
                {mutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
                Update
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
