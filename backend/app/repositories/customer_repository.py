from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.models.customer import Customer
from app.repositories.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, db: AsyncSession):
        super().__init__(Customer, db)

    async def get_by_email(self, email: str) -> Optional[Customer]:
        result = await self.db.execute(
            select(Customer).where(Customer.email == email, Customer.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        search: Optional[str] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Customer], int]:
        filters = [Customer.deleted_at.is_(None)]
        if search:
            filters.append(
                or_(
                    Customer.full_name.ilike(f"%{search}%"),
                    Customer.email.ilike(f"%{search}%"),
                    Customer.phone.ilike(f"%{search}%"),
                )
            )

        count_result = await self.db.execute(
            select(func.count()).select_from(Customer).where(*filters)
        )
        total = count_result.scalar()

        result = await self.db.execute(
            select(Customer)
            .where(*filters)
            .order_by(Customer.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all(), total
