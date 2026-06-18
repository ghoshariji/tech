from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.customer import Customer
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.dashboard import DashboardStats


class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.product_repo = ProductRepository(db)

    async def get_stats(self) -> DashboardStats:
        # Total products
        p_count = await self.db.execute(
            select(func.count(Product.id)).where(Product.deleted_at.is_(None))
        )
        total_products = p_count.scalar() or 0

        # Total customers
        c_count = await self.db.execute(
            select(func.count(Customer.id)).where(Customer.deleted_at.is_(None))
        )
        total_customers = c_count.scalar() or 0

        # Total orders
        o_count = await self.db.execute(
            select(func.count(Order.id)).where(Order.deleted_at.is_(None))
        )
        total_orders = o_count.scalar() or 0

        # Total revenue
        rev = await self.db.execute(
            select(func.coalesce(func.sum(Order.total_amount), 0)).where(
                Order.deleted_at.is_(None),
                Order.status != OrderStatus.CANCELLED,
            )
        )
        total_revenue = rev.scalar() or Decimal("0.00")

        # Pending orders
        pending = await self.db.execute(
            select(func.count(Order.id)).where(
                Order.deleted_at.is_(None), Order.status == OrderStatus.PENDING
            )
        )
        pending_orders = pending.scalar() or 0

        # Low stock
        low_stock_products = await self.product_repo.get_low_stock()
        low_stock_count = len(low_stock_products)

        # Recent orders
        recent_orders = await self.order_repo.get_recent(limit=10)

        # This month
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        month_rev = await self.db.execute(
            select(func.coalesce(func.sum(Order.total_amount), 0)).where(
                Order.deleted_at.is_(None),
                Order.status != OrderStatus.CANCELLED,
                Order.created_at >= month_start,
            )
        )
        revenue_this_month = month_rev.scalar() or Decimal("0.00")

        month_orders = await self.db.execute(
            select(func.count(Order.id)).where(
                Order.deleted_at.is_(None),
                Order.created_at >= month_start,
            )
        )
        orders_this_month = month_orders.scalar() or 0

        return DashboardStats(
            total_products=total_products,
            total_customers=total_customers,
            total_orders=total_orders,
            total_revenue=total_revenue,
            pending_orders=pending_orders,
            low_stock_count=low_stock_count,
            low_stock_products=low_stock_products[:5],
            recent_orders=recent_orders,
            revenue_this_month=revenue_this_month,
            orders_this_month=orders_this_month,
        )
