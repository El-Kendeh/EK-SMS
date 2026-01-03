"""
User Schemas

Pydantic models for request/response validation.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.modules.users.models import UserRole


# ==========================================
# Base Schemas
# ==========================================


class UserBase(BaseModel):
    """Base user fields shared across schemas."""

    email: EmailStr
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    role: UserRole = UserRole.STUDENT


# ==========================================
# Request Schemas
# ==========================================


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating a user. All fields optional."""

    email: EmailStr | None = None
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    role: UserRole | None = None
    is_active: bool | None = None


class UserUpdatePassword(BaseModel):
    """Schema for updating user password."""

    current_password: str
    new_password: str = Field(min_length=8, max_length=100)


# ==========================================
# Response Schemas
# ==========================================


class UserResponse(UserBase):
    """Schema for user responses. Excludes sensitive data."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    is_active: bool
    is_verified: bool
    is_two_factor_enabled: bool
    created_at: datetime
    updated_at: datetime

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class UserListResponse(BaseModel):
    """Schema for paginated user list."""

    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
