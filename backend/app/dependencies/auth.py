from typing import Optional
from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_db
from app.models.user import User, UserRole
from app.security.jwt import verify_access_token
from app.core.exceptions import UnauthorizedException, ForbiddenException

security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not credentials:
        raise UnauthorizedException("Missing authentication token")

    payload = verify_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload")

    result = await db.execute(select(User).where(User.id == user_id, User.deleted_at.is_(None)))
    user = result.scalar_one_or_none()
    if not user:
        raise UnauthorizedException("User not found")
    if not user.is_active:
        raise UnauthorizedException("User account is disabled")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise UnauthorizedException("Inactive user")
    return current_user


def require_role(*roles: UserRole):
    async def check_role(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise ForbiddenException(
                f"This action requires one of the following roles: {[r.value for r in roles]}"
            )
        return current_user
    return check_role


require_admin = require_role(UserRole.ADMIN)
require_admin_or_manager = require_role(UserRole.ADMIN, UserRole.MANAGER)
require_any_role = require_role(UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF)
