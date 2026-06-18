import { useQuery } from '@tanstack/react-query'
import {
  Package, Users, ShoppingCart, DollarSign,
  AlertTriangle, Clock, TrendingUp
} from 'lucide-react'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar
} from 'recharts'
import { dashboardService } from '@/services/dashboard.service'
import { StatCard } from '@/components/common/StatCard'
import { PageHeader } from '@/components/common/PageHeader'
import { formatCurrency, formatDate, getStatusColor } from '@/lib/utils'
import { Badge } from '@/components/common/Badge'

const CHART_MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
const MOCK_REVENUE = [4200, 5800, 4900, 7200, 6100, 8400]
const MOCK_ORDERS = [24, 38, 29, 45, 39, 52]

export default function DashboardPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => dashboardService.stats(),
    refetchInterval: 60_000,
  })

  const revenueData = CHART_MONTHS.map((m, i) => ({ month: m, revenue: MOCK_REVENUE[i], orders: MOCK_ORDERS[i] }))

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Dashboard" description="Overview of your business" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-muted rounded-xl skeleton" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Dashboard" description="Overview of your business operations" />

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Products"
          value={stats?.total_products ?? 0}
          icon={Package}
          iconClassName="bg-blue-500"
          trend={{ value: `${stats?.total_products ?? 0} active`, positive: true }}
        />
        <StatCard
          title="Total Customers"
          value={stats?.total_customers ?? 0}
          icon={Users}
          iconClassName="bg-green-500"
        />
        <StatCard
          title="Total Orders"
          value={stats?.total_orders ?? 0}
          icon={ShoppingCart}
          iconClassName="bg-purple-500"
          trend={{ value: `${stats?.orders_this_month ?? 0} this month`, positive: true }}
        />
        <StatCard
          title="Total Revenue"
          value={formatCurrency(stats?.total_revenue ?? 0)}
          icon={DollarSign}
          iconClassName="bg-yellow-500"
          trend={{ value: formatCurrency(stats?.revenue_this_month ?? 0) + ' this month', positive: true }}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card border border-border rounded-xl p-6">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-primary" /> Revenue Trend
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={revenueData}>
              <defs>
                <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(221.2 83.2% 53.3%)" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="hsl(221.2 83.2% 53.3%)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="month" className="text-xs fill-muted-foreground" tick={{ fontSize: 11 }} />
              <YAxis className="text-xs fill-muted-foreground" tick={{ fontSize: 11 }} tickFormatter={(v) => `$${v}`} />
              <Tooltip formatter={(v: number) => [`$${v}`, 'Revenue']} />
              <Area type="monotone" dataKey="revenue" stroke="hsl(221.2 83.2% 53.3%)" fill="url(#colorRev)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-card border border-border rounded-xl p-6">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <ShoppingCart className="h-4 w-4 text-primary" /> Orders by Month
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={revenueData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="month" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="orders" fill="hsl(221.2 83.2% 53.3%)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Low stock + recent orders */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Low Stock */}
        <div className="bg-card border border-border rounded-xl p-6">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-yellow-500" />
            Low Stock Alert ({stats?.low_stock_count ?? 0})
          </h3>
          {stats?.low_stock_products?.length ? (
            <div className="space-y-3">
              {stats.low_stock_products.map((p) => (
                <div key={p.id} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                  <div>
                    <p className="text-sm font-medium">{p.name}</p>
                    <p className="text-xs text-muted-foreground">{p.sku}</p>
                  </div>
                  <Badge variant="warning">{p.quantity} left</Badge>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">All products are well stocked</p>
          )}
        </div>

        {/* Recent Orders */}
        <div className="bg-card border border-border rounded-xl p-6">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <Clock className="h-4 w-4 text-primary" /> Recent Orders
          </h3>
          {stats?.recent_orders?.length ? (
            <div className="space-y-3">
              {stats.recent_orders.slice(0, 6).map((o) => (
                <div key={o.id} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                  <div>
                    <p className="text-sm font-medium">{o.order_number}</p>
                    <p className="text-xs text-muted-foreground">{formatDate(o.created_at)}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold">{formatCurrency(o.total_amount)}</p>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${getStatusColor(o.status)}`}>{o.status}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">No recent orders</p>
          )}
        </div>
      </div>
    </div>
  )
}
