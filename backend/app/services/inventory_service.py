import uuid
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.audit.service import AuditService
from app.core.exceptions import BadRequestException, NotFoundException
from app.models.inventory import InventoryMovement, MovementType
from app.models.product import Product
from app.models.user import User
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.inventory import InventoryAdjustRequest


class InventoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = InventoryRepository(db)
        self.product_repo = ProductRepository(db)
        self.audit = AuditService(db)

    async def adjust(
        self, data: InventoryAdjustRequest, current_user: User
    ) -> InventoryMovement:
        result = await self.db.execute(
            select(Product)
            .where(Product.id == data.product_id, Product.deleted_at.is_(None))
            .with_for_update()
        )
        product = result.scalar_one_or_none()
        if not product:
            raise NotFoundException("Product", data.product_id)

        new_quantity = product.quantity + data.quantity
        if new_quantity < 0:
            raise BadRequestException(
                f"Adjustment would result in negative stock ({new_quantity}) for '{product.name}'"
            )

        quantity_before = product.quantity
        product.quantity = new_quantity
        await self.db.flush()

        movement = InventoryMovement(
            product_id=product.id,
            movement_type=data.movement_type,
            quantity=abs(data.quantity),
            quantity_before=quantity_before,
            quantity_after=new_quantity,
            reason=data.reason,
            performed_by=current_user.id,
        )
        self.db.add(movement)
        await self.db.flush()
        await self.db.refresh(movement)

        await self.audit.log(
            action="INVENTORY_ADJUST",
            resource="inventory",
            resource_id=str(product.id),
            user_id=current_user.id,
            old_values={"quantity": quantity_before},
            new_values={"quantity": new_quantity, "adjustment": data.quantity},
        )

        return movement

    async def get_history(
        self,
        page: int = 1,
        page_size: int = 20,
        product_id: Optional[uuid.UUID] = None,
    ) -> Tuple[List[InventoryMovement], int]:
        return await self.repo.get_history(
            offset=(page - 1) * page_size,
            limit=page_size,
            product_id=product_id,
        )

    async def get_low_stock(self) -> List[Product]:
        return await self.product_repo.get_low_stock()
