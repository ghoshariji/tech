import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.responses import PaginatedResponse, StandardResponse
from app.database.session import get_db
from app.dependencies.auth import get_current_user, require_admin_or_manager
from app.models.user import User
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("", response_model=StandardResponse[CustomerResponse], status_code=status.HTTP_201_CREATED)
async def create_customer(
    data: CustomerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CustomerService(db)
    customer = await service.create(data, current_user)
    return StandardResponse.ok(CustomerResponse.model_validate(customer), "Customer created")


@router.get("", response_model=PaginatedResponse[CustomerResponse])
async def list_customers(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None, max_length=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CustomerService(db)
    customers, total = await service.list(search=search, page=page, page_size=page_size)
    return PaginatedResponse.create(
        data=[CustomerResponse.model_validate(c) for c in customers],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{customer_id}", response_model=StandardResponse[CustomerResponse])
async def get_customer(
    customer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CustomerService(db)
    customer = await service.get_by_id(customer_id)
    return StandardResponse.ok(CustomerResponse.model_validate(customer))


@router.put("/{customer_id}", response_model=StandardResponse[CustomerResponse])
async def update_customer(
    customer_id: uuid.UUID,
    data: CustomerUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CustomerService(db)
    customer = await service.update(customer_id, data, current_user)
    return StandardResponse.ok(CustomerResponse.model_validate(customer), "Customer updated")


@router.delete("/{customer_id}", response_model=StandardResponse)
async def delete_customer(
    customer_id: uuid.UUID,
    current_user: User = Depends(require_admin_or_manager),
    db: AsyncSession = Depends(get_db),
):
    service = CustomerService(db)
    await service.delete(customer_id, current_user)
    return StandardResponse.ok(message="Customer deleted successfully")
