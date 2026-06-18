from typing import List, Optional, Tuple
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.models.product import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: AsyncSession):
        super().__init__(Product, db)

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        result = await self.db.execute(
            select(Product).where(Product.sku == sku, Product.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        search: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        low_stock_only: bool = False,
        offset: int = 0,
        limit: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Product], int]:
        filters = [Product.deleted_at.is_(None)]

        if search:
            filters.append(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.sku.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%"),
                )
            )
        if category:
            filters.append(Product.category == category)
        if min_price is not None:
            filters.append(Product.price >= min_price)
        if max_price is not None:
            filters.append(Product.price <= max_price)
        if low_stock_only:
            filters.append(Product.quantity <= Product.reorder_level)

        count_result = await self.db.execute(
            select(func.count()).select_from(Product).where(*filters)
        )
        total = count_result.scalar()

        sort_col = getattr(Product, sort_by, Product.created_at)
        order_expr = sort_col.desc() if sort_order == "desc" else sort_col.asc()

        result = await self.db.execute(
            select(Product).where(*filters).order_by(order_expr).offset(offset).limit(limit)
        )
        return result.scalars().all(), total

    async def get_low_stock(self) -> List[Product]:
        result = await self.db.execute(
            select(Product).where(
                Product.deleted_at.is_(None),
                Product.quantity <= Product.reorder_level,
            )
        )
        return result.scalars().all()

    async def get_distinct_categories(self) -> List[str]:
        result = await self.db.execute(
            select(Product.category)
            .where(Product.deleted_at.is_(None), Product.category.isnot(None))
            .distinct()
        )
        return [row[0] for row in result.fetchall()]
