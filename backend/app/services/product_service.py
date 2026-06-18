import uuid
import io
import csv
from typing import List, Optional, Tuple
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.service import AuditService
from app.core.exceptions import ConflictException, NotFoundException
from app.models.product import Product
from app.models.user import User
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate, ProductFilter
from app.core.logging import get_logger

logger = get_logger(__name__)


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProductRepository(db)
        self.audit = AuditService(db)

    async def create(self, data: ProductCreate, current_user: User) -> Product:
        if await self.repo.get_by_sku(data.sku):
            raise ConflictException(f"Product with SKU '{data.sku}' already exists")

        product = await self.repo.create(data.model_dump())

        await self.audit.log(
            action="PRODUCT_CREATE",
            resource="products",
            resource_id=str(product.id),
            user_id=current_user.id,
            new_values=data.model_dump(mode="json"),
        )
        return product

    async def get_by_id(self, product_id: uuid.UUID) -> Product:
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product", product_id)
        return product

    async def list(
        self,
        search: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        low_stock_only: bool = False,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Product], int]:
        return await self.repo.search(
            search=search,
            category=category,
            min_price=min_price,
            max_price=max_price,
            low_stock_only=low_stock_only,
            offset=(page - 1) * page_size,
            limit=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def update(
        self, product_id: uuid.UUID, data: ProductUpdate, current_user: User
    ) -> Product:
        product = await self.get_by_id(product_id)

        if data.sku and data.sku != product.sku:
            existing = await self.repo.get_by_sku(data.sku)
            if existing:
                raise ConflictException(f"Product with SKU '{data.sku}' already exists")

        old_values = {
            "name": product.name,
            "sku": product.sku,
            "price": str(product.price),
            "quantity": product.quantity,
        }

        update_data = data.model_dump(exclude_none=True)
        updated = await self.repo.update(product, update_data)

        await self.audit.log(
            action="PRODUCT_UPDATE",
            resource="products",
            resource_id=str(product_id),
            user_id=current_user.id,
            old_values=old_values,
            new_values=data.model_dump(exclude_none=True, mode="json"),
        )
        return updated

    async def delete(self, product_id: uuid.UUID, current_user: User) -> None:
        product = await self.get_by_id(product_id)
        await self.repo.soft_delete(product)
        await self.audit.log(
            action="PRODUCT_DELETE",
            resource="products",
            resource_id=str(product_id),
            user_id=current_user.id,
            old_values={"name": product.name, "sku": product.sku},
        )

    async def get_low_stock(self) -> List[Product]:
        return await self.repo.get_low_stock()

    async def export_csv(self) -> io.StringIO:
        products, _ = await self.repo.search(limit=10000)
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["id", "name", "sku", "category", "price", "quantity", "reorder_level", "created_at"],
        )
        writer.writeheader()
        for p in products:
            writer.writerow(
                {
                    "id": str(p.id),
                    "name": p.name,
                    "sku": p.sku,
                    "category": p.category or "",
                    "price": str(p.price),
                    "quantity": p.quantity,
                    "reorder_level": p.reorder_level,
                    "created_at": p.created_at.isoformat(),
                }
            )
        output.seek(0)
        return output

    async def bulk_import(self, rows: List[dict], current_user: User) -> dict:
        created = 0
        updated = 0
        errors = []

        for i, row in enumerate(rows):
            try:
                sku = row.get("sku")
                existing = await self.repo.get_by_sku(sku) if sku else None
                if existing:
                    await self.repo.update(existing, row)
                    updated += 1
                else:
                    await self.repo.create(row)
                    created += 1
            except Exception as exc:
                errors.append({"row": i + 1, "error": str(exc)})

        return {"created": created, "updated": updated, "errors": errors}
