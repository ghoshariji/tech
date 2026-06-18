import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Download, Pencil, Trash2, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { productService, type Product } from '@/services/product.service'
import { PageHeader } from '@/components/common/PageHeader'
import { DataTable } from '@/components/common/DataTable'
import { Pagination } from '@/components/common/Pagination'
import { SearchInput } from '@/components/common/SearchInput'
import { Badge } from '@/components/common/Badge'
import { formatCurrency, formatDate, getApiError } from '@/lib/utils'
import { useAuthStore } from '@/store/authStore'
import { ProductModal } from '@/components/forms/ProductModal'

export default function ProductsPage() {
  const qc = useQueryClient()
  const role = useAuthStore((s) => s.user?.role)
  const canEdit = role === 'ADMIN' || role === 'MANAGER'

  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [editProduct, setEditProduct] = useState<Product | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['products', page, search],
    queryFn: () => productService.list({ page, page_size: 20, search: search || undefined }),
  })

  const deleteMutation = useMutation({
    mutationFn: productService.delete,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['products'] })
      toast.success('Product deleted')
    },
    onError: (err) => toast.error(getApiError(err)),
  })

  const handleExport = async () => {
    try {
      const blob = await productService.exportCsv()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url; a.download = 'products.csv'; a.click()
      URL.revokeObjectURL(url)
    } catch { toast.error('Export failed') }
  }

  const columns = [
    { key: 'name', header: 'Product', render: (p: Product) => (
      <div>
        <p className="font-medium">{p.name}</p>
        <p className="text-xs text-muted-foreground">{p.sku}</p>
      </div>
    )},
    { key: 'category', header: 'Category', render: (p: Product) => p.category || <span className="text-muted-foreground">—</span> },
    { key: 'price', header: 'Price', render: (p: Product) => formatCurrency(p.price) },
    { key: 'quantity', header: 'Stock', render: (p: Product) => (
      <div className="flex items-center gap-2">
        {p.is_low_stock && <AlertCircle className="h-3.5 w-3.5 text-yellow-500" />}
        <span className={p.is_low_stock ? 'text-yellow-600 font-medium' : ''}>{p.quantity}</span>
      </div>
    )},
    { key: 'reorder_level', header: 'Reorder At' },
    { key: 'status', header: 'Status', render: (p: Product) => (
      <Badge variant={p.is_low_stock ? 'warning' : 'success'}>
        {p.is_low_stock ? 'Low Stock' : 'In Stock'}
      </Badge>
    )},
    { key: 'created_at', header: 'Created', render: (p: Product) => formatDate(p.created_at) },
    ...(canEdit ? [{
      key: 'actions', header: 'Actions', render: (p: Product) => (
        <div className="flex items-center gap-1">
          <button onClick={() => { setEditProduct(p); setModalOpen(true) }} className="p-1.5 hover:bg-muted rounded-md"><Pencil className="h-3.5 w-3.5" /></button>
          <button onClick={() => { if (confirm(`Delete "${p.name}"?`)) deleteMutation.mutate(p.id) }} className="p-1.5 hover:bg-destructive/10 text-destructive rounded-md"><Trash2 className="h-3.5 w-3.5" /></button>
        </div>
      ),
    }] : []),
  ]

  return (
    <div className="space-y-4">
      <PageHeader
        title="Products"
        description="Manage your product catalog"
        actions={
          <>
            {canEdit && (
              <>
                <button onClick={handleExport} className="flex items-center gap-2 px-3 py-2 border border-border rounded-lg text-sm hover:bg-muted">
                  <Download className="h-4 w-4" /> Export
                </button>
                <button onClick={() => { setEditProduct(null); setModalOpen(true) }} className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm hover:bg-primary/90">
                  <Plus className="h-4 w-4" /> Add Product
                </button>
              </>
            )}
          </>
        }
      />

      <div className="w-full max-w-sm">
        <SearchInput value={search} onChange={(v) => { setSearch(v); setPage(1) }} placeholder="Search products..." />
      </div>

      <DataTable columns={columns} data={data?.data || []} isLoading={isLoading} keyExtractor={(p) => p.id} />

      {data && data.total > 20 && (
        <Pagination page={page} totalPages={data.total_pages} onPageChange={setPage} total={data.total} pageSize={20} />
      )}

      <ProductModal
        open={modalOpen}
        onClose={() => { setModalOpen(false); setEditProduct(null) }}
        product={editProduct}
      />
    </div>
  )
}
