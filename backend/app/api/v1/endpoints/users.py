import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.responses import PaginatedResponse, StandardResponse
from app.database.session import get_db
from app.dependencies.auth import get_current_user, require_admin
from app.models.user import User
from app.schemas.user import UserChangePassword, UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    users, total = await service.list(page=page, page_size=page_size)
    return PaginatedResponse.create(
        data=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=StandardResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    user = await service.create(data, current_user)
    return StandardResponse.ok(UserResponse.model_validate(user), "User created")


@router.get("/{user_id}", response_model=StandardResponse[UserResponse])
async def get_user(
    user_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    user = await service.get_by_id(user_id)
    return StandardResponse.ok(UserResponse.model_validate(user))


@router.put("/{user_id}", response_model=StandardResponse[UserResponse])
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    user = await service.update(user_id, data, current_user)
    return StandardResponse.ok(UserResponse.model_validate(user), "User updated")


@router.delete("/{user_id}", response_model=StandardResponse)
async def delete_user(
    user_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    await service.delete(user_id, current_user)
    return StandardResponse.ok(message="User deleted")


@router.post("/me/change-password", response_model=StandardResponse)
async def change_password(
    data: UserChangePassword,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    await service.change_password(current_user.id, data, current_user)
    return StandardResponse.ok(message="Password changed successfully")
