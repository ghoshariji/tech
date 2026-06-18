import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.responses import PaginatedResponse, StandardResponse
from app.database.session import get_db
from app.dependencies.auth import get_current_user, require_admin_or_manager
from app.models.order import OrderStatus
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=StandardResponse[OrderResponse], status_code=status.HTTP_201_CREATED)
async def create_order(
    data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrderService(db)
    order = await service.create(data, current_user)
    return StandardResponse.ok(OrderResponse.model_validate(order), "Order created")


@router.get("", response_model=PaginatedResponse[OrderResponse])
async def list_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    customer_id: Optional[uuid.UUID] = Query(default=None),
    status: Optional[OrderStatus] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrderService(db)
    orders, total = await service.list(
        customer_id=customer_id,
        status=status,
        search=search,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse.create(
        data=[OrderResponse.model_validate(o) for o in orders],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/export/csv")
async def export_orders_csv(
    current_user: User = Depends(require_admin_or_manager),
    db: AsyncSession = Depends(get_db),
):
    service = OrderService(db)
    output = await service.export_csv()
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=orders.csv"},
    )


@router.get("/{order_id}", response_model=StandardResponse[OrderResponse])
async def get_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrderService(db)
    order = await service.get_by_id(order_id)
    return StandardResponse.ok(OrderResponse.model_validate(order))


@router.put("/{order_id}", response_model=StandardResponse[OrderResponse])
async def update_order(
    order_id: uuid.UUID,
    data: OrderUpdate,
    current_user: User = Depends(require_admin_or_manager),
    db: AsyncSession = Depends(get_db),
):
    service = OrderService(db)
    order = await service.update(order_id, data, current_user)
    return StandardResponse.ok(OrderResponse.model_validate(order), "Order updated")


@router.delete("/{order_id}", response_model=StandardResponse)
async def cancel_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrderService(db)
    await service.cancel(order_id, current_user)
    return StandardResponse.ok(message="Order cancelled successfully")
