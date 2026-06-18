import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { userService, type User } from '@/services/user.service'
import { PageHeader } from '@/components/common/PageHeader'
import { DataTable } from '@/components/common/DataTable'
import { Pagination } from '@/components/common/Pagination'
import { Badge } from '@/components/common/Badge'
import { formatDate, getApiError, getRoleColor } from '@/lib/utils'
import { UserModal } from '@/components/forms/UserModal'
import { useAuthStore } from '@/store/authStore'

export default function UsersPage() {
  const qc = useQueryClient()
  const currentUser = useAuthStore((s) => s.user)
  const [page, setPage] = useState(1)
  const [modalOpen, setModalOpen] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['users', page],
    queryFn: () => userService.list({ page, page_size: 20 }),
  })

  const deleteMutation = useMutation({
    mutationFn: userService.delete,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['users'] }); toast.success('User deleted') },
    onError: (err) => toast.error(getApiError(err)),
  })

  const columns = [
    { key: 'full_name', header: 'User', render: (u: User) => (
      <div>
        <p className="font-medium">{u.full_name}</p>
        <p className="text-xs text-muted-foreground">{u.email}</p>
      </div>
    )},
    { key: 'role', header: 'Role', render: (u: User) => (
      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${getRoleColor(u.role)}`}>{u.role}</span>
    )},
    { key: 'is_active', header: 'Status', render: (u: User) => (
      <Badge variant={u.is_active ? 'success' : 'danger'}>{u.is_active ? 'Active' : 'Inactive'}</Badge>
    )},
    { key: 'is_verified', header: 'Verified', render: (u: User) => (
      <Badge variant={u.is_verified ? 'success' : 'warning'}>{u.is_verified ? 'Yes' : 'No'}</Badge>
    )},
    { key: 'created_at', header: 'Joined', render: (u: User) => formatDate(u.created_at) },
    { key: 'actions', header: 'Actions', render: (u: User) => u.id !== currentUser?.id ? (
      <button onClick={() => { if (confirm(`Delete user "${u.full_name}"?`)) deleteMutation.mutate(u.id) }} className="p-1.5 hover:bg-destructive/10 text-destructive rounded-md">
        <Trash2 className="h-3.5 w-3.5" />
      </button>
    ) : <span className="text-xs text-muted-foreground">You</span> },
  ]

  return (
    <div className="space-y-4">
      <PageHeader
        title="Users"
        description="Manage system users and roles"
        actions={
          <button onClick={() => setModalOpen(true)} className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm hover:bg-primary/90">
            <Plus className="h-4 w-4" /> Add User
          </button>
        }
      />

      <DataTable columns={columns} data={data?.data || []} isLoading={isLoading} keyExtractor={(u) => u.id} />

      {data && data.total > 20 && (
        <Pagination page={page} totalPages={data.total_pages} onPageChange={setPage} total={data.total} pageSize={20} />
      )}

      <UserModal open={modalOpen} onClose={() => setModalOpen(false)} />
    </div>
  )
}
