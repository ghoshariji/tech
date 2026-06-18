import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sku: str = Field(..., min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_\-]+$")
    description: Optional[str] = Field(default=None, max_length=2000)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    quantity: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=10, ge=0)
    category: Optional[str] = Field(default=None, max_length=100)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    sku: Optional[str] = Field(default=None, min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_\-]+$")
    description: Optional[str] = Field(default=None, max_length=2000)
    price: Optional[Decimal] = Field(default=None, gt=0, decimal_places=2)
    quantity: Optional[int] = Field(default=None, ge=0)
    reorder_level: Optional[int] = Field(default=None, ge=0)
    category: Optional[str] = Field(default=None, max_length=100)


class ProductResponse(ProductBase):
    id: uuid.UUID
    is_low_stock: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductFilter(BaseModel):
    category: Optional[str] = None
    min_price: Optional[Decimal] = Field(default=None, gt=0)
    max_price: Optional[Decimal] = Field(default=None, gt=0)
    low_stock_only: bool = False
