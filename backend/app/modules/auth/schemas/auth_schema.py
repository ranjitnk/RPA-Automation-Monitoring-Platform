"""
Auth module schemas for registration, login, and token responses.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

from app.schemas.common import EntitySchema


class TokenSchema(BaseModel):
    """Token response schema."""

    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Token expiration in seconds")


class UserSchema(BaseModel):
    """User schema for responses."""

    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_superadmin: bool
    avatar_url: Optional[str] = None


class UserDetailSchema(EntitySchema, UserSchema):
    """Detailed user schema with timestamps."""

    last_login: Optional[datetime] = None
    phone_number: Optional[str] = None


class RegisterSchema(BaseModel):
    """User registration schema."""

    username: str = Field(
        min_length=3,
        max_length=50,
        description="Username (3-50 characters)"
    )
    email: EmailStr = Field(description="Email address")
    password: str = Field(
        min_length=8,
        description="Password (minimum 8 characters)"
    )
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")


class LoginSchema(BaseModel):
    """User login schema."""

    email: EmailStr = Field(description="Email address")
    password: str = Field(description="Password")


class RefreshTokenSchema(BaseModel):
    """Refresh token request schema."""

    refresh_token: str = Field(description="Refresh token")


class PasswordChangeSchema(BaseModel):
    """Password change schema."""

    current_password: str = Field(description="Current password")
    new_password: str = Field(
        min_length=8,
        description="New password (minimum 8 characters)"
    )
    confirm_password: str = Field(description="Confirm new password")


class ProfileUpdateSchema(BaseModel):
    """User profile update schema."""

    full_name: Optional[str] = Field(None, max_length=255, description="Full name")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Avatar URL")
