import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { auditService, type AuditLog } from '@/services/audit.service'
import { PageHeader } from '@/components/common/PageHeader'
import { DataTable } from '@/components/common/DataTable'
import { Pagination } from '@/components/common/Pagination'
import { Badge } from '@/components/common/Badge'
import { formatDateTime } from '@/lib/utils'

export default function AuditLogsPage() {
  const [page, setPage] = useState(1)
  const [resource, setResource] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['audit-logs', page, resource],
    queryFn: () => auditService.list({ page, page_size: 20, resource: resource || undefined }),
  })

  const columns = [
    { key: 'action', header: 'Action', render: (l: AuditLog) => (
      <span className="font-mono text-xs bg-muted px-2 py-0.5 rounded">{l.action}</span>
    )},
    { key: 'resource', header: 'Resource', render: (l: AuditLog) => (
      <span className="capitalize">{l.resource}</span>
    )},
    { key: 'resource_id', header: 'Resource ID', render: (l: AuditLog) => (
      <span className="text-xs text-muted-foreground font-mono">{l.resource_id ? l.resource_id.slice(0, 8) + '...' : '—'}</span>
    )},
    { key: 'status', header: 'Status', render: (l: AuditLog) => (
      <Badge variant={l.status === 'SUCCESS' ? 'success' : 'danger'}>{l.status}</Badge>
    )},
    { key: 'ip_address', header: 'IP', render: (l: AuditLog) => l.ip_address || '—' },
    { key: 'created_at', header: 'Timestamp', render: (l: AuditLog) => formatDateTime(l.created_at) },
  ]

  return (
    <div className="space-y-4">
      <PageHeader title="Audit Logs" description="Track all system activity" />

      <div>
        <select value={resource} onChange={(e) => { setResource(e.target.value); setPage(1) }} className="px-3 py-2 border border-border rounded-lg text-sm bg-background focus:outline-none focus:ring-2 focus:ring-ring">
          <option value="">All Resources</option>
          {['users', 'products', 'customers', 'orders', 'inventory'].map((r) => (
            <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</option>
          ))}
        </select>
      </div>

      <DataTable columns={columns} data={data?.data || []} isLoading={isLoading} keyExtractor={(l) => l.id} />

      {data && data.total > 20 && (
        <Pagination page={page} totalPages={data.total_pages} onPageChange={setPage} total={data.total} pageSize={20} />
      )}
    </div>
  )
}
