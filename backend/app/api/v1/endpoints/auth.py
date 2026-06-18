from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.responses import StandardResponse
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.user import (
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=StandardResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    user = await service.register(data, request)
    return StandardResponse.ok(UserResponse.model_validate(user), "Registration successful")


@router.post("/login", response_model=StandardResponse[TokenResponse])
async def login(
    data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    tokens = await service.login(data, request)
    return StandardResponse.ok(tokens, "Login successful")


@router.post("/refresh", response_model=StandardResponse[TokenResponse])
async def refresh(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    tokens = await service.refresh_token(data.refresh_token)
    return StandardResponse.ok(tokens, "Token refreshed")


@router.post("/logout", response_model=StandardResponse)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    await service.logout(current_user, request)
    return StandardResponse.ok(message="Logged out successfully")


@router.get("/me", response_model=StandardResponse[UserResponse])
async def get_me(current_user: User = Depends(get_current_user)):
    return StandardResponse.ok(UserResponse.model_validate(current_user))


@router.get("/verify-email/{token}", response_model=StandardResponse)
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.verify_email(token)
    return StandardResponse.ok(message="Email verified successfully")


@router.post("/forgot-password", response_model=StandardResponse)
async def forgot_password(data: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.request_password_reset(data.email)
    return StandardResponse.ok(message="If the email exists, a reset link has been sent")


@router.post("/reset-password", response_model=StandardResponse)
async def reset_password(data: PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.reset_password(data.token, data.new_password)
    return StandardResponse.ok(message="Password reset successfully")
