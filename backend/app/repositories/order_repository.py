import uuid
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderStatus
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: AsyncSession):
        super().__init__(Order, db)

    async def get_by_id_with_items(self, order_id: uuid.UUID) -> Optional[Order]:
        result = await self.db.execute(
            select(Order)
            .where(Order.id == order_id, Order.deleted_at.is_(None))
            .options(selectinload(Order.items))
        )
        return result.scalar_one_or_none()

    async def get_by_order_number(self, order_number: str) -> Optional[Order]:
        result = await self.db.execute(
            select(Order).where(Order.order_number == order_number, Order.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        customer_id: Optional[uuid.UUID] = None,
        status: Optional[OrderStatus] = None,
        search: Optional[str] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Order], int]:
        filters = [Order.deleted_at.is_(None)]

        if customer_id:
            filters.append(Order.customer_id == customer_id)
        if status:
            filters.append(Order.status == status)
        if search:
            filters.append(Order.order_number.ilike(f"%{search}%"))

        count_result = await self.db.execute(
            select(func.count()).select_from(Order).where(*filters)
        )
        total = count_result.scalar()

        result = await self.db.execute(
            select(Order)
            .where(*filters)
            .order_by(Order.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all(), total

    async def get_recent(self, limit: int = 10) -> List[Order]:
        result = await self.db.execute(
            select(Order)
            .where(Order.deleted_at.is_(None))
            .order_by(Order.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
