import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.responses import PaginatedResponse, StandardResponse
from app.database.session import get_db
from app.dependencies.auth import get_current_user, require_admin_or_manager
from app.models.user import User
from app.schemas.inventory import InventoryAdjustRequest, InventoryMovementResponse
from app.schemas.product import ProductResponse
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.post("/adjust", response_model=StandardResponse[InventoryMovementResponse])
async def adjust_inventory(
    data: InventoryAdjustRequest,
    current_user: User = Depends(require_admin_or_manager),
    db: AsyncSession = Depends(get_db),
):
    service = InventoryService(db)
    movement = await service.adjust(data, current_user)
    return StandardResponse.ok(
        InventoryMovementResponse.model_validate(movement), "Inventory adjusted"
    )


@router.get("/history", response_model=PaginatedResponse[InventoryMovementResponse])
async def get_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    product_id: Optional[uuid.UUID] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = InventoryService(db)
    movements, total = await service.get_history(
        page=page, page_size=page_size, product_id=product_id
    )
    return PaginatedResponse.create(
        data=[InventoryMovementResponse.model_validate(m) for m in movements],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/low-stock", response_model=StandardResponse[list[ProductResponse]])
async def get_low_stock(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = InventoryService(db)
    products = await service.get_low_stock()
    return StandardResponse.ok([ProductResponse.model_validate(p) for p in products])
