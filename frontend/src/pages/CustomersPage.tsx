import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Pencil, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { customerService, type Customer } from '@/services/customer.service'
import { PageHeader } from '@/components/common/PageHeader'
import { DataTable } from '@/components/common/DataTable'
import { Pagination } from '@/components/common/Pagination'
import { SearchInput } from '@/components/common/SearchInput'
import { formatDate, getApiError } from '@/lib/utils'
import { useAuthStore } from '@/store/authStore'
import { CustomerModal } from '@/components/forms/CustomerModal'

export default function CustomersPage() {
  const qc = useQueryClient()
  const role = useAuthStore((s) => s.user?.role)
  const canEdit = role === 'ADMIN' || role === 'MANAGER'

  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [editCustomer, setEditCustomer] = useState<Customer | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['customers', page, search],
    queryFn: () => customerService.list({ page, page_size: 20, search: search || undefined }),
  })

  const deleteMutation = useMutation({
    mutationFn: customerService.delete,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['customers'] }); toast.success('Customer deleted') },
    onError: (err) => toast.error(getApiError(err)),
  })

  const columns = [
    { key: 'full_name', header: 'Name', render: (c: Customer) => (
      <div>
        <p className="font-medium">{c.full_name}</p>
        <p className="text-xs text-muted-foreground">{c.email}</p>
      </div>
    )},
    { key: 'phone', header: 'Phone', render: (c: Customer) => c.phone || <span className="text-muted-foreground">—</span> },
    { key: 'address', header: 'Address', render: (c: Customer) => c.address ? <span className="max-w-48 truncate block">{c.address}</span> : <span className="text-muted-foreground">—</span> },
    { key: 'created_at', header: 'Joined', render: (c: Customer) => formatDate(c.created_at) },
    ...(canEdit ? [{
      key: 'actions', header: 'Actions', render: (c: Customer) => (
        <div className="flex items-center gap-1">
          <button onClick={() => { setEditCustomer(c); setModalOpen(true) }} className="p-1.5 hover:bg-muted rounded-md"><Pencil className="h-3.5 w-3.5" /></button>
          <button onClick={() => { if (confirm(`Delete customer "${c.full_name}"?`)) deleteMutation.mutate(c.id) }} className="p-1.5 hover:bg-destructive/10 text-destructive rounded-md"><Trash2 className="h-3.5 w-3.5" /></button>
        </div>
      ),
    }] : []),
  ]

  return (
    <div className="space-y-4">
      <PageHeader
        title="Customers"
        description="Manage your customer base"
        actions={canEdit && (
          <button onClick={() => { setEditCustomer(null); setModalOpen(true) }} className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm hover:bg-primary/90">
            <Plus className="h-4 w-4" /> Add Customer
          </button>
        )}
      />

      <div className="w-full max-w-sm">
        <SearchInput value={search} onChange={(v) => { setSearch(v); setPage(1) }} placeholder="Search customers..." />
      </div>

      <DataTable columns={columns} data={data?.data || []} isLoading={isLoading} keyExtractor={(c) => c.id} />

      {data && data.total > 20 && (
        <Pagination page={page} totalPages={data.total_pages} onPageChange={setPage} total={data.total} pageSize={20} />
      )}

      <CustomerModal open={modalOpen} onClose={() => { setModalOpen(false); setEditCustomer(null) }} customer={editCustomer} />
    </div>
  )
}
