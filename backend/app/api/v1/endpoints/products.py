import uuid
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.responses import PaginatedResponse, StandardResponse
from app.database.session import get_db
from app.dependencies.auth import get_current_user, require_admin_or_manager
from app.models.user import User
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("", response_model=StandardResponse[ProductResponse], status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    current_user: User = Depends(require_admin_or_manager),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    product = await service.create(data, current_user)
    return StandardResponse.ok(ProductResponse.model_validate(product), "Product created")


@router.get("", response_model=PaginatedResponse[ProductResponse])
async def list_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None, max_length=200),
    category: Optional[str] = Query(default=None),
    min_price: Optional[Decimal] = Query(default=None),
    max_price: Optional[Decimal] = Query(default=None),
    low_stock_only: bool = Query(default=False),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    products, total = await service.list(
        search=search,
        category=category,
        min_price=min_price,
        max_price=max_price,
        low_stock_only=low_stock_only,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return PaginatedResponse.create(
        data=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/export/csv")
async def export_products_csv(
    current_user: User = Depends(require_admin_or_manager),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    output = await service.export_csv()
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=products.csv"},
    )


@router.get("/{product_id}", response_model=StandardResponse[ProductResponse])
async def get_product(
    product_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    product = await service.get_by_id(product_id)
    return StandardResponse.ok(ProductResponse.model_validate(product))


@router.put("/{product_id}", response_model=StandardResponse[ProductResponse])
async def update_product(
    product_id: uuid.UUID,
    data: ProductUpdate,
    current_user: User = Depends(require_admin_or_manager),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    product = await service.update(product_id, data, current_user)
    return StandardResponse.ok(ProductResponse.model_validate(product), "Product updated")


@router.delete("/{product_id}", response_model=StandardResponse, status_code=status.HTTP_200_OK)
async def delete_product(
    product_id: uuid.UUID,
    current_user: User = Depends(require_admin_or_manager),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    await service.delete(product_id, current_user)
    return StandardResponse.ok(message="Product deleted successfully")
