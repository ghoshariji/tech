import uuid
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.service import AuditService
from app.core.exceptions import BadRequestException, ConflictException, ForbiddenException, NotFoundException
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserChangePassword
from app.security.password import hash_password, verify_password


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)
        self.audit = AuditService(db)

    async def get_by_id(self, user_id: uuid.UUID) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        return user

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[User], int]:
        return await self.repo.get_all(
            offset=(page - 1) * page_size,
            limit=page_size,
        )

    async def create(self, data: UserCreate, current_user: User) -> User:
        if current_user.role != UserRole.ADMIN:
            raise ForbiddenException("Only admins can create users")
        if await self.repo.get_by_email(data.email):
            raise ConflictException(f"Email '{data.email}' is already registered")

        user = await self.repo.create(
            {
                "full_name": data.full_name,
                "email": data.email,
                "hashed_password": hash_password(data.password),
                "role": data.role,
                "is_active": True,
                "is_verified": True,
            }
        )
        await self.audit.log(
            action="USER_CREATE",
            resource="users",
            resource_id=str(user.id),
            user_id=current_user.id,
            new_values={"email": user.email, "role": user.role.value},
        )
        return user

    async def update(self, user_id: uuid.UUID, data: UserUpdate, current_user: User) -> User:
        user = await self.get_by_id(user_id)
        updated = await self.repo.update(user, data.model_dump(exclude_none=True))
        await self.audit.log(
            action="USER_UPDATE",
            resource="users",
            resource_id=str(user_id),
            user_id=current_user.id,
            new_values=data.model_dump(exclude_none=True),
        )
        return updated

    async def delete(self, user_id: uuid.UUID, current_user: User) -> None:
        if user_id == current_user.id:
            raise BadRequestException("Cannot delete your own account")
        user = await self.get_by_id(user_id)
        await self.repo.soft_delete(user)
        await self.audit.log(
            action="USER_DELETE",
            resource="users",
            resource_id=str(user_id),
            user_id=current_user.id,
        )

    async def change_password(
        self, user_id: uuid.UUID, data: UserChangePassword, current_user: User
    ) -> User:
        user = await self.get_by_id(user_id)
        if not verify_password(data.current_password, user.hashed_password):
            raise BadRequestException("Current password is incorrect")
        updated = await self.repo.update(
            user, {"hashed_password": hash_password(data.new_password)}
        )
        return updated
