import uuid
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import String, Numeric, Integer, Text, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base, TimestampMixin, SoftDeleteMixin


class Product(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reorder_level: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    # Relationships
    order_items: Mapped[List["OrderItem"]] = relationship(  # noqa: F821
        "OrderItem", back_populates="product", lazy="noload"
    )
    inventory_movements: Mapped[List["InventoryMovement"]] = relationship(  # noqa: F821
        "InventoryMovement", back_populates="product", lazy="noload"
    )

    __table_args__ = (
        CheckConstraint("price > 0", name="ck_products_price_positive"),
        CheckConstraint("quantity >= 0", name="ck_products_quantity_non_negative"),
        CheckConstraint("reorder_level >= 0", name="ck_products_reorder_level_non_negative"),
        Index("ix_products_sku_deleted", "sku", "deleted_at"),
    )

    @property
    def is_low_stock(self) -> bool:
        return self.quantity <= self.reorder_level

    def __repr__(self) -> str:
        return f"<Product {self.sku}: {self.name}>"
