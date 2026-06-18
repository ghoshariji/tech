import uuid
import io
import csv
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.audit.service import AuditService
from app.core.exceptions import (
    BadRequestException,
    InsufficientStockException,
    NotFoundException,
)
from app.models.inventory import InventoryMovement, MovementType
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.user import User
from app.repositories.customer_repository import CustomerRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.order import OrderCreate, OrderUpdate
from app.core.logging import get_logger

logger = get_logger(__name__)


def _generate_order_number() -> str:
    from datetime import datetime
    import random
    now = datetime.now(timezone.utc)
    return f"ORD-{now.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.product_repo = ProductRepository(db)
        self.customer_repo = CustomerRepository(db)
        self.audit = AuditService(db)

    async def create(self, data: OrderCreate, current_user: User) -> Order:
        customer = await self.customer_repo.get_by_id(data.customer_id)
        if not customer:
            raise NotFoundException("Customer", data.customer_id)

        # Validate and lock products
        order_items_data = []
        total_amount = Decimal("0.00")

        for item in data.items:
            result = await self.db.execute(
                select(Product).where(
                    Product.id == item.product_id, Product.deleted_at.is_(None)
                ).with_for_update()
            )
            product = result.scalar_one_or_none()
            if not product:
                raise NotFoundException("Product", item.product_id)
            if product.quantity < item.quantity:
                raise InsufficientStockException(
                    product.name, product.quantity, item.quantity
                )
            order_items_data.append((product, item.quantity))
            total_amount += product.price * item.quantity

        # Create order
        order_number = _generate_order_number()
        while await self.order_repo.get_by_order_number(order_number):
            order_number = _generate_order_number()

        order = Order(
            order_number=order_number,
            customer_id=data.customer_id,
            status=OrderStatus.PENDING,
            total_amount=total_amount,
            notes=data.notes,
        )
        self.db.add(order)
        await self.db.flush()

        # Create order items + deduct inventory
        for product, quantity in order_items_data:
            quantity_before = product.quantity
            product.quantity -= quantity
            await self.db.flush()

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                price=product.price,
            )
            self.db.add(order_item)

            movement = InventoryMovement(
                product_id=product.id,
                movement_type=MovementType.OUT,
                quantity=quantity,
                quantity_before=quantity_before,
                quantity_after=product.quantity,
                reference_id=str(order.id),
                reference_type="ORDER",
                reason=f"Order {order_number}",
                performed_by=current_user.id,
            )
            self.db.add(movement)

        await self.db.flush()
        await self.db.refresh(order)

        await self.audit.log(
            action="ORDER_CREATE",
            resource="orders",
            resource_id=str(order.id),
            user_id=current_user.id,
            new_values={"order_number": order_number, "total_amount": str(total_amount)},
        )

        return order

    async def get_by_id(self, order_id: uuid.UUID) -> Order:
        order = await self.order_repo.get_by_id_with_items(order_id)
        if not order:
            raise NotFoundException("Order", order_id)
        return order

    async def list(
        self,
        customer_id: Optional[uuid.UUID] = None,
        status: Optional[OrderStatus] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Order], int]:
        return await self.order_repo.search(
            customer_id=customer_id,
            status=status,
            search=search,
            offset=(page - 1) * page_size,
            limit=page_size,
        )

    async def update(
        self, order_id: uuid.UUID, data: OrderUpdate, current_user: User
    ) -> Order:
        order = await self.get_by_id(order_id)

        if order.status == OrderStatus.CANCELLED:
            raise BadRequestException("Cannot update a cancelled order")
        if order.status == OrderStatus.DELIVERED and data.status not in (None, OrderStatus.DELIVERED):
            raise BadRequestException("Cannot change status of a delivered order")

        old_status = order.status
        update_data = data.model_dump(exclude_none=True)
        updated = await self.order_repo.update(order, update_data)

        await self.audit.log(
            action="ORDER_UPDATE",
            resource="orders",
            resource_id=str(order_id),
            user_id=current_user.id,
            old_values={"status": old_status},
            new_values=update_data,
        )
        return updated

    async def cancel(self, order_id: uuid.UUID, current_user: User) -> Order:
        order = await self.get_by_id(order_id)

        if order.status in (OrderStatus.DELIVERED, OrderStatus.CANCELLED):
            raise BadRequestException(f"Cannot cancel an order with status '{order.status}'")

        # Restore inventory
        for item in order.items:
            result = await self.db.execute(
                select(Product).where(Product.id == item.product_id).with_for_update()
            )
            product = result.scalar_one_or_none()
            if product:
                quantity_before = product.quantity
                product.quantity += item.quantity
                await self.db.flush()

                movement = InventoryMovement(
                    product_id=product.id,
                    movement_type=MovementType.RETURN,
                    quantity=item.quantity,
                    quantity_before=quantity_before,
                    quantity_after=product.quantity,
                    reference_id=str(order.id),
                    reference_type="ORDER_CANCEL",
                    reason=f"Order cancellation {order.order_number}",
                    performed_by=current_user.id,
                )
                self.db.add(movement)

        updated = await self.order_repo.update(order, {"status": OrderStatus.CANCELLED})

        await self.audit.log(
            action="ORDER_CANCEL",
            resource="orders",
            resource_id=str(order_id),
            user_id=current_user.id,
        )
        return updated

    async def export_csv(self) -> io.StringIO:
        orders, _ = await self.order_repo.search(limit=10000)
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["order_number", "customer", "status", "total_amount", "created_at"],
        )
        writer.writeheader()
        for o in orders:
            writer.writerow(
                {
                    "order_number": o.order_number,
                    "customer": o.customer.email if o.customer else "",
                    "status": o.status,
                    "total_amount": str(o.total_amount),
                    "created_at": o.created_at.isoformat(),
                }
            )
        output.seek(0)
        return output
