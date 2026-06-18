import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, Package, Users, ShoppingCart, Warehouse,
  ClipboardList, UserCog, X, Package2
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { cn } from '@/lib/utils'

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/products', icon: Package, label: 'Products' },
  { to: '/customers', icon: Users, label: 'Customers' },
  { to: '/orders', icon: ShoppingCart, label: 'Orders' },
  { to: '/inventory', icon: Warehouse, label: 'Inventory' },
  { to: '/audit-logs', icon: ClipboardList, label: 'Audit Logs', roles: ['ADMIN'] },
  { to: '/users', icon: UserCog, label: 'Users', roles: ['ADMIN'] },
]

interface SidebarProps { open: boolean; onClose: () => void }

export function Sidebar({ open, onClose }: SidebarProps) {
  const role = useAuthStore((s) => s.user?.role)
  const filteredNav = navItems.filter((item) => !item.roles || item.roles.includes(role || ''))

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div className="fixed inset-0 z-20 bg-black/50 lg:hidden" onClick={onClose} />
      )}

      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-30 w-64 bg-card border-r border-border flex flex-col transition-transform duration-300 ease-in-out lg:static lg:translate-x-0',
          open ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-border">
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-primary rounded-lg">
              <Package2 className="h-5 w-5 text-primary-foreground" />
            </div>
            <span className="font-bold text-lg">IMS</span>
          </div>
          <button onClick={onClose} className="lg:hidden p-1 rounded-md hover:bg-muted">
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {filteredNav.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              onClick={onClose}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                )
              }
            >
              <Icon className="h-4 w-4 shrink-0" />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Role badge */}
        <div className="px-4 py-3 border-t border-border">
          <p className="text-xs text-muted-foreground">
            Role: <span className="font-semibold text-foreground">{role}</span>
          </p>
        </div>
      </aside>
    </>
  )
}
