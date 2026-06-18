import { Outlet } from 'react-router-dom'
import { Package } from 'lucide-react'

export function AuthLayout() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="p-2 bg-primary rounded-xl">
            <Package className="h-7 w-7 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">IMS</h1>
            <p className="text-xs text-slate-400">Inventory & Order Management</p>
          </div>
        </div>
        <div className="bg-card text-card-foreground rounded-2xl shadow-2xl border border-border p-8">
          <Outlet />
        </div>
      </div>
    </div>
  )
}
