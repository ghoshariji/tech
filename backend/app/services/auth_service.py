import secrets
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.service import AuditService
from app.config.settings import settings
from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
    UnauthorizedException,
)
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    TokenResponse,
    UserCreate,
    UserLogin,
)
from app.security.jwt import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from app.security.password import hash_password, verify_password
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)
        self.audit = AuditService(db)

    async def register(self, data: UserCreate, request: Optional[Request] = None) -> User:
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise ConflictException(f"Email '{data.email}' is already registered")

        hashed = hash_password(data.password)
        verification_token = secrets.token_urlsafe(32)

        user = await self.repo.create(
            {
                "full_name": data.full_name,
                "email": data.email,
                "hashed_password": hashed,
                "role": data.role,
                "is_active": True,
                "is_verified": False,
                "verification_token": verification_token,
            }
        )

        await self.audit.log(
            action="USER_REGISTER",
            resource="users",
            resource_id=str(user.id),
            user_id=user.id,
            ip_address=self._get_ip(request),
            new_values={"email": user.email, "role": user.role},
        )

        logger.info(f"New user registered: {user.email}")
        return user

    async def login(self, data: UserLogin, request: Optional[Request] = None) -> TokenResponse:
        user = await self.repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            await self.audit.log(
                action="LOGIN_FAILED",
                resource="users",
                ip_address=self._get_ip(request),
                new_values={"email": data.email},
                status="FAILED",
                error_message="Invalid credentials",
            )
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("Account is disabled. Contact administrator.")

        access_token = create_access_token(str(user.id), user.role.value)
        refresh_token = create_refresh_token(str(user.id))

        await self.repo.update(user, {"refresh_token": refresh_token})

        await self.audit.log(
            action="USER_LOGIN",
            resource="users",
            resource_id=str(user.id),
            user_id=user.id,
            ip_address=self._get_ip(request),
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        payload = verify_refresh_token(refresh_token)
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid refresh token")

        user = await self.repo.get_by_id(uuid.UUID(user_id))
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")

        if user.refresh_token != refresh_token:
            raise UnauthorizedException("Refresh token has been rotated. Please log in again.")

        new_access_token = create_access_token(str(user.id), user.role.value)
        new_refresh_token = create_refresh_token(str(user.id))

        await self.repo.update(user, {"refresh_token": new_refresh_token})

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def logout(self, user: User, request: Optional[Request] = None) -> None:
        await self.repo.update(user, {"refresh_token": None})
        await self.audit.log(
            action="USER_LOGOUT",
            resource="users",
            resource_id=str(user.id),
            user_id=user.id,
            ip_address=self._get_ip(request),
        )

    async def verify_email(self, token: str) -> User:
        user = await self.repo.get_by_verification_token(token)
        if not user:
            raise BadRequestException("Invalid or expired verification token")
        await self.repo.update(user, {"is_verified": True, "verification_token": None})
        return user

    async def request_password_reset(self, email: str) -> Optional[str]:
        user = await self.repo.get_by_email(email)
        if not user:
            return None
        token = secrets.token_urlsafe(32)
        await self.repo.update(user, {"password_reset_token": token})
        return token

    async def reset_password(self, token: str, new_password: str) -> User:
        user = await self.repo.get_by_reset_token(token)
        if not user:
            raise BadRequestException("Invalid or expired reset token")
        hashed = hash_password(new_password)
        await self.repo.update(user, {"hashed_password": hashed, "password_reset_token": None})
        return user

    def _get_ip(self, request: Optional[Request]) -> Optional[str]:
        if not request:
            return None
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else None
