import uuid
from typing import List, Optional
from sqlalchemy import String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base, TimestampMixin, SoftDeleteMixin


class Customer(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    orders: Mapped[List["Order"]] = relationship(  # noqa: F821
        "Order", back_populates="customer", lazy="noload"
    )

    __table_args__ = (
        Index("ix_customers_email_deleted", "email", "deleted_at"),
    )

    def __repr__(self) -> str:
        return f"<Customer {self.email}>"
