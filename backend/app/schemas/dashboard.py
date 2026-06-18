from decimal import Decimal
from typing import List
from pydantic import BaseModel

from app.schemas.product import ProductResponse
from app.schemas.order import OrderResponse


class DashboardStats(BaseModel):
    total_products: int
    total_customers: int
    total_orders: int
    total_revenue: Decimal
    pending_orders: int
    low_stock_count: int
    low_stock_products: List[ProductResponse]
    recent_orders: List[OrderResponse]
    revenue_this_month: Decimal
    orders_this_month: int
