import { Menu, Moon, Sun, LogOut, User, Bell } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useAuthStore } from '@/store/authStore'
import { useThemeStore } from '@/store/themeStore'
import { authService } from '@/services/auth.service'

interface HeaderProps { onMenuClick: () => void }

export function Header({ onMenuClick }: HeaderProps) {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const clearAuth = useAuthStore((s) => s.clearAuth)
  const { isDark, toggle } = useThemeStore()

  const handleLogout = async () => {
    try {
      await authService.logout()
    } catch {}
    clearAuth()
    navigate('/login')
    toast.success('Logged out successfully')
  }

  return (
    <header className="h-16 border-b border-border bg-card flex items-center justify-between px-4 md:px-6 shrink-0">
      <button onClick={onMenuClick} className="lg:hidden p-2 rounded-md hover:bg-muted">
        <Menu className="h-5 w-5" />
      </button>

      <div className="hidden lg:flex items-center text-sm text-muted-foreground">
        Inventory & Order Management System
      </div>

      <div className="flex items-center gap-2 ml-auto">
        <button
          onClick={toggle}
          className="p-2 rounded-md hover:bg-muted transition-colors"
          aria-label="Toggle theme"
        >
          {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </button>

        <button
          onClick={() => navigate('/profile')}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-muted transition-colors text-sm"
        >
          <div className="h-7 w-7 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-xs font-bold">
            {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
          </div>
          <span className="hidden md:block font-medium max-w-32 truncate">{user?.full_name}</span>
        </button>

        <button
          onClick={handleLogout}
          className="p-2 rounded-md hover:bg-destructive/10 hover:text-destructive transition-colors"
          title="Logout"
        >
          <LogOut className="h-4 w-4" />
        </button>
      </div>
    </header>
  )
}
