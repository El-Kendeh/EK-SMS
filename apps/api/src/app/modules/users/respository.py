"""
User Repository

Database operations for users.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User


class UserRepository:
    """Repository for user database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: str) -> User | None:
        """Get user by ID."""
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        result = await self.session.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> User | None:
        """Get user by phone number."""
        result = await self.session.execute(select(User).where(User.phone == phone))
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        is_active: bool | None = None,
    ) -> tuple[list[User], int]:
        """
        List users with pagination.

        Returns:
            Tuple of (users, total_count)
        """
        query = select(User)
        count_query = select(func.count(User.id))

        if is_active is not None:
            query = query.where(User.is_active == is_active)
            count_query = count_query.where(User.is_active == is_active)

        # Get total count
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await self.session.execute(query)
        users = list(result.scalars().all())

        return users, total

    async def create(self, user: User) -> User:
        """Create a new user."""
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def update(self, user: User) -> User:
        """Update an existing user."""
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        """Delete a user."""
        await self.session.delete(user)
        await self.session.flush()

    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        result = await self.session.execute(
            select(func.count(User.id)).where(User.email == email.lower())
        )
        return result.scalar_one() > 0

    async def exists_by_phone(self, phone: str) -> bool:
        """Check if user exists by phone."""
        result = await self.session.execute(
            select(func.count(User.id)).where(User.phone == phone)
        )
        return result.scalar_one() > 0
