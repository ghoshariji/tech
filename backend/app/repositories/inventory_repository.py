import uuid
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.inventory import InventoryMovement
from app.repositories.base import BaseRepository


class InventoryRepository(BaseRepository[InventoryMovement]):
    def __init__(self, db: AsyncSession):
        super().__init__(InventoryMovement, db)

    async def get_by_product(
        self,
        product_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[InventoryMovement], int]:
        filters = [InventoryMovement.product_id == product_id]

        count_result = await self.db.execute(
            select(func.count()).select_from(InventoryMovement).where(*filters)
        )
        total = count_result.scalar()

        result = await self.db.execute(
            select(InventoryMovement)
            .where(*filters)
            .order_by(InventoryMovement.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all(), total

    async def get_history(
        self,
        offset: int = 0,
        limit: int = 20,
        product_id: Optional[uuid.UUID] = None,
    ) -> Tuple[List[InventoryMovement], int]:
        filters = []
        if product_id:
            filters.append(InventoryMovement.product_id == product_id)

        count_result = await self.db.execute(
            select(func.count()).select_from(InventoryMovement).where(*filters)
        )
        total = count_result.scalar()

        result = await self.db.execute(
            select(InventoryMovement)
            .where(*filters)
            .order_by(InventoryMovement.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all(), total
