import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowUpDown, Loader2, AlertTriangle } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import { inventoryService, type InventoryMovement } from '@/services/inventory.service'
import { productService } from '@/services/product.service'
import { PageHeader } from '@/components/common/PageHeader'
import { DataTable } from '@/components/common/DataTable'
import { Pagination } from '@/components/common/Pagination'
import { Badge } from '@/components/common/Badge'
import { formatDateTime, getApiError } from '@/lib/utils'

const schema = z.object({
  product_id: z.string().min(1, 'Select a product'),
  quantity: z.coerce.number().int().refine((v) => v !== 0, 'Cannot be 0'),
  movement_type: z.enum(['IN', 'OUT', 'ADJUSTMENT', 'RETURN']),
  reason: z.string().optional(),
})

type FormData = z.infer<typeof schema>

const movementBadge: Record<string, { variant: 'success' | 'danger' | 'info' | 'warning'; label: string }> = {
  IN: { variant: 'success', label: 'Stock In' },
  OUT: { variant: 'danger', label: 'Stock Out' },
  ADJUSTMENT: { variant: 'info', label: 'Adjustment' },
  RETURN: { variant: 'warning', label: 'Return' },
}

export default function InventoryPage() {
  const qc = useQueryClient()
  const [page, setPage] = useState(1)

  const { data: history, isLoading } = useQuery({
    queryKey: ['inventory-history', page],
    queryFn: () => inventoryService.history({ page, page_size: 20 }),
  })

  const { data: lowStock } = useQuery({
    queryKey: ['inventory-low-stock'],
    queryFn: () => inventoryService.lowStock(),
  })

  const { data: products } = useQuery({
    queryKey: ['products-all'],
    queryFn: () => productService.list({ page_size: 100 }),
  })

  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { movement_type: 'ADJUSTMENT' },
  })

  const mutation = useMutation({
    mutationFn: (data: FormData) => inventoryService.adjust(data as any),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['inventory-history'] })
      qc.invalidateQueries({ queryKey: ['inventory-low-stock'] })
      qc.invalidateQueries({ queryKey: ['products'] })
      toast.success('Inventory adjusted')
      reset()
    },
    onError: (err) => toast.error(getApiError(err)),
  })

  const columns = [
    { key: 'product', header: 'Product', render: (m: InventoryMovement) => (
      <span className="font-medium">{(m as any).product?.name || m.product_id}</span>
    )},
    { key: 'movement_type', header: 'Type', render: (m: InventoryMovement) => {
      const b = movementBadge[m.movement_type]
      return <Badge variant={b.variant}>{b.label}</Badge>
    }},
    { key: 'quantity', header: 'Qty', render: (m: InventoryMovement) => (
      <span className={m.movement_type === 'OUT' ? 'text-red-500' : 'text-green-600'}>
        {m.movement_type === 'OUT' ? '-' : '+'}{m.quantity}
      </span>
    )},
    { key: 'quantity_before', header: 'Before' },
    { key: 'quantity_after', header: 'After' },
    { key: 'reason', header: 'Reason', render: (m: InventoryMovement) => m.reason || <span className="text-muted-foreground">—</span> },
    { key: 'created_at', header: 'Date', render: (m: InventoryMovement) => formatDateTime(m.created_at) },
  ]

  return (
    <div className="space-y-6">
      <PageHeader title="Inventory" description="Track stock levels and movements" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Adjust Form */}
        <div className="lg:col-span-1">
          <div className="bg-card border border-border rounded-xl p-6">
            <h3 className="font-semibold mb-4 flex items-center gap-2"><ArrowUpDown className="h-4 w-4" /> Adjust Stock</h3>
            <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="space-y-3">
              <div>
                <label className="block text-xs font-medium mb-1">Product *</label>
                <select {...register('product_id')} className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-background focus:outline-none focus:ring-2 focus:ring-ring">
                  <option value="">Select product...</option>
                  {products?.data?.map((p) => <option key={p.id} value={p.id}>{p.name} (qty: {p.quantity})</option>)}
                </select>
                {errors.product_id && <p className="text-xs text-destructive mt-1">{errors.product_id.message}</p>}
              </div>
              <div>
                <label className="block text-xs font-medium mb-1">Type</label>
                <select {...register('movement_type')} className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-background focus:outline-none focus:ring-2 focus:ring-ring">
                  <option value="IN">Stock In</option>
                  <option value="OUT">Stock Out</option>
                  <option value="ADJUSTMENT">Adjustment</option>
                  <option value="RETURN">Return</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium mb-1">Quantity (negative to remove)</label>
                <input {...register('quantity')} type="number" placeholder="e.g. 50 or -10" className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-background focus:outline-none focus:ring-2 focus:ring-ring" />
                {errors.quantity && <p className="text-xs text-destructive mt-1">{errors.quantity.message}</p>}
              </div>
              <div>
                <label className="block text-xs font-medium mb-1">Reason</label>
                <input {...register('reason')} placeholder="Optional..." className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-background focus:outline-none focus:ring-2 focus:ring-ring" />
              </div>
              <button type="submit" disabled={isSubmitting} className="w-full py-2 bg-primary text-primary-foreground rounded-lg text-sm hover:bg-primary/90 disabled:opacity-60 flex items-center justify-center gap-2">
                {isSubmitting && <Loader2 className="h-4 w-4 animate-spin" />}
                Adjust Stock
              </button>
            </form>
          </div>

          {/* Low stock */}
          {lowStock && lowStock.length > 0 && (
            <div className="bg-card border border-yellow-200 dark:border-yellow-900/50 rounded-xl p-6 mt-4">
              <h3 className="font-semibold mb-3 flex items-center gap-2 text-yellow-700 dark:text-yellow-400">
                <AlertTriangle className="h-4 w-4" /> Low Stock ({lowStock.length})
              </h3>
              <div className="space-y-2">
                {lowStock.map((p) => (
                  <div key={p.id} className="flex justify-between items-center text-sm">
                    <span className="truncate font-medium">{p.name}</span>
                    <Badge variant="warning">{p.quantity} left</Badge>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Movement History */}
        <div className="lg:col-span-2">
          <h3 className="font-semibold mb-3">Movement History</h3>
          <DataTable columns={columns} data={history?.data || []} isLoading={isLoading} keyExtractor={(m) => m.id} />
          {history && history.total > 20 && (
            <Pagination page={page} totalPages={history.total_pages} onPageChange={setPage} total={history.total} pageSize={20} />
          )}
        </div>
      </div>
    </div>
  )
}
