from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token_safe,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse


class AuthService:
    def __init__(self, repository: AuthRepository) -> None:
        self._repo = repository

    async def register(self, data: RegisterRequest) -> UserResponse:
        existing = await self._repo.get_user_by_email(data.email)
        if existing:
            raise ConflictError("Email already registered")

        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
        )
        created = await self._repo.create_user(user)
        return UserResponse.model_validate(created)

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self._repo.get_user_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedError("Account is disabled")

        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_token_safe(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid refresh token")

        from uuid import UUID

        user = await self._repo.get_user_by_id(UUID(payload["sub"]))
        if not user or not user.is_active:
            raise UnauthorizedError("User not found")

        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    async def get_profile(self, user: User) -> UserResponse:
        return UserResponse.model_validate(user)
