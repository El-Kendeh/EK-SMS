"""
User Service

Business logic for user management.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate, UserUpdate


class UserServiceError(Exception):
    """Base exception for user service errors."""

    pass


class UserNotFoundError(UserServiceError):
    """User not found."""

    pass


class UserAlreadyExistsError(UserServiceError):
    """User already exists."""

    pass


class InvalidPasswordError(UserServiceError):
    """Invalid password."""

    pass


class UserService:
    """Service for user business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = UserRepository(session)

    async def get_by_id(self, user_id: str) -> User:
        """Get user by ID or raise error."""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        return user

    async def get_by_email(self, email: str) -> User:
        """Get user by email or raise error."""
        user = await self.repository.get_by_email(email)
        if not user:
            raise UserNotFoundError(f"User with email {email} not found")
        return user

    async def list(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        is_active: bool | None = None,
    ) -> tuple[list[User], int]:
        """List users with pagination."""
        skip = (page - 1) * page_size
        return await self.repository.list(
            skip=skip,
            limit=page_size,
            is_active=is_active,
        )

    async def create(self, data: UserCreate) -> User:
        """Create a new user."""
        # Check if email already exists
        if await self.repository.exists_by_email(data.email):
            raise UserAlreadyExistsError(f"User with email {data.email} already exists")

        # Check if phone already exists (if provided)
        if data.phone and await self.repository.exists_by_phone(data.phone):
            raise UserAlreadyExistsError(f"User with phone {data.phone} already exists")

        # Create user
        user = User(
            email=data.email.lower(),
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            role=data.role,
            password_hash=hash_password(data.password),
        )

        return await self.repository.create(user)

    async def update(self, user_id: str, data: UserUpdate) -> User:
        """Update a user."""
        user = await self.get_by_id(user_id)

        # Check email uniqueness if changing
        if data.email and data.email.lower() != user.email:
            if await self.repository.exists_by_email(data.email):
                raise UserAlreadyExistsError(
                    f"User with email {data.email} already exists"
                )
            user.email = data.email.lower()

        # Check phone uniqueness if changing
        if data.phone and data.phone != user.phone:
            if await self.repository.exists_by_phone(data.phone):
                raise UserAlreadyExistsError(
                    f"User with phone {data.phone} already exists"
                )
            user.phone = data.phone

        # Update other fields
        if data.first_name is not None:
            user.first_name = data.first_name
        if data.last_name is not None:
            user.last_name = data.last_name
        if data.role is not None:
            user.role = data.role
        if data.is_active is not None:
            user.is_active = data.is_active

        return await self.repository.update(user)

    async def update_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str,
    ) -> User:
        """Update user password."""
        user = await self.get_by_id(user_id)

        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise InvalidPasswordError("Current password is incorrect")

        # Update password
        user.password_hash = hash_password(new_password)
        return await self.repository.update(user)

    async def delete(self, user_id: str) -> None:
        """Delete a user."""
        user = await self.get_by_id(user_id)
        await self.repository.delete(user)

    async def verify_credentials(self, email: str, password: str) -> User:
        """Verify user credentials for login."""
        user = await self.repository.get_by_email(email)

        if not user:
            raise UserNotFoundError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise InvalidPasswordError("Invalid email or password")

        if not user.is_active:
            raise UserServiceError("User account is deactivated")

        return user
