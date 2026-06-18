import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Download, X } from 'lucide-react'
import toast from 'react-hot-toast'
import { orderService, type Order, type OrderStatus } from '@/services/order.service'
import { PageHeader } from '@/components/common/PageHeader'
import { DataTable } from '@/components/common/DataTable'
import { Pagination } from '@/components/common/Pagination'
import { SearchInput } from '@/components/common/SearchInput'
import { formatCurrency, formatDate, getStatusColor, getApiError } from '@/lib/utils'
import { OrderModal } from '@/components/forms/OrderModal'
import { OrderDetailModal } from '@/components/forms/OrderDetailModal'

const STATUS_OPTIONS: OrderStatus[] = ['PENDING', 'CONFIRMED', 'SHIPPED', 'DELIVERED', 'CANCELLED']

export default function OrdersPage() {
  const qc = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<OrderStatus | ''>('')
  const [createOpen, setCreateOpen] = useState(false)
  const [detailOrder, setDetailOrder] = useState<Order | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['orders', page, search, statusFilter],
    queryFn: () => orderService.list({ page, page_size: 20, search: search || undefined, status: statusFilter || undefined }),
  })

  const cancelMutation = useMutation({
    mutationFn: orderService.cancel,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['orders'] }); toast.success('Order cancelled') },
    onError: (err) => toast.error(getApiError(err)),
  })

  const handleExport = async () => {
    try {
      const blob = await orderService.exportCsv()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url; a.download = 'orders.csv'; a.click()
      URL.revokeObjectURL(url)
    } catch { toast.error('Export failed') }
  }

  const columns = [
    { key: 'order_number', header: 'Order #', render: (o: Order) => (
      <button onClick={() => setDetailOrder(o)} className="font-medium text-primary hover:underline">{o.order_number}</button>
    )},
    { key: 'customer', header: 'Customer', render: (o: Order) => (
      <div>
        <p className="font-medium">{o.customer?.full_name || '—'}</p>
        <p className="text-xs text-muted-foreground">{o.customer?.email}</p>
      </div>
    )},
    { key: 'items', header: 'Items', render: (o: Order) => `${o.items?.length ?? 0} item(s)` },
    { key: 'total_amount', header: 'Total', render: (o: Order) => <span className="font-semibold">{formatCurrency(o.total_amount)}</span> },
    { key: 'status', header: 'Status', render: (o: Order) => (
      <span className={`text-xs px-2 py-1 rounded-full font-medium ${getStatusColor(o.status)}`}>{o.status}</span>
    )},
    { key: 'created_at', header: 'Created', render: (o: Order) => formatDate(o.created_at) },
    { key: 'actions', header: 'Actions', render: (o: Order) => o.status !== 'CANCELLED' && o.status !== 'DELIVERED' ? (
      <button onClick={() => { if (confirm('Cancel this order?')) cancelMutation.mutate(o.id) }} className="p-1.5 hover:bg-destructive/10 text-destructive rounded-md" title="Cancel"><X className="h-3.5 w-3.5" /></button>
    ) : null },
  ]

  return (
    <div className="space-y-4">
      <PageHeader
        title="Orders"
        description="Track and manage customer orders"
        actions={
          <>
            <button onClick={handleExport} className="flex items-center gap-2 px-3 py-2 border border-border rounded-lg text-sm hover:bg-muted">
              <Download className="h-4 w-4" /> Export
            </button>
            <button onClick={() => setCreateOpen(true)} className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm hover:bg-primary/90">
              <Plus className="h-4 w-4" /> New Order
            </button>
          </>
        }
      />

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="w-full max-w-xs">
          <SearchInput value={search} onChange={(v) => { setSearch(v); setPage(1) }} placeholder="Search by order number..." />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value as OrderStatus | ''); setPage(1) }}
          className="px-3 py-2 border border-border rounded-lg text-sm bg-background focus:outline-none focus:ring-2 focus:ring-ring"
        >
          <option value="">All Statuses</option>
          {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      <DataTable columns={columns} data={data?.data || []} isLoading={isLoading} keyExtractor={(o) => o.id} />

      {data && data.total > 20 && (
        <Pagination page={page} totalPages={data.total_pages} onPageChange={setPage} total={data.total} pageSize={20} />
      )}

      <OrderModal open={createOpen} onClose={() => setCreateOpen(false)} />
      {detailOrder && <OrderDetailModal order={detailOrder} onClose={() => setDetailOrder(null)} />}
    </div>
  )
}
