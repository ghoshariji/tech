import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { X, Plus, Minus, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { orderService } from '@/services/order.service'
import { customerService } from '@/services/customer.service'
import { productService } from '@/services/product.service'
import { getApiError, formatCurrency } from '@/lib/utils'

interface OrderItem { product_id: string; quantity: number; price: number; name: string }

interface OrderModalProps { open: boolean; onClose: () => void }

export function OrderModal({ open, onClose }: OrderModalProps) {
  const qc = useQueryClient()
  const [customerId, setCustomerId] = useState('')
  const [items, setItems] = useState<OrderItem[]>([])
  const [notes, setNotes] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const { data: customers } = useQuery({
    queryKey: ['customers-all'],
    queryFn: () => customerService.list({ page_size: 100 }),
    enabled: open,
  })

  const { data: products } = useQuery({
    queryKey: ['products-all'],
    queryFn: () => productService.list({ page_size: 100 }),
    enabled: open,
  })

  const addItem = (productId: string) => {
    const product = products?.data?.find((p) => p.id === productId)
    if (!product) return
    const existing = items.find((i) => i.product_id === productId)
    if (existing) {
      setItems(items.map((i) => i.product_id === productId ? { ...i, quantity: i.quantity + 1 } : i))
    } else {
      setItems([...items, { product_id: productId, quantity: 1, price: parseFloat(product.price), name: product.name }])
    }
  }

  const removeItem = (productId: string) => setItems(items.filter((i) => i.product_id !== productId))
  const total = items.reduce((sum, i) => sum + i.price * i.quantity, 0)

  const handleSubmit = async () => {
    if (!customerId) { toast.error('Select a customer'); return }
    if (items.length === 0) { toast.error('Add at least one item'); return }
    setIsSubmitting(true)
    try {
      await orderService.create({
        customer_id: customerId,
        items: items.map((i) => ({ product_id: i.product_id, quantity: i.quantity })),
        notes: notes || undefined,
      })
      qc.invalidateQueries({ queryKey: ['orders'] })
      qc.invalidateQueries({ queryKey: ['products'] })
      qc.invalidateQueries({ queryKey: ['dashboard'] })
      toast.success('Order created successfully')
      onClose()
      setCustomerId(''); setItems([]); setNotes('')
    } catch (err) {
      toast.error(getApiError(err))
    } finally {
      setIsSubmitting(false)
    }
  }

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="bg-card border border-border rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-2xl">
        <div className="flex items-center justify-between p-6 border-b border-border">
          <h2 className="text-lg font-semibold">Create New Order</h2>
          <button onClick={onClose} className="p-1 rounded-md hover:bg-muted"><X className="h-4 w-4" /></button>
        </div>

        <div className="p-6 space-y-5">
          <div>
            <label className="block text-sm font-medium mb-1.5">Customer *</label>
            <select value={customerId} onChange={(e) => setCustomerId(e.target.value)} className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-background focus:outline-none focus:ring-2 focus:ring-ring">
              <option value="">Select customer...</option>
              {customers?.data?.map((c) => <option key={c.id} value={c.id}>{c.full_name} — {c.email}</option>)}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">Add Products</label>
            <select onChange={(e) => { if (e.target.value) addItem(e.target.value); e.target.value = '' }} className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-background focus:outline-none focus:ring-2 focus:ring-ring">
              <option value="">Select product to add...</option>
              {products?.data?.filter((p) => p.quantity > 0).map((p) => (
                <option key={p.id} value={p.id}>{p.name} ({p.sku}) — {formatCurrency(p.price)} — Stock: {p.quantity}</option>
              ))}
            </select>
          </div>

          {items.length > 0 && (
            <div className="border border-border rounded-lg overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs text-muted-foreground">Product</th>
                    <th className="px-4 py-2 text-left text-xs text-muted-foreground">Qty</th>
                    <th className="px-4 py-2 text-left text-xs text-muted-foreground">Subtotal</th>
                    <th className="px-4 py-2"></th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((item) => (
                    <tr key={item.product_id} className="border-t border-border">
                      <td className="px-4 py-2">{item.name}</td>
                      <td className="px-4 py-2">
                        <div className="flex items-center gap-2">
                          <button onClick={() => setItems(items.map((i) => i.product_id === item.product_id ? { ...i, quantity: Math.max(1, i.quantity - 1) } : i))} className="p-0.5 border border-border rounded"><Minus className="h-3 w-3" /></button>
                          <span className="w-8 text-center">{item.quantity}</span>
                          <button onClick={() => setItems(items.map((i) => i.product_id === item.product_id ? { ...i, quantity: i.quantity + 1 } : i))} className="p-0.5 border border-border rounded"><Plus className="h-3 w-3" /></button>
                        </div>
                      </td>
                      <td className="px-4 py-2">{formatCurrency(item.price * item.quantity)}</td>
                      <td className="px-4 py-2"><button onClick={() => removeItem(item.product_id)} className="text-destructive hover:text-destructive/80"><X className="h-3.5 w-3.5" /></button></td>
                    </tr>
                  ))}
                  <tr className="border-t border-border bg-muted/30">
                    <td colSpan={2} className="px-4 py-2 font-semibold text-right">Total:</td>
                    <td colSpan={2} className="px-4 py-2 font-bold text-primary">{formatCurrency(total)}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-1.5">Notes</label>
            <textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-background focus:outline-none focus:ring-2 focus:ring-ring resize-none" placeholder="Optional order notes..." />
          </div>

          <div className="flex gap-3">
            <button type="button" onClick={onClose} className="flex-1 py-2 border border-border rounded-lg text-sm hover:bg-muted">Cancel</button>
            <button onClick={handleSubmit} disabled={isSubmitting} className="flex-1 py-2 bg-primary text-primary-foreground rounded-lg text-sm hover:bg-primary/90 disabled:opacity-60 flex items-center justify-center gap-2">
              {isSubmitting && <Loader2 className="h-4 w-4 animate-spin" />}
              Create Order
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
