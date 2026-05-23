from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_auth_service, require_active_user
from app.models.user import User
from app.modules.auth.schemas import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.modules.auth.service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    body: RegisterRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    return await service.register(body)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    return await service.login(body)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    body: RefreshTokenRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    return await service.refresh(body.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(
    user: Annotated[User, Depends(require_active_user)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    return await service.get_profile(user)
