import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.order import OrderStatus
from app.schemas.product import ProductResponse
from app.schemas.customer import CustomerResponse


class OrderItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(..., gt=0)


class OrderItemResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    price: Decimal
    product: Optional[ProductResponse] = None

    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    customer_id: uuid.UUID
    items: List[OrderItemCreate] = Field(..., min_length=1)
    notes: Optional[str] = Field(default=None, max_length=1000)


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    notes: Optional[str] = Field(default=None, max_length=1000)


class OrderResponse(BaseModel):
    id: uuid.UUID
    order_number: str
    customer_id: uuid.UUID
    status: OrderStatus
    total_amount: Decimal
    notes: Optional[str] = None
    customer: Optional[CustomerResponse] = None
    items: List[OrderItemResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
